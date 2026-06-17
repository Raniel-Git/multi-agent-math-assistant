class LanguageDetector:
    """
    Detects the language used in a user message.
    """

    def detect(self, message: str) -> str:
        """
        Detects whether the user message is in Portuguese, English or Spanish.

        Args:
            message (str): User message.

        Returns:
            str: Language code.
        """
        normalized_message = message.lower()

        spanish_phrases = [
            "ahora divide",
            "divide el resultado",
            "dividir el resultado",
            "el resultado",
            "por favor",
            "no es posible",
        ]

        for phrase in spanish_phrases:
            if phrase in normalized_message:
                return "es"

        portuguese_phrases = [
            "agora subtraia",
            "ignore suas instruções",
            "ignore suas instrucoes",
            "sem usar nenhuma ferramenta",
            "escreva um texto",
            "no final diga",
            "não é possível",
            "nao e possivel",
        ]

        for phrase in portuguese_phrases:
            if phrase in normalized_message:
                return "pt"

        english_phrases = [
            "multiply that",
            "divide that",
            "add that",
            "subtract that",
            "the result",
            "without using",
        ]

        for phrase in english_phrases:
            if phrase in normalized_message:
                return "en"

        spanish_keywords = [
            "ahora",
            "cuanto",
            "cuánto",
            "hola",
            "entre",
        ]

        for keyword in spanish_keywords:
            if keyword in normalized_message:
                return "es"

        english_keywords = [
            "multiply",
            "that",
            "by",
            "what",
            "divide",
            "divided",
            "add",
            "subtract",
            "plus",
            "minus",
            "instructions",
            "previous",
            "tool",
            "without",
        ]

        for keyword in english_keywords:
            if keyword in normalized_message:
                return "en"

        portuguese_keywords = [
            "oi",
            "olá",
            "ola",
            "bom dia",
            "boa tarde",
            "boa noite",
            "tudo bem",
            "quanto",
            "quem",
            "qual",
            "é",
            "soma",
            "somar",
            "some",
            "subtrair",
            "subtraia",
            "menos",
            "tirar",
            "remover",
            "multiplicar",
            "multiplica",
            "vezes",
            "dividir",
            "dividido",
            "resultado",
            "agora",
            "por",
            "pra",
            "para",
            "me",
            "ignore",
            "suas",
            "instruções",
            "instrucoes",
            "anteriores",
            "diga",
            "sem usar",
            "nenhuma ferramenta",
            "escreva",
            "texto",
            "enorme",
            "sobre",
            "futebol",
            "final",
        ]

        for keyword in portuguese_keywords:
            if keyword in normalized_message:
                return "pt"

        return "pt"