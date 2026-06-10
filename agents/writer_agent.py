from typing import Any


class WriterAgent:
    """
    Agent responsible for transforming structured calculation
    results into user-friendly responses.
    """

    def execute(
        self,
        math_result: dict[str, Any],
        user_language: str = "en",
    ) -> str:
        """
        Builds a readable response from a mathematical result.

        Args:
            math_result (dict[str, Any]): Structured result produced
                by the Mathematical Agent.
            user_language (str): Language used to generate the response.

        Returns:
            str: User-friendly response.
        """
        result = math_result["result"]
        formatted_result = self._format_number(result)

        if user_language == "pt":
            return f"O resultado é {formatted_result}."

        return f"The result is {formatted_result}."

    def _format_number(
        self,
        value: int | float,
    ) -> str:
        """
        Formats a number for user-friendly display.

        Args:
            value (int | float): Number to format.

        Returns:
            str: Formatted number.
        """
        if isinstance(value, float) and value.is_integer():
            return str(int(value))

        return str(value)