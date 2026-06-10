from typing import Any

from tools.math_tools import add, divide, multiply, subtract


class MathematicalAgent:
    """
    Agent responsible for executing mathematical operations
    through dedicated tools.
    """

    def execute(
        self,
        operation: str,
        first_number: float,
        second_number: float,
    ) -> dict[str, Any]:
        """
        Executes a mathematical operation using the
        appropriate tool.

        Args:
            operation (str):
                Operation name.
            first_number (float):
                First operand.
            second_number (float):
                Second operand.

        Returns:
            dict[str, Any]:
                Structured operation result.

        Raises:
            ValueError:
                If operation is not supported.
        """

        operations = {
            "add": add,
            "subtract": subtract,
            "multiply": multiply,
            "divide": divide,
        }

        tool = operations.get(operation)

        if tool is None:
            raise ValueError(
                f"Unsupported operation: {operation}"
            )

        result = tool(
            first_number,
            second_number,
        )

        return {
            "operation": operation,
            "first_number": first_number,
            "second_number": second_number,
            "result": result,
        }