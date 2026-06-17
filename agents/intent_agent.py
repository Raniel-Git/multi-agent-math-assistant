from typing import Any

from clients.ollama_client import OllamaClient
from utils.language_detector import LanguageDetector
from utils.math_parser import MathParser
from utils.parser_exceptions import (
    InvalidMathExpressionError,
    MissingContextError,
    UnsupportedMathRequestError,
)


class IntentAgent:
    """
    Agent responsible for interpreting user messages using an LLM.
    """

    VALID_OPERATIONS = {
        "add",
        "subtract",
        "multiply",
        "divide",
    }

    FOLLOW_UP_TERMS = {
        "isso",
        "resultado",
        "ultimo",
        "último",
        "valor anterior",
        "esse valor",
        "ele",
        "it",
        "this",
        "that",
        "result",
        "last result",
        "previous result",
    }

    def __init__(
        self,
        ollama_client: OllamaClient,
    ) -> None:
        """
        Initializes the intent agent.

        Args:
            ollama_client (OllamaClient): Ollama client dependency.
        """
        self.ollama_client = ollama_client
        self.language_detector = LanguageDetector()
        self.math_parser = MathParser()

    def interpret(
        self,
        message: str,
        last_result: float | None = None,
    ) -> dict[str, Any]:
        """
        Interprets a user message and returns structured intent data.

        Args:
            message (str): User message.
            last_result (float | None): Last mathematical result.

        Returns:
            dict[str, Any]: Structured intent data.
        """
        prompt = self._build_prompt(
            message=message,
            last_result=last_result,
        )

        result = self.ollama_client.generate_json(
            prompt=prompt,
        )

        result["language"] = self.language_detector.detect(
            message
        )

        result = self._sanitize_llm_result(
            result=result,
        )

        return self._normalize_intent_result(
            result=result,
            message=message,
            last_result=last_result,
        )

    def _sanitize_llm_result(
        self,
        result: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Sanitizes raw LLM output.

        Args:
            result (dict[str, Any]): Raw LLM result.

        Returns:
            dict[str, Any]: Sanitized result.
        """
        operation = result.get("operation")

        if operation not in self.VALID_OPERATIONS:
            operation = None

        return {
            "intent": result.get("intent"),
            "operation": operation,
            "first_number": self._to_number_or_none(
                result.get("first_number")
            ),
            "second_number": self._to_number_or_none(
                result.get("second_number")
            ),
            "language": result.get("language"),
        }

    def _normalize_intent_result(
        self,
        result: dict[str, Any],
        message: str,
        last_result: float | None,
    ) -> dict[str, Any]:
        """
        Normalizes and corrects LLM intent output.

        Args:
            result (dict[str, Any]): Raw LLM result.
            message (str): User message.
            last_result (float | None): Last mathematical result.

        Returns:
            dict[str, Any]: Normalized intent result.
        """
        language = result.get("language") or self.language_detector.detect(
            message
        )

        if self._is_follow_up_reference(message):
            return self._normalize_follow_up_result(
                result=result,
                message=message,
                last_result=last_result,
                language=language,
            )

        try:
            parsed_request = self.math_parser.parse(
                message=message,
                last_result=last_result,
            )

            return {
                "intent": "math_operation",
                "operation": parsed_request["operation"],
                "first_number": parsed_request["first_number"],
                "second_number": parsed_request["second_number"],
                "language": language,
            }

        except MissingContextError:
            return {
                "intent": "missing_context",
                "operation": result.get("operation"),
                "first_number": None,
                "second_number": result.get("second_number"),
                "language": language,
            }

        except InvalidMathExpressionError:
            return {
                "intent": "invalid_math",
                "operation": result.get("operation"),
                "first_number": result.get("first_number"),
                "second_number": result.get("second_number"),
                "language": language,
            }

        except UnsupportedMathRequestError:
            return {
                "intent": result.get("intent") or "out_of_scope",
                "operation": result.get("operation"),
                "first_number": result.get("first_number"),
                "second_number": result.get("second_number"),
                "language": language,
            }

    def _normalize_follow_up_result(
        self,
        result: dict[str, Any],
        message: str,
        last_result: float | None,
        language: str,
    ) -> dict[str, Any]:
        """
        Normalizes follow-up operation results.

        Args:
            result (dict[str, Any]): Raw LLM result.
            message (str): User message.
            last_result (float | None): Last mathematical result.
            language (str): User language.

        Returns:
            dict[str, Any]: Normalized follow-up result.
        """
        if last_result is None:
            return {
                "intent": "missing_context",
                "operation": result.get("operation"),
                "first_number": None,
                "second_number": result.get("second_number")
                or self._extract_fallback_number(message),
                "language": language,
            }

        try:
            parsed_request = self.math_parser.parse(
                message=message,
                last_result=last_result,
            )

            return {
                "intent": "math_operation",
                "operation": parsed_request["operation"],
                "first_number": parsed_request["first_number"],
                "second_number": parsed_request["second_number"],
                "language": language,
            }

        except (
            InvalidMathExpressionError,
            MissingContextError,
            UnsupportedMathRequestError,
        ):
            second_number = result.get("second_number")

            if second_number is None:
                second_number = self._extract_fallback_number(
                    message
                )

            return {
                "intent": "math_operation",
                "operation": result.get("operation"),
                "first_number": last_result,
                "second_number": second_number,
                "language": language,
            }

    def _is_follow_up_reference(
        self,
        message: str,
    ) -> bool:
        """
        Checks whether a message references previous context.

        Args:
            message (str): User message.

        Returns:
            bool: True if message references previous context.
        """
        normalized_message = message.lower()

        return any(
            term in normalized_message
            for term in self.FOLLOW_UP_TERMS
        )

    def _extract_fallback_number(
        self,
        message: str,
    ) -> float | None:
        """
        Extracts a fallback number from natural language.

        Args:
            message (str): User message.

        Returns:
            float | None: Extracted number or None.
        """
        normalized_message = message.lower()

        number_words = {
            "zero": 0,
            "um": 1,
            "uma": 1,
            "dois": 2,
            "duas": 2,
            "tres": 3,
            "três": 3,
            "quatro": 4,
            "cinco": 5,
            "seis": 6,
            "sete": 7,
            "oito": 8,
            "nove": 9,
            "dez": 10,
            "one": 1,
            "two": 2,
            "three": 3,
            "four": 4,
            "five": 5,
            "six": 6,
            "seven": 7,
            "eight": 8,
            "nine": 9,
            "ten": 10,
        }

        for word, value in number_words.items():
            if word in normalized_message:
                return float(value)

        return None

    def _to_number_or_none(
        self,
        value: Any,
    ) -> float | None:
        """
        Converts a value to float or None.

        Args:
            value (Any): Raw value.

        Returns:
            float | None: Parsed number or None.
        """
        if value is None:
            return None

        if isinstance(value, (int, float)):
            return float(value)

        if isinstance(value, str):
            try:
                return float(value)
            except ValueError:
                return None

        return None

    def _build_prompt(
        self,
        message: str,
        last_result: float | None,
    ) -> str:
        """
        Builds the LLM prompt.

        Args:
            message (str): User message.
            last_result (float | None): Last mathematical result.

        Returns:
            str: Prompt text.
        """
        return f"""
You are an intent extraction agent for a math chatbot.

Your only responsibility is to convert the user's message into structured JSON.

Do NOT calculate the final answer.
Do NOT explain.
Do NOT use markdown.
Return ONLY valid JSON.

Supported operations:
- add
- subtract
- multiply
- divide

Supported intents:
- math_operation
- invalid_math
- out_of_scope
- greeting
- unclear
- missing_context

Output JSON format:
{{"intent":"math_operation | invalid_math | out_of_scope | greeting | unclear | missing_context","operation":"add | subtract | multiply | divide | null","first_number":number | null,"second_number":number | null,"language":"pt | en"}}

Rules:
- If the user asks a valid math operation with two numbers, return math_operation.
- If the user asks a valid follow-up operation and Previous result is not null, use Previous result as first_number.
- If the user asks a follow-up operation and Previous result is null, return missing_context.
- Portuguese follow-up references include: "isso", "resultado", "ultimo resultado", "valor anterior", "esse valor", "ele".
- English follow-up references include: "it", "this", "that", "result", "last result", "previous result".
- If one operand is invalid text, return invalid_math.
- If one number is missing and it is not a valid follow-up, return invalid_math.
- If the user asks something unrelated to math, return out_of_scope.
- If the user greets, return greeting.
- Always detect the user language as "pt" or "en".
- Null values must be valid JSON null, not string "null".

Previous result:
{last_result}

User:
{message}

Response:
"""