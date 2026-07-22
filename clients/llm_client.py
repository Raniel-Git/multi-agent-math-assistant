from typing import Any, Protocol


class LLMClient(Protocol):
    """Defines the operations required from a language model client."""

    def generate_text(
        self,
        prompt: str,
    ) -> str:
        """Generate a text response from a prompt.

        Args:
            prompt: Prompt sent to the language model.

        Returns:
            Generated text response.
        """
        ...

    def generate_json(
        self,
        prompt: str,
    ) -> dict[str, Any]:
        """Generate a structured JSON response from a prompt.

        Args:
            prompt: Prompt sent to the language model.

        Returns:
            Structured language model response.
        """
        ...
