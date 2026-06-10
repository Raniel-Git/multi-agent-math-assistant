class LanguageDetector:
    """
    Detects the language used in a user message.
    """

    def detect(self, message: str) -> str:
        """
        Detects whether the user message is in Portuguese or English.

        Args:
            message (str): User message.

        Returns:
            str: Language code.
        """
        normalized_message = message.lower()

        portuguese_keywords = [
            "quanto",
            "soma",
            "somar",
            "subtrair",
            "menos",
            "multiplicar",
            "vezes",
            "dividir",
            "resultado",
            "agora",
            "por",
        ]

        for keyword in portuguese_keywords:
            if keyword in normalized_message:
                return "pt"

        return "en"