import re
from typing import Any


class MathParser:
    """
    Parses user messages into structured mathematical requests.
    """

    def parse(
        self,
        message: str,
        last_result: float | None = None,
    ) -> dict[str, Any]:
        """
        Parses a user message and extracts a mathematical operation.

        Args:
            message (str): User message.
            last_result (float | None): Last stored mathematical result.

        Returns:
            dict[str, Any]: Parsed mathematical request.

        Raises:
            ValueError: If no supported mathematical operation is found.
        """
        normalized_message = message.lower().strip()

        direct_operation = self._parse_direct_operation(
            normalized_message
        )

        if direct_operation is not None:
            return direct_operation

        follow_up_operation = self._parse_follow_up_operation(
            normalized_message=normalized_message,
            last_result=last_result,
        )

        if follow_up_operation is not None:
            return follow_up_operation

        raise ValueError("No supported mathematical operation was found.")

    def _parse_direct_operation(
        self,
        message: str,
    ) -> dict[str, Any] | None:
        """
        Parses direct operations containing two explicit numbers.

        Args:
            message (str): Normalized user message.

        Returns:
            dict[str, Any] | None: Parsed operation or None.
        """
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

    def _parse_follow_up_operation(
        self,
        normalized_message: str,
        last_result: float | None,
    ) -> dict[str, Any] | None:
        """
        Parses follow-up operations using the previous result.

        Args:
            normalized_message (str): Normalized user message.
            last_result (float | None): Last stored mathematical result.

        Returns:
            dict[str, Any] | None: Parsed operation or None.
        """
        if last_result is None:
            return None

        pattern = (
            r"(add|sum|plus|soma|somar|subtract|minus|subtrair|"
            r"menos|multiply|times|multiplicar|vezes|divide|dividir)"
            r"\s*(?:by|por)?\s*(-?\d+(?:\.\d+)?)"
        )
        match = re.search(pattern, normalized_message)

        if match is None:
            return None

        keyword = match.group(1)
        second_number = float(match.group(2))

        keyword_operator_map = {
            "add": "+",
            "sum": "+",
            "plus": "+",
            "soma": "+",
            "somar": "+",
            "subtract": "-",
            "minus": "-",
            "subtrair": "-",
            "menos": "-",
            "multiply": "*",
            "times": "*",
            "multiplicar": "*",
            "vezes": "*",
            "divide": "/",
            "dividir": "/",
        }

        return self._build_operation(
            first_number=last_result,
            operator=keyword_operator_map[keyword],
            second_number=second_number,
        )

    def _build_operation(
        self,
        first_number: float,
        operator: str,
        second_number: float,
    ) -> dict[str, Any]:
        """
        Builds a structured mathematical operation.

        Args:
            first_number (float): First operand.
            operator (str): Mathematical operator.
            second_number (float): Second operand.

        Returns:
            dict[str, Any]: Structured mathematical operation.
        """
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