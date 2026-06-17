import re
import unicodedata
from typing import Any

from utils.parser_exceptions import (
    InvalidMathExpressionError,
    MissingContextError,
    UnsupportedMathRequestError,
)


class MathParser:
    """
    Parses natural language user messages into structured mathematical requests.
    """

    def parse(
        self,
        message: str,
        last_result: float | None = None,
    ) -> dict[str, Any]:
        normalized_message = self._normalize_message(message)

        symbol_operation = self._parse_symbol_operation(
            normalized_message
        )

        if symbol_operation is not None:
            return symbol_operation

        follow_up_operation = self._parse_follow_up_operation(
            normalized_message=normalized_message,
            last_result=last_result,
        )

        if follow_up_operation is not None:
            return follow_up_operation

        natural_operation = self._parse_natural_operation(
            normalized_message
        )

        if natural_operation is not None:
            return natural_operation

        if self._looks_like_follow_up(normalized_message):
            raise MissingContextError(
                "Previous result is required for this operation."
            )

        if self._has_math_signal(normalized_message):
            raise InvalidMathExpressionError(
                "Invalid mathematical expression."
            )

        raise UnsupportedMathRequestError(
            "No supported mathematical operation was found."
        )

    def _normalize_message(self, message: str) -> str:
        normalized = message.lower().strip()
        normalized = unicodedata.normalize("NFKD", normalized)
        normalized = "".join(
            char for char in normalized if not unicodedata.combining(char)
        )
        normalized = normalized.replace(",", ".")
        normalized = re.sub(r"[?!;:]", " ", normalized)
        normalized = re.sub(r"\s+", " ", normalized)

        return normalized

    def _parse_symbol_operation(
        self,
        message: str,
    ) -> dict[str, Any] | None:
        pattern = (
            r"(-?\d+(?:\.\d+)?)\s*([\+\-\*\/])\s*"
            r"(-?\d+(?:\.\d+)?)"
        )
        match = re.search(pattern, message)

        if match is None:
            return None

        return self._build_operation(
            first_number=float(match.group(1)),
            operator=match.group(2),
            second_number=float(match.group(3)),
        )

    def _parse_natural_operation(
        self,
        message: str,
    ) -> dict[str, Any] | None:
        numbers = self._extract_numbers(message)

        if len(numbers) < 2:
            return None

        operator = self._detect_operator(message)

        if operator is None:
            return None

        return self._build_operation(
            first_number=numbers[0],
            operator=operator,
            second_number=numbers[1],
        )

    def _parse_follow_up_operation(
        self,
        normalized_message: str,
        last_result: float | None,
    ) -> dict[str, Any] | None:
        if last_result is None:
            return None

        numbers = self._extract_numbers(normalized_message)

        if not numbers:
            return None

        operator = self._detect_operator(normalized_message)

        if operator is None:
            return None

        return self._build_operation(
            first_number=last_result,
            operator=operator,
            second_number=numbers[0],
        )

    def _extract_numbers(self, message: str) -> list[float]:
        converted_message = self._replace_number_words(message)
        matches = re.findall(r"-?\d+(?:\.\d+)?", converted_message)

        return [float(match) for match in matches]

    def _replace_number_words(self, message: str) -> str:
        number_words = {
            "zero": "0",
            "one": "1",
            "two": "2",
            "three": "3",
            "four": "4",
            "five": "5",
            "six": "6",
            "seven": "7",
            "eight": "8",
            "nine": "9",
            "ten": "10",
            "um": "1",
            "uma": "1",
            "dois": "2",
            "duas": "2",
            "tres": "3",
            "três": "3",
            "quatro": "4",
            "cinco": "5",
            "seis": "6",
            "sete": "7",
            "oito": "8",
            "nove": "9",
            "dez": "10",
            "vinte": "20",
            "uno": "1",
            "dos": "2",
            "tres": "3",
            "cuatro": "4",
            "cinco": "5",
            "seis": "6",
            "siete": "7",
            "ocho": "8",
            "nueve": "9",
            "diez": "10",
        }

        words = message.split()

        return " ".join(number_words.get(word, word) for word in words)

    def _detect_operator(self, message: str) -> str | None:
        operation_keywords = {
            "+": [
                "add",
                "sum",
                "plus",
                "increase",
                "somar",
                "soma",
                "some",
                "mais",
                "adicionar",
                "acrescentar",
                "juntar",
                "sumar",
                "mas",
                "más",
            ],
            "-": [
                "subtract",
                "subtracted",
                "minus",
                "decrease",
                "remove",
                "subtrair",
                "subtraia",
                "menos",
                "tirar",
                "remover",
                "diminuir",
                "descontar",
                "restar",
                "resta",
            ],
            "*": [
                "multiply",
                "times",
                "multiplied",
                "multiplicar",
                "multiplica",
                "vezes",
                "dobrar",
                "triplicar",
                "multiplicado",
            ],
            "/": [
                "divide",
                "divided",
                "division",
                "dividir",
                "divide",
                "dividido",
                "entre",
            ],
        }

        for operator, keywords in operation_keywords.items():
            for keyword in keywords:
                if re.search(rf"\b{keyword}\b", message):
                    return operator

        return None

    def _has_math_signal(self, message: str) -> bool:
        math_signals = [
            "+",
            "-",
            "*",
            "/",
            "mais",
            "menos",
            "vezes",
            "dividir",
            "dividido",
            "soma",
            "somar",
            "subtrair",
            "subtraia",
            "multiplicar",
            "multiplica",
            "quanto",
            "calcule",
            "calcular",
            "add",
            "plus",
            "minus",
            "subtract",
            "multiply",
            "divide",
            "ahora",
            "resultado",
        ]

        return any(signal in message for signal in math_signals)

    def _looks_like_follow_up(self, message: str) -> bool:
        follow_up_signals = [
            "agora",
            "resultado",
            "ultimo",
            "último",
            "isso",
            "esse",
            "ele",
            "that",
            "it",
            "previous",
            "last",
            "from the result",
            "ahora",
        ]

        return any(signal in message for signal in follow_up_signals)

    def _build_operation(
        self,
        first_number: float,
        operator: str,
        second_number: float,
    ) -> dict[str, Any]:
        operation_map = {
            "+": "add",
            "-": "subtract",
            "*": "multiply",
            "/": "divide",
        }

        return {
            "operation": operation_map[operator],
            "first_number": first_number,
            "second_number": second_number,
        }