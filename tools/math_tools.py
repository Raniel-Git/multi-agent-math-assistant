from typing import Union


Number = Union[int, float]


def add(a: Number, b: Number) -> Number:
    """
    Returns the sum of two numbers.

    Args:
        a (Number): First number.
        b (Number): Second number.

    Returns:
        Number: Sum of the provided numbers.
    """
    return a + b


def subtract(a: Number, b: Number) -> Number:
    """
    Returns the subtraction of two numbers.

    Args:
        a (Number): First number.
        b (Number): Second number.

    Returns:
        Number: Result of the subtraction.
    """
    return a - b


def multiply(a: Number, b: Number) -> Number:
    """
    Returns the multiplication of two numbers.

    Args:
        a (Number): First number.
        b (Number): Second number.

    Returns:
        Number: Result of the multiplication.
    """
    return a * b


def divide(a: Number, b: Number) -> Number:
    """
    Returns the division of two numbers.

    Args:
        a (Number): Dividend.
        b (Number): Divisor.

    Returns:
        Number: Result of the division.

    Raises:
        ValueError: If divisor is zero.
    """
    if b == 0:
        raise ValueError("Division by zero is not allowed.")

    return a / b