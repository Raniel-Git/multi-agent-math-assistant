import pytest

from tools.math_tools import add, divide, multiply, subtract


def test_add() -> None:
    assert add(5, 4) == 9


def test_subtract() -> None:
    assert subtract(10, 3) == 7


def test_multiply() -> None:
    assert multiply(7, 8) == 56


def test_divide() -> None:
    assert divide(20, 5) == 4


def test_divide_by_zero() -> None:
    with pytest.raises(ValueError, match="Division by zero is not allowed."):
        divide(10, 0)