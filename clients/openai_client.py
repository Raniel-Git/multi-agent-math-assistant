import json
import os
import re
from typing import Any

from dotenv import load_dotenv
from openai import APIConnectionError, APIError, APITimeoutError, OpenAI


class OpenAIClient:
    """
    Client responsible for communicating with the OpenAI API.
    """

    def __init__(
        self,
        model_name: str = "gpt-4o-mini",
    ) -> None:
        """
        Initializes the OpenAI client.

        Args:
            model_name (str): OpenAI model name.
        """
        load_dotenv()

        api_key = os.getenv("OPENAI_API_KEY")

        if api_key is None:
            raise ValueError(
                "OPENAI_API_KEY environment variable is not set."
            )

        self.model_name = model_name
        self.client = OpenAI(
            api_key=api_key,
            timeout=8.0,
            max_retries=1,
        )

    def generate_text(
        self,
        prompt: str,
    ) -> str:
        """
        Sends a prompt to OpenAI and returns a text response.
        """
        try:
            response = self.client.responses.create(
                model=self.model_name,
                input=prompt,
            )

            return response.output_text.strip()

        except (
            APIConnectionError,
            APITimeoutError,
            APIError,
        ) as error:
            raise ValueError(
                "OpenAI is temporarily unavailable."
            ) from error

    def generate_json(
        self,
        prompt: str,
    ) -> dict[str, Any]:
        """
        Sends a prompt to OpenAI and parses the JSON response.
        """
        try:
            response = self.client.responses.create(
                model=self.model_name,
                input=prompt,
            )

            content = response.output_text.strip()

            return self._parse_json_response(content)

        except (
            APIConnectionError,
            APITimeoutError,
            APIError,
        ) as error:
            raise ValueError(
                "OpenAI is temporarily unavailable."
            ) from error

    def _parse_json_response(
        self,
        content: str,
    ) -> dict[str, Any]:
        """
        Parses a JSON object from an OpenAI response.
        """
        try:
            return self._normalize_response(
                json.loads(content)
            )
        except json.JSONDecodeError:
            json_match = re.search(
                r"\{.*\}",
                content,
                re.DOTALL,
            )

            if json_match is None:
                raise ValueError(
                    "OpenAI returned an invalid JSON response."
                )

            return self._normalize_response(
                json.loads(json_match.group(0))
            )

    def _normalize_response(
        self,
        response: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Normalizes missing keys in the model response.
        """
        return {
            "intent": response.get("intent"),
            "operation": response.get("operation"),
            "first_number": response.get("first_number"),
            "second_number": response.get("second_number"),
            "language": response.get("language"),
        }