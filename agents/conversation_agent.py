from typing import Any

from clients.llm_client import LLMClient


class ConversationAgent:
    """Generate natural conversational responses for non-math messages.

    Attributes:
        llm_client: Client responsible for text generation.
    """

    def __init__(
        self,
        llm_client: LLMClient | None = None,
    ) -> None:
        """Initialize the conversation agent.

        Args:
            llm_client: Client used to generate conversational responses.
        """
        self.llm_client = llm_client

    def execute(
        self,
        user_message: str,
        intent: str,
        user_language: str,
        text_math_context: dict[str, Any] | None = None,
        conversation_history: list[dict[str, Any]] | None = None,
    ) -> str:
        """Generate a conversational response for the user message.

        Args:
            user_message: Original user message.
            intent: Intent detected for the current message.
            user_language: Language detected for the user message.
            text_math_context: Optional context for messages mixing text
                and mathematical expressions.
            conversation_history: Recent messages stored in the current
                conversation session.

        Returns:
            Natural conversational response.
        """
        if self.llm_client is None:
            return self._build_default_response(
                intent=intent,
                user_language=user_language,
                text_math_context=text_math_context,
            )

        prompt = self._build_prompt(
            user_message=user_message,
            intent=intent,
            user_language=user_language,
            text_math_context=text_math_context,
            conversation_history=conversation_history,
        )

        try:
            return self.llm_client.generate_text(
                prompt=prompt,
            )
        except ValueError:
            return self._build_default_response(
                intent=intent,
                user_language=user_language,
                text_math_context=text_math_context,
            )

    def _build_prompt(
        self,
        user_message: str,
        intent: str,
        user_language: str,
        text_math_context: dict[str, Any] | None,
        conversation_history: list[dict[str, Any]] | None,
    ) -> str:
        recent_history = self._get_recent_history(
            conversation_history=conversation_history,
        )

        if user_language == "pt":
            return f"""
Você é um assistente conversacional de um chatbot matemático.

Responda em português do Brasil.
Seja natural, útil e curto.
Use o histórico recente para manter o contexto da conversa.
Use apenas informações pessoais explicitamente presentes no histórico.
Nunca invente informações sobre o usuário.
Não invente cálculos.
Se houver uma possível interpretação usando texto, explique com clareza.
Não responda assuntos fora do escopo como se fosse um assistente geral.
O escopo principal é matemática básica.

Histórico recente da conversa:
{recent_history}

Mensagem atual do usuário:
{user_message}

Intenção detectada:
{intent}

Contexto de texto misturado com matemática:
{text_math_context}

Regras:
- Use o histórico recente quando a mensagem atual depender de contexto.
- Se o usuário perguntar algo que informou anteriormente, responda usando
  apenas informações presentes no histórico.
- Se a informação solicitada não estiver no histórico, não a invente.
- Se a mensagem mistura número com palavra, explique que não é uma
  operação matemática direta.
- Se houver text_math_context, diga que uma possível interpretação é usar
  a quantidade de letras da palavra.
- Se houver possible_result, mostre a conta possível, mas deixe claro que
  é uma interpretação.
- Se for saudação, cumprimente e dê exemplos.
- Se for fora do escopo e não depender do histórico, explique
  educadamente o limite do chatbot.
- Use no máximo 4 frases.

Gere apenas a resposta final.
"""

        return f"""
You are a conversational assistant for a math chatbot.

Answer in English.
Be natural, helpful and short.
Use the recent conversation history to maintain context.
Use only personal information explicitly present in the history.
Never invent information about the user.
Do not invent calculations.
If there is a possible interpretation involving text, explain it clearly.
Do not answer out-of-scope topics as a general assistant.
The main scope is basic math.

Recent conversation history:
{recent_history}

Current user message:
{user_message}

Detected intent:
{intent}

Text mixed with math context:
{text_math_context}

Rules:
- Use the recent history when the current message depends on context.
- If the user asks about something previously provided, answer using only
  information present in the history.
- If the requested information is not present in the history, do not
  invent it.
- If the message mixes a number with a word, explain that it is not a
  direct mathematical operation.
- If text_math_context exists, say one possible interpretation is using
  the number of letters in the word.
- If possible_result exists, show the possible calculation, but make it
  clear that it is an interpretation.
- If it is a greeting, greet and provide examples.
- If it is out of scope and does not depend on conversation history,
  politely explain the chatbot limitation.
- Use at most 4 sentences.

Generate only the final response.
"""

    def _get_recent_history(
        self,
        conversation_history: list[dict[str, Any]] | None,
    ) -> list[dict[str, Any]]:
        if conversation_history is None:
            return []

        return conversation_history[-10:]

    def _build_default_response(
        self,
        intent: str,
        user_language: str,
        text_math_context: dict[str, Any] | None,
    ) -> str:
        if text_math_context is not None:
            word = text_math_context["word"]
            first_number = self._format_number(text_math_context["first_number"])
            letter_count = text_math_context["letter_count"]
            possible_result = self._format_number(text_math_context["possible_result"])

            if user_language == "pt":
                return (
                    f"Essa não é uma operação matemática direta, porque "
                    f"'{word}' é uma palavra. Uma possível interpretação "
                    f"seria usar a quantidade de letras de '{word}', que é "
                    f"{letter_count}; nesse caso, {first_number} com "
                    f"{letter_count} resultaria em {possible_result}."
                )

            return (
                f"This is not a direct math operation because '{word}' is "
                f"a word. One possible interpretation is to use the number "
                f"of letters in '{word}', which is {letter_count}; in that "
                f"case, the result would be {possible_result}."
            )

        if user_language == "pt":
            responses = {
                "greeting": (
                    "Olá! Posso ajudar com operações matemáticas básicas, "
                    "como 5 + 4 ou quanto é 10 dividido por 2."
                ),
                "out_of_scope": (
                    "Eu sou focado em operações matemáticas básicas. "
                    "Tente me enviar uma soma, subtração, multiplicação "
                    "ou divisão."
                ),
                "invalid_math": (
                    "Não consegui identificar uma operação matemática "
                    "válida. Tente usar dois números, como 2 + 4."
                ),
                "missing_context": (
                    "Preciso de um resultado anterior para continuar. "
                    "Comece com uma operação completa, como 5 + 4."
                ),
            }

            return responses.get(
                intent,
                (
                    "Não consegui entender totalmente, mas posso ajudar "
                    "com matemática básica."
                ),
            )

        responses = {
            "greeting": (
                "Hello! I can help with basic math operations, "
                "such as 5 + 4 or 10 divided by 2."
            ),
            "out_of_scope": (
                "I focus on basic math operations. Try sending an addition, "
                "subtraction, multiplication or division."
            ),
            "invalid_math": (
                "I could not identify a valid math operation. "
                "Try using two numbers, such as 2 + 4."
            ),
            "missing_context": (
                "I need a previous result to continue. "
                "Start with a complete operation, such as 5 + 4."
            ),
        }

        return responses.get(
            intent,
            "I could not fully understand, but I can help with basic math.",
        )

    def _format_number(
        self,
        value: int | float,
    ) -> str:
        if isinstance(value, float) and value.is_integer():
            return str(int(value))

        return str(value)
