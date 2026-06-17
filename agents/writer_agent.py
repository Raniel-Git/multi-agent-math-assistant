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
        result = math_result["result"]
        formatted_result = self._format_number(result)

        if user_language == "pt":
            return f"O resultado é {formatted_result}."

        if user_language == "es":
            return f"El resultado es {formatted_result}."

        return f"The result is {formatted_result}."

    def _format_number(
        self,
        value: int | float,
    ) -> str:
        if isinstance(value, float) and value.is_integer():
            return str(int(value))

        return str(value)