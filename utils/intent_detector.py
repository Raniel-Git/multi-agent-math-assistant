import re


class IntentDetector:
    """
    Detects the intent behind a user message.
    """

    def detect(self, message: str) -> str:
        """
        Detects the user message intent.

        Args:
            message (str): User message.

        Returns:
            str: Detected intent.
        """
        normalized_message = message.lower().strip()

        if not normalized_message:
            return "empty"

        if self._is_greeting(normalized_message):
            return "greeting"

        if self._looks_like_math(normalized_message):
            return "math_operation"

        if self._looks_like_random_text(normalized_message):
            return "unclear"

        return "out_of_scope"

    def _is_greeting(self, message: str) -> bool:
        """
        Checks whether the message is a greeting.

        Args:
            message (str): Normalized user message.

        Returns:
            bool: True if message is a greeting.
        """
        greetings = {
            "hi",
            "hello",
            "hey",
            "oi",
            "ola",
            "olá",
            "bom dia",
            "boa tarde",
            "boa noite",
            "tudo bem",
        }

        return message in greetings

    def _looks_like_math(self, message: str) -> bool:
        """
        Checks whether the message looks like a math request.

        Args:
            message (str): Normalized user message.

        Returns:
            bool: True if message looks like math.
        """
        math_symbols = re.search(r"\d+\s*[\+\-\*\/]\s*\d+", message)

        math_keywords = [
            "add",
            "sum",
            "plus",
            "subtract",
            "minus",
            "multiply",
            "times",
            "divide",
            "calcule",
            "calcular",
            "quanto",
            "soma",
            "somar",
            "some",
            "mais",
            "subtrair",
            "menos",
            "tirar",
            "remove",
            "remover",
            "multiplicar",
            "vezes",
            "dividir",
            "dividido",
            "resultado",
        ]

        if math_symbols:
            return True

        return any(keyword in message for keyword in math_keywords)

    def _looks_like_random_text(self, message: str) -> bool:
        """
        Checks whether the message looks like random text.

        Args:
            message (str): Normalized user message.

        Returns:
            bool: True if message seems random.
        """
        has_no_space = " " not in message
        has_no_digit = not any(char.isdigit() for char in message)
        has_many_consonants = bool(
            re.search(r"[bcdfghjklmnpqrstvwxyz]{5,}", message)
        )

        return has_no_space and has_no_digit and has_many_consonants