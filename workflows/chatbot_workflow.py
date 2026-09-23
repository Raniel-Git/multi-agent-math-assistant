import re
from typing import Any

from agents.conversation_agent import ConversationAgent
from agents.intent_agent import IntentAgent
from memory.session_memory import SessionMemory
from orchestration.orchestrator import ChatbotOrchestrator
from tools.expression_tools import ExpressionTool
from tools.text_tools import extract_text_math_context
from utils.language_detector import LanguageDetector
from utils.math_parser import MathParser
from utils.parser_exceptions import (
    AmbiguousMathRequestError,
    InvalidMathExpressionError,
    MissingContextError,
    UnsupportedMathRequestError,
)


class ChatbotWorkflow:
    """Coordinates the complete chatbot message processing workflow."""

    def __init__(
        self,
        memory: SessionMemory,
        orchestrator: ChatbotOrchestrator,
        conversation_agent: ConversationAgent,
        intent_agent: IntentAgent,
        expression_tool: ExpressionTool,
        parser: MathParser,
        language_detector: LanguageDetector,
    ) -> None:
        self.memory = memory
        self.orchestrator = orchestrator
        self.conversation_agent = conversation_agent
        self.intent_agent = intent_agent
        self.expression_tool = expression_tool
        self.parser = parser
        self.language_detector = language_detector

    def process_message(self, message: str) -> str:
        user_language = self.language_detector.detect(message)

        self.memory.add_message(
            role="user",
            content=message,
        )

        if self._is_division_by_zero_request(message):
            response = self._build_division_by_zero_response(
                user_language=user_language,
            )

            self._store_assistant_message(response)

            return response

        try:
            expression_response = self._process_expression(
                message=message,
                user_language=user_language,
            )

            if expression_response is not None:
                return expression_response

            parser_response = self._process_local_parser(
                message=message,
                user_language=user_language,
            )

            if parser_response is not None:
                return parser_response

            return self._process_intent(
                message=message,
                user_language=user_language,
            )

        except (
            AmbiguousMathRequestError,
            InvalidMathExpressionError,
            MissingContextError,
            UnsupportedMathRequestError,
            ValueError,
        ) as error:
            response = self._build_error_response(
                error=error,
                user_language=user_language,
            )

            self._store_assistant_message(response)

            return response

    def get_messages(self) -> list[dict[str, Any]]:
        return self.memory.get_messages()

    def get_last_result(self) -> float | None:
        return self.memory.get_last_result()

    def clear_memory(self) -> None:
        self.memory.clear()

    def _process_expression(
        self,
        message: str,
        user_language: str,
    ) -> str | None:
        expression = self.expression_tool.extract_expression(message)

        if expression is None:
            return None

        try:
            result = self.expression_tool.evaluate(expression)
        except ValueError as error:
            error_message = str(error)

            if (
                "Division by zero" in error_message
                or "zero" in error_message
            ):
                response = self._build_division_by_zero_response(
                    user_language=user_language,
                )

                self._store_assistant_message(response)

                return response

            return None

        self.memory.set_last_result(result=result)

        response = self._build_expression_response(
            result=result,
            user_language=user_language,
        )

        self._store_assistant_message(response)

        return response

    def _process_local_parser(
        self,
        message: str,
        user_language: str,
    ) -> str | None:
        try:
            parsed_request = self.parser.parse(
                message=message,
                last_result=self.memory.get_last_result(),
            )

            result = self.orchestrator.handle_math_request(
                operation=parsed_request["operation"],
                first_number=parsed_request["first_number"],
                second_number=parsed_request["second_number"],
                user_language=user_language,
            )

            return str(result["final_response"])

        except (
            InvalidMathExpressionError,
            MissingContextError,
            UnsupportedMathRequestError,
            ValueError,
        ):
            return None

    def _process_intent(
        self,
        message: str,
        user_language: str,
    ) -> str:
        try:
            intent_result = self.intent_agent.interpret(
                message=message,
                last_result=self.memory.get_last_result(),
            )
        except ValueError:
            return self._process_conversation(
                message=message,
                intent="unclear",
                user_language=user_language,
            )

        resolved_language = intent_result.get(
            "language",
            user_language,
        )

        intent = intent_result.get(
            "intent",
            "unclear",
        )

        if intent != "math_operation":
            return self._process_conversation(
                message=message,
                intent=intent,
                user_language=resolved_language,
            )

        parsed_request = self._build_parsed_request_from_intent(
            intent_result=intent_result,
        )

        if (
            parsed_request["operation"] is None
            or parsed_request["first_number"] is None
            or parsed_request["second_number"] is None
        ):
            return self._process_conversation(
                message=message,
                intent="invalid_math",
                user_language=resolved_language,
            )

        result = self.orchestrator.handle_math_request(
            operation=parsed_request["operation"],
            first_number=parsed_request["first_number"],
            second_number=parsed_request["second_number"],
            user_language=resolved_language,
        )

        return str(result["final_response"])

    def _process_conversation(
        self,
        message: str,
        intent: str,
        user_language: str,
    ) -> str:
        text_math_context = extract_text_math_context(message)

        try:
            response = self.conversation_agent.execute(
                user_message=message,
                intent=intent,
                user_language=user_language,
                text_math_context=text_math_context,
            )
        except ValueError:
            response = self._build_fallback_response(
                intent=intent,
                user_language=user_language,
            )

        self._store_assistant_message(response)

        return response

    def _store_assistant_message(self, response: str) -> None:
        self.memory.add_message(
            role="assistant",
            content=response,
        )

    def _build_expression_response(
        self,
        result: float,
        user_language: str,
    ) -> str:
        formatted_result = self._format_number(result)

        if user_language == "pt":
            return f"O resultado é {formatted_result}."

        if user_language == "es":
            return f"El resultado es {formatted_result}."

        return f"The result is {formatted_result}."

    def _build_division_by_zero_response(
        self,
        user_language: str,
    ) -> str:
        if user_language == "pt":
            return (
                "Não é possível dividir por zero. "
                "Essa operação é inválida matematicamente."
            )

        if user_language == "es":
            return (
                "No es posible dividir por cero. "
                "Esa operación no es válida matemáticamente."
            )

        return (
            "Division by zero is not allowed. "
            "That operation is mathematically invalid."
        )

    def _build_fallback_response(
        self,
        intent: str,
        user_language: str,
    ) -> str:
        if user_language == "pt":
            responses = {
                "empty": (
                    "Digite uma operação matemática para começarmos."
                ),
                "greeting": (
                    "Olá! Eu posso ajudar com operações matemáticas "
                    "básicas. Tente algo como: 5 + 4."
                ),
                "unclear": (
                    "Não consegui entender sua mensagem. "
                    "Tente escrever uma operação como: 10 - 3."
                ),
                "invalid_math": (
                    "Não consegui identificar uma operação matemática "
                    "válida. Use apenas números e uma operação, "
                    "como: 2 + 4."
                ),
                "missing_context": (
                    "Preciso de um resultado anterior para continuar. "
                    "Comece com uma operação completa, como: 5 + 4."
                ),
                "out_of_scope": (
                    "Eu só consigo ajudar com operações matemáticas "
                    "básicas: soma, subtração, multiplicação e divisão."
                ),
            }

            return responses.get(
                intent,
                "Não consegui processar essa solicitação.",
            )

        if user_language == "es":
            responses = {
                "empty": (
                    "Escribe una operación matemática para empezar."
                ),
                "greeting": (
                    "¡Hola! Puedo ayudar con operaciones matemáticas "
                    "básicas. Prueba algo como: 5 + 4."
                ),
                "unclear": (
                    "No pude entender tu mensaje. "
                    "Intenta escribir una operación como: 10 - 3."
                ),
                "invalid_math": (
                    "No pude identificar una operación matemática "
                    "válida. Usa solo números y una operación, "
                    "como: 2 + 4."
                ),
                "missing_context": (
                    "Necesito un resultado anterior para continuar. "
                    "Empieza con una operación completa, como: 5 + 4."
                ),
                "out_of_scope": (
                    "Solo puedo ayudar con operaciones matemáticas "
                    "básicas: suma, resta, multiplicación y división."
                ),
            }

            return responses.get(
                intent,
                "No pude procesar esa solicitud.",
            )

        responses = {
            "empty": "Type a mathematical operation to start.",
            "greeting": (
                "Hello! I can help with basic mathematical operations. "
                "Try something like: 5 + 4."
            ),
            "unclear": (
                "I could not understand your message. "
                "Try writing an operation like: 10 - 3."
            ),
            "invalid_math": (
                "I could not identify a valid mathematical operation. "
                "Use only numbers and one operation, such as: 2 + 4."
            ),
            "missing_context": (
                "I need a previous result to continue. "
                "Start with a complete operation, such as: 5 + 4."
            ),
            "out_of_scope": (
                "I can only help with basic mathematical operations: "
                "addition, subtraction, multiplication and division."
            ),
        }

        return responses.get(
            intent,
            "I could not process this request.",
        )

    def _build_error_response(
        self,
        error: Exception,
        user_language: str,
    ) -> str:
        error_message = str(error)

        if (
            "Division by zero" in error_message
            or "zero" in error_message
        ):
            return self._build_division_by_zero_response(
                user_language=user_language,
            )

        if isinstance(error, InvalidMathExpressionError):
            return self._build_fallback_response(
                intent="invalid_math",
                user_language=user_language,
            )

        if isinstance(error, AmbiguousMathRequestError):
            if user_language == "pt":
                return (
                    "Sua solicitação está incompleta. "
                    "Informe a operação matemática desejada."
                )

            if user_language == "es":
                return (
                    "Tu solicitud está incompleta. "
                    "Indica la operación matemática deseada."
                )

            return (
                "Your request is incomplete. "
                "Please specify the mathematical operation."
            )

        if isinstance(error, MissingContextError):
            return self._build_fallback_response(
                intent="missing_context",
                user_language=user_language,
            )

        if isinstance(error, UnsupportedMathRequestError):
            return self._build_fallback_response(
                intent="out_of_scope",
                user_language=user_language,
            )

        return str(error)

    def _build_parsed_request_from_intent(
        self,
        intent_result: dict[str, Any],
    ) -> dict[str, Any]:
        return {
            "operation": intent_result["operation"],
            "first_number": intent_result["first_number"],
            "second_number": intent_result["second_number"],
        }

    def _is_division_by_zero_request(
        self,
        message: str,
    ) -> bool:
        normalized_message = message.lower().strip()
        normalized_message = normalized_message.replace("÷", "/")

        direct_patterns = [
            r"/\s*0\b",
            r"dividido\s+por\s+0\b",
            r"dividir\s+por\s+0\b",
            r"divide\s+by\s+0\b",
            r"divided\s+by\s+0\b",
            r"dividido\s+por\s+zero\b",
            r"dividir\s+por\s+zero\b",
            r"divide\s+by\s+zero\b",
            r"divided\s+by\s+zero\b",
            r"dividido\s+entre\s+0\b",
            r"dividir\s+entre\s+0\b",
        ]

        return any(
            re.search(pattern, normalized_message)
            for pattern in direct_patterns
        )

    def _format_number(
        self,
        value: int | float,
    ) -> str:
        if isinstance(value, float) and value.is_integer():
            return str(int(value))

        return str(value)