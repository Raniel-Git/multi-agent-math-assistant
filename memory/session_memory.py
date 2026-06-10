from typing import Any


class SessionMemory:
    """
    Stores conversation history and contextual information
    during the current session.
    """

    def __init__(self) -> None:
        """
        Initializes session memory.
        """
        self.messages: list[dict[str, Any]] = []
        self.last_result: float | None = None

    def add_message(
        self,
        role: str,
        content: str,
    ) -> None:
        """
        Stores a message in memory.

        Args:
            role (str): Message author role.
            content (str): Message content.
        """
        self.messages.append(
            {
                "role": role,
                "content": content,
            }
        )

    def get_messages(self) -> list[dict[str, Any]]:
        """
        Returns all stored messages.

        Returns:
            list[dict[str, Any]]: Conversation history.
        """
        return self.messages

    def set_last_result(
        self,
        result: float,
    ) -> None:
        """
        Stores the last mathematical result.

        Args:
            result (float): Mathematical result.
        """
        self.last_result = result

    def get_last_result(self) -> float | None:
        """
        Returns the last stored mathematical result.

        Returns:
            float | None: Last mathematical result.
        """
        return self.last_result