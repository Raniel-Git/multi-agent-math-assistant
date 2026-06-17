import ast
import math
import operator
import re
import unicodedata


class ExpressionTool:
    """
    Tool responsible for safely evaluating mathematical expressions.
    """

    ALLOWED_OPERATORS = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.Pow: operator.pow,
        ast.USub: operator.neg,
        ast.UAdd: operator.pos,
    }

    ALLOWED_FUNCTIONS = {
        "sqrt": math.sqrt,
        "sin": math.sin,
        "cos": math.cos,
        "tan": math.tan,
        "log": math.log,
        "log10": math.log10,
        "abs": abs,
        "round": round,
    }

    ALLOWED_CONSTANTS = {
        "pi": math.pi,
        "e": math.e,
    }

    NUMBER_WORDS_PT = {
        "zero": 0,
        "um": 1,
        "uma": 1,
        "dois": 2,
        "duas": 2,
        "tres": 3,
        "três": 3,
        "quatro": 4,
        "cinco": 5,
        "seis": 6,
        "sete": 7,
        "oito": 8,
        "nove": 9,
        "dez": 10,
        "onze": 11,
        "doze": 12,
        "treze": 13,
        "quatorze": 14,
        "catorze": 14,
        "quinze": 15,
        "dezesseis": 16,
        "dezessete": 17,
        "dezoito": 18,
        "dezenove": 19,
        "vinte": 20,
        "trinta": 30,
        "quarenta": 40,
        "cinquenta": 50,
        "sessenta": 60,
        "setenta": 70,
        "oitenta": 80,
        "noventa": 90,
        "cem": 100,
        "cento": 100,
        "duzentos": 200,
        "trezentos": 300,
        "quatrocentos": 400,
        "quinhentos": 500,
        "seiscentos": 600,
        "setecentos": 700,
        "oitocentos": 800,
        "novecentos": 900,
    }

    NUMBER_WORDS_EN = {
        "zero": 0,
        "one": 1,
        "two": 2,
        "three": 3,
        "four": 4,
        "five": 5,
        "six": 6,
        "seven": 7,
        "eight": 8,
        "nine": 9,
        "ten": 10,
        "eleven": 11,
        "twelve": 12,
        "thirteen": 13,
        "fourteen": 14,
        "fifteen": 15,
        "sixteen": 16,
        "seventeen": 17,
        "eighteen": 18,
        "nineteen": 19,
        "twenty": 20,
        "thirty": 30,
        "forty": 40,
        "fifty": 50,
        "sixty": 60,
        "seventy": 70,
        "eighty": 80,
        "ninety": 90,
        "hundred": 100,
    }

    SCALE_WORDS = {
        "mil": 1000,
        "thousand": 1000,
        "milhao": 1000000,
        "milhoes": 1000000,
        "million": 1000000,
        "millions": 1000000,
    }

    def extract_expression(
        self,
        message: str,
    ) -> str | None:
        normalized_message = self._normalize_message(message)

        natural_expression = self._extract_natural_business_expression(
            normalized_message
        )

        if natural_expression is not None:
            return natural_expression

        expression = self._convert_natural_language_to_expression(
            normalized_message
        )

        expression = self._remove_prompt_injection_text(expression)
        expression = self._remove_common_math_words(expression)
        expression = self._keep_expression_characters(expression)

        if not expression:
            return None

        if not self._has_valid_expression_shape(expression):
            return None

        try:
            self._validate_expression(expression)
        except Exception:
            return None

        return expression

    def evaluate(
        self,
        expression: str,
    ) -> float:
        parsed_expression = ast.parse(
            expression,
            mode="eval",
        )

        return self._evaluate_node(
            parsed_expression.body,
        )

    def _evaluate_node(
        self,
        node: ast.AST,
    ) -> float:
        if isinstance(node, ast.Constant):
            if isinstance(node.value, (int, float)):
                return float(node.value)

            raise ValueError("Invalid expression value.")

        if isinstance(node, ast.Name):
            if node.id in self.ALLOWED_CONSTANTS:
                return float(self.ALLOWED_CONSTANTS[node.id])

            raise ValueError("Unsupported constant.")

        if isinstance(node, ast.BinOp):
            operator_type = type(node.op)

            if operator_type not in self.ALLOWED_OPERATORS:
                raise ValueError("Unsupported operator.")

            left_value = self._evaluate_node(node.left)
            right_value = self._evaluate_node(node.right)

            if operator_type is ast.Div and right_value == 0:
                raise ValueError("Division by zero is not allowed.")

            return float(
                self.ALLOWED_OPERATORS[operator_type](
                    left_value,
                    right_value,
                )
            )

        if isinstance(node, ast.UnaryOp):
            operator_type = type(node.op)

            if operator_type not in self.ALLOWED_OPERATORS:
                raise ValueError("Unsupported unary operator.")

            operand_value = self._evaluate_node(node.operand)

            return float(
                self.ALLOWED_OPERATORS[operator_type](
                    operand_value,
                )
            )

        if isinstance(node, ast.Call):
            if not isinstance(node.func, ast.Name):
                raise ValueError("Unsupported function call.")

            function_name = node.func.id

            if function_name not in self.ALLOWED_FUNCTIONS:
                raise ValueError("Unsupported function.")

            arguments = [
                self._evaluate_node(argument)
                for argument in node.args
            ]

            return float(
                self.ALLOWED_FUNCTIONS[function_name](
                    *arguments
                )
            )

        raise ValueError("Unsupported expression.")

    def _normalize_message(
        self,
        message: str,
    ) -> str:
        normalized = message.lower().strip()
        normalized = unicodedata.normalize(
            "NFKD",
            normalized,
        )
        normalized = "".join(
            char for char in normalized
            if not unicodedata.combining(char)
        )
        normalized = normalized.replace(",", ".")
        normalized = normalized.replace("?", " ")
        normalized = normalized.replace("=", " ")
        normalized = normalized.replace("-", " ")

        return normalized

    def _extract_natural_business_expression(
        self,
        message: str,
    ) -> str | None:
        numbers = self._extract_numbers_from_text(message)

        if (
            "caixa" in message
            and "cada" in message
            and ("perdi" in message or "perdeu" in message)
            and len(numbers) >= 3
        ):
            return f"{numbers[0]}*{numbers[1]}-{numbers[2]}"

        return None

    def _extract_numbers_from_text(
        self,
        message: str,
    ) -> list[str]:
        converted_message = self._replace_number_words(message)

        return re.findall(
            r"\d+(?:\.\d+)?",
            converted_message,
        )

    def _replace_number_words(
        self,
        message: str,
    ) -> str:
        tokens = message.split()
        result_tokens: list[str] = []
        index = 0

        while index < len(tokens):
            parsed_number, next_index = self._parse_number_phrase(
                tokens=tokens,
                start_index=index,
            )

            if parsed_number is not None:
                result_tokens.append(str(parsed_number))
                index = next_index
            else:
                result_tokens.append(tokens[index])
                index += 1

        return " ".join(result_tokens)

    def _parse_number_phrase(
        self,
        tokens: list[str],
        start_index: int,
    ) -> tuple[int | None, int]:
        total = 0
        current = 0
        index = start_index
        consumed = False

        while index < len(tokens):
            token = tokens[index]

            if token == "e" or token == "and":
                index += 1
                continue

            if token in self.NUMBER_WORDS_PT:
                current += self.NUMBER_WORDS_PT[token]
                consumed = True
                index += 1
                continue

            if token in self.NUMBER_WORDS_EN:
                value = self.NUMBER_WORDS_EN[token]

                if value == 100:
                    current = max(current, 1) * value
                else:
                    current += value

                consumed = True
                index += 1
                continue

            if token in self.SCALE_WORDS:
                scale = self.SCALE_WORDS[token]

                if current == 0:
                    current = 1

                total += current * scale
                current = 0
                consumed = True
                index += 1
                continue

            break

        if not consumed:
            return None, start_index

        return total + current, index

    def _convert_natural_language_to_expression(
        self,
        message: str,
    ) -> str:
        expression = self._replace_number_words(message)

        expression = re.sub(
            r"raiz quadrada de\s*(-?\d+(?:\.\d+)?)",
            r"sqrt(\1)",
            expression,
        )
        expression = re.sub(
            r"raiz de\s*(-?\d+(?:\.\d+)?)",
            r"sqrt(\1)",
            expression,
        )

        replacements = {
            " vezes ": " * ",
            " multiplicado por ": " * ",
            " dividido por ": " / ",
            " dividido ": " / ",
            " dividir por ": " / ",
            " dividir ": " / ",
            " mais ": " + ",
            " menos ": " - ",
            " plus ": " + ",
            " minus ": " - ",
            " times ": " * ",
            " multiplied by ": " * ",
            " divided by ": " / ",
            " divide by ": " / ",
        }

        for old_value, new_value in replacements.items():
            expression = expression.replace(
                old_value,
                new_value,
            )

        expression = expression.replace("^", "**")
        expression = expression.replace(" elevado a ", " ** ")

        expression = re.sub(
            r"(\d+(?:\.\d+)?)\s+ao quadrado",
            r"\1 ** 2",
            expression,
        )
        expression = re.sub(
            r"(\d+(?:\.\d+)?)\s+ao cubo",
            r"\1 ** 3",
            expression,
        )

        return expression

    def _remove_prompt_injection_text(
        self,
        message: str,
    ) -> str:
        if ":" in message:
            return message.split(":")[-1]

        return message

    def _remove_common_math_words(
        self,
        message: str,
    ) -> str:
        words_to_remove = [
            "quanto",
            "qual",
            "e",
            "a",
            "o",
            "os",
            "as",
            "calcule",
            "calcular",
            "calcula",
            "passo",
            "por",
            "resultado",
            "da",
            "de",
            "do",
            "das",
            "dos",
            "operacao",
            "operação",
            "conta",
            "valor",
            "total",
            "isso",
            "aqui",
            "mano",
            "kkkkk",
            "kkkk",
        ]

        cleaned_message = message

        for word in words_to_remove:
            cleaned_message = re.sub(
                rf"\b{word}\b",
                "",
                cleaned_message,
            )

        return cleaned_message

    def _keep_expression_characters(
        self,
        message: str,
    ) -> str:
        expression = re.sub(
            r"[^0-9+\-*/().\sa-zA-Z]",
            "",
            message,
        )

        expression = re.sub(
            r"\s+",
            "",
            expression,
        )

        return expression.strip()

    def _has_valid_expression_shape(
        self,
        expression: str,
    ) -> bool:
        has_function = any(
            f"{function_name}(" in expression
            for function_name in self.ALLOWED_FUNCTIONS
        )

        has_operator = bool(
            re.search(
                r"[+\-*/]",
                expression,
            )
        )

        numbers = re.findall(
            r"\d+(?:\.\d+)?",
            expression,
        )

        return (has_operator or has_function) and len(numbers) >= 2

    def _validate_expression(
        self,
        expression: str,
    ) -> None:
        ast.parse(
            expression,
            mode="eval",
        )