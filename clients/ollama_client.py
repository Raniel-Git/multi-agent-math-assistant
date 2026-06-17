import json
import re
from typing import Any

import ollama


class OllamaClient:
    """
    Client responsible for communicating with a local Ollama model.
    """

    def __init__(
        self,
        model_name: str = "llama3.2:3b",
    ) -> None:
        """
        Initializes the Ollama client.

        Args:
            model_name (str): Ollama model name.
        """
        self.model_name = model_name

    def generate_text(
        self,
        prompt: str,
    ) -> str:
        """
        Sends a prompt to Ollama and returns a text response.

        Args:
            prompt (str): Prompt sent to the model.

        Returns:
            str: Generated text response.
        """
        response = ollama.generate(
            model=self.model_name,
            prompt=prompt,
        )

        return response["response"].strip()

    def generate_json(
        self,
        prompt: str,
    ) -> dict[str, Any]:
        """
        Sends a prompt to Ollama and parses the JSON response.

        Args:
            prompt (str): Prompt sent to the model.

        Returns:
            dict[str, Any]: Parsed JSON response.

        Raises:
            ValueError: If the model response is not valid JSON.
        """
        response = ollama.generate(
            model=self.model_name,
            prompt=prompt,
            format="json",
        )

        content = response["response"]

        return self._parse_json_response(content)

    def _parse_json_response(
        self,
        content: str,
    ) -> dict[str, Any]:
        """
        Parses a JSON object from an Ollama response.

        Args:
            content (str): Raw model response.

        Returns:
            dict[str, Any]: Parsed JSON object.

        Raises:
            ValueError: If no valid JSON object is found.
        """
        cleaned_content = content.strip()

        try:
            parsed_response = json.loads(cleaned_content)
            return self._normalize_response(parsed_response)
        except json.JSONDecodeError:
            json_match = re.search(
                r"\{.*\}",
                cleaned_content,
                re.DOTALL,
            )

            if json_match is None:
                raise ValueError(
                    "Ollama returned an invalid JSON response."
                )

            try:
                parsed_response = json.loads(json_match.group(0))
                return self._normalize_response(parsed_response)
            except json.JSONDecodeError as error:
                raise ValueError(
                    "Ollama returned an invalid JSON response."
                ) from error

    def _normalize_response(
        self,
        response: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Normalizes missing keys in the model response.

        Args:
            response (dict[str, Any]): Parsed model response.

        Returns:
            dict[str, Any]: Normalized response.
        """
        return {
            "intent": response.get("intent"),
            "operation": response.get("operation"),
            "first_number": response.get("first_number"),
            "second_number": response.get("second_number"),
            "language": response.get("language"),
        }