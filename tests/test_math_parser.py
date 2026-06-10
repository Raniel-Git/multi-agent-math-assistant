import pytest

from utils.math_parser import MathParser


def test_parse_addition_operation() -> None:
    parser = MathParser()

    result = parser.parse("5 + 4")

    assert result == {
        "operation": "add",
        "first_number": 5.0,
        "second_number": 4.0,
    }


def test_parse_subtraction_operation() -> None:
    parser = MathParser()

    result = parser.parse("10 - 3")

    assert result == {
        "operation": "subtract",
        "first_number": 10.0,
        "second_number": 3.0,
    }


def test_parse_multiplication_operation() -> None:
    parser = MathParser()

    result = parser.parse("8 * 5")

    assert result == {
        "operation": "multiply",
        "first_number": 8.0,
        "second_number": 5.0,
    }


def test_parse_division_operation() -> None:
    parser = MathParser()

    result = parser.parse("20 / 4")

    assert result == {
        "operation": "divide",
        "first_number": 20.0,
        "second_number": 4.0,
    }


def test_parse_follow_up_subtraction_operation() -> None:
    parser = MathParser()

    result = parser.parse(
        message="subtract 2",
        last_result=9,
    )

    assert result == {
        "operation": "subtract",
        "first_number": 9,
        "second_number": 2.0,
    }


def test_parse_follow_up_portuguese_multiplication_operation() -> None:
    parser = MathParser()

    result = parser.parse(
        message="multiplicar por 3",
        last_result=7,
    )

    assert result == {
        "operation": "multiply",
        "first_number": 7,
        "second_number": 3.0,
    }


def test_parse_follow_up_without_last_result_raises_value_error() -> None:
    parser = MathParser()

    with pytest.raises(
        ValueError,
        match="No supported mathematical operation was found.",
    ):
        parser.parse("subtract 2")


def test_parse_invalid_message_raises_value_error() -> None:
    parser = MathParser()

    with pytest.raises(
        ValueError,
        match="No supported mathematical operation was found.",
    ):
        parser.parse("Who is Neymar?")