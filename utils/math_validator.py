import re

from utils.parser_exceptions import (
    AmbiguousMathRequestError,
    InvalidMathExpressionError,
)


class MathValidator:
    """
    Validates mathematical user inputs before parsing.

    This class is responsible for identifying malformed
    mathematical expressions, ambiguous requests, and
    unsupported inputs that could generate parser errors.
    """

    def validate(
        self,
        message: str,
    ) -> None:
        """
        Validates a user mathematical request.

        Args:
            message (str): User message.

        Raises:
            AmbiguousMathRequestError:
                If the request is too vague.

            InvalidMathExpressionError:
                If the expression appears malformed.
        """
        normalized_message = message.lower().strip()

        self._validate_empty_message(
            normalized_message
        )

        self._validate_ambiguous_message(
            normalized_message
        )

        self._validate_invalid_operators(
            normalized_message
        )

        self._validate_invalid_symbol_usage(
            normalized_message
        )

        self._validate_text_mixed_with_math(
            normalized_message
        )

    def _validate_empty_message(
        self,
        message: str,
    ) -> None:
        """
        Validates empty messages.

        Args:
            message (str): User message.

        Raises:
            AmbiguousMathRequestError:
                If message is empty.
        """
        if not message:
            raise AmbiguousMathRequestError(
                "Empty mathematical request."
            )

    def _validate_ambiguous_message(
        self,
        message: str,
    ) -> None:
        """
        Validates vague requests.

        Args:
            message (str): User message.

        Raises:
            AmbiguousMathRequestError:
                If request lacks enough information.
        """
        ambiguous_phrases = [
            "calcula",
            "calcule",
            "faz a conta",
            "faz isso",
            "resolve",
            "me ajuda",
            "agora multiplica",
            "agora divide",
            "agora soma",
            "agora subtrai",
        ]

        if message in ambiguous_phrases:
            raise AmbiguousMathRequestError(
                "Mathematical request is ambiguous."
            )

    def _validate_invalid_operators(
        self,
        message: str,
    ) -> None:
        """
        Detects malformed operators.

        Args:
            message (str): User message.

        Raises:
            InvalidMathExpressionError:
                If invalid operators are found.
        """
        invalid_patterns = [
            r"\+\+",
            r"--",
            r"\*\*",
            r"//",
            r"\+\-",
            r"\-\+",
        ]

        for pattern in invalid_patterns:
            if re.search(pattern, message):
                raise InvalidMathExpressionError(
                    "Invalid mathematical operator sequence."
                )

    def _validate_invalid_symbol_usage(
        self,
        message: str,
    ) -> None:
        """
        Detects unsupported symbols.

        Args:
            message (str): User message.

        Raises:
            InvalidMathExpressionError:
                If unsupported symbols are found.
        """
        unsupported_symbols = [
            "@",
            "#",
            "$",
            "%",
            "&",
            "=",
        ]

        if any(
            symbol in message
            for symbol in unsupported_symbols
        ):
            raise InvalidMathExpressionError(
                "Unsupported mathematical symbols."
            )

    def _validate_text_mixed_with_math(
        self,
        message: str,
    ) -> None:
        """
        Detects mixed mathematical and unrelated text.

        Examples:
            2 + batata
            soma casa com 5

        Args:
            message (str): User message.

        Raises:
            InvalidMathExpressionError:
                If unrelated text appears in a math expression.
        """
        contains_number = bool(
            re.search(r"\d", message)
        )

        contains_operator = any(
            operator in message
            for operator in [
                "+",
                "-",
                "*",
                "/",
                "mais",
                "menos",
                "soma",
                "somar",
                "multiplicar",
                "dividir",
            ]
        )

        if not (
            contains_number
            and contains_operator
        ):
            return

        allowed_words = {
            "mais",
            "menos",
            "soma",
            "somar",
            "some",
            "multiplicar",
            "vezes",
            "dividir",
            "por",
            "com",
            "add",
            "plus",
            "subtract",
            "minus",
            "multiply",
            "divide",
            "what",
            "is",
            "quanto",
            "e",
            "é",
        }

        words = re.findall(
            r"[a-zA-ZÀ-ÿ]+",
            message,
        )

        for word in words:
            if word.lower() in allowed_words:
                continue

            raise InvalidMathExpressionError(
                "Unrelated text detected in mathematical expression."
            )