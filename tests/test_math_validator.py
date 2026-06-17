import pytest

from utils.math_validator import MathValidator
from utils.parser_exceptions import (
    AmbiguousMathRequestError,
    InvalidMathExpressionError,
)


def test_validate_valid_expression() -> None:
    validator = MathValidator()

    validator.validate("5 + 4")


def test_validate_invalid_operator_sequence() -> None:
    validator = MathValidator()

    with pytest.raises(
        InvalidMathExpressionError
    ):
        validator.validate("5 ++ 4")


def test_validate_invalid_symbol() -> None:
    validator = MathValidator()

    with pytest.raises(
        InvalidMathExpressionError
    ):
        validator.validate("5 + @")


def test_validate_text_mixed_with_math() -> None:
    validator = MathValidator()

    with pytest.raises(
        InvalidMathExpressionError
    ):
        validator.validate(
            "2 + batata"
        )


def test_validate_ambiguous_message() -> None:
    validator = MathValidator()

    with pytest.raises(
        AmbiguousMathRequestError
    ):
        validator.validate(
            "faz a conta"
        )


def test_validate_empty_message() -> None:
    validator = MathValidator()

    with pytest.raises(
        AmbiguousMathRequestError
    ):
        validator.validate("")