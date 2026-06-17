import re
import unicodedata
from typing import Any


def count_letters(text: str) -> int:
    """
    Counts alphabetic letters in a text.

    Args:
        text (str): Text to count letters from.

    Returns:
        int: Number of alphabetic letters.
    """
    return len(
        re.findall(
            r"[a-zA-ZÀ-ÿ]",
            text,
        )
    )


def extract_text_math_context(
    message: str,
) -> dict[str, Any] | None:
    """
    Extracts a possible math interpretation when the user mixes
    numbers and words.

    Example:
        "quanto é 2 + batata?"

    Returns:
        dict[str, Any] | None: Suggested interpretation or None.
    """
    normalized_message = _normalize_message(message)

    pattern = (
        r"(-?\d+(?:\.\d+)?)\s*"
        r"(\+|\-|\*|\/|mais|menos|vezes|dividido|dividir)"
        r"\s*([a-zA-ZÀ-ÿ]+)"
    )

    match = re.search(
        pattern,
        normalized_message,
    )

    if match is None:
        return None

    first_number = float(match.group(1))
    operator = match.group(2)
    word = match.group(3)
    letter_count = count_letters(word)

    operation = _map_operator(operator)
    possible_result = _calculate_possible_result(
        first_number=first_number,
        operation=operation,
        second_number=letter_count,
    )

    return {
        "first_number": first_number,
        "operation": operation,
        "word": word,
        "letter_count": letter_count,
        "possible_result": possible_result,
    }


def _normalize_message(
    message: str,
) -> str:
    normalized = message.lower().strip()
    normalized = unicodedata.normalize(
        "NFKD",
        normalized,
    )
    normalized = "".join(
        char for char in normalized
        if not unicodedata.combining(char)
    )
    normalized = normalized.replace(
        "?",
        "",
    )

    return normalized


def _map_operator(
    operator: str,
) -> str:
    operation_map = {
        "+": "add",
        "mais": "add",
        "-": "subtract",
        "menos": "subtract",
        "*": "multiply",
        "vezes": "multiply",
        "/": "divide",
        "dividido": "divide",
        "dividir": "divide",
    }

    return operation_map[operator]


def _calculate_possible_result(
    first_number: float,
    operation: str,
    second_number: int,
) -> float:
    if operation == "add":
        return first_number + second_number

    if operation == "subtract":
        return first_number - second_number

    if operation == "multiply":
        return first_number * second_number

    if operation == "divide":
        return first_number / second_number

    raise ValueError("Unsupported text math operation.")