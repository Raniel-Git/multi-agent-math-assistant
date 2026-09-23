import os
import re

import streamlit as st
from dotenv import load_dotenv

from agents.conversation_agent import ConversationAgent
from agents.intent_agent import IntentAgent
from agents.mathematical_agent import MathematicalAgent
from agents.writer_agent import WriterAgent
from clients.ollama_client import OllamaClient
from clients.openai_client import OpenAIClient
from memory.session_memory import SessionMemory
from orchestration.orchestrator import ChatbotOrchestrator
from tools.expression_tools import ExpressionTool
from tools.text_tools import extract_text_math_context
from utils.intent_detector import IntentDetector
from utils.language_detector import LanguageDetector
from utils.math_parser import MathParser
from utils.math_validator import MathValidator
from utils.parser_exceptions import (
    AmbiguousMathRequestError,
    InvalidMathExpressionError,
    MissingContextError,
    UnsupportedMathRequestError,
)

load_dotenv()

st.set_page_config(
    page_title="Multi-Agent Chatbot",
    page_icon="📊",
    layout="wide",
)

st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #111827 100%);
    }

    h1 {
        color: #f8fafc;
        font-weight: 800;
    }

    .stMarkdown {
        color: #e5e7eb;
    }

    section[data-testid="stSidebar"] {
        background-color: #020617;
        border-right: 1px solid #1e293b;
    }

    div[data-testid="stChatMessage"] {
        border-radius: 16px;
        padding: 12px;
        border: 1px solid #334155;
        background-color: #111827;
    }

    div[data-testid="stChatInput"] {
        border-radius: 16px;
    }

    .stButton > button {
        border-radius: 12px;
        background-color: #2563eb;
        color: white;
        border: none;
        font-weight: 600;
    }

    .stButton > button:hover {
        background-color: #1d4ed8;
        color: white;
    }

    div[data-testid="stMetric"] {
        background-color: #0f172a;
        border: 1px solid #334155;
        padding: 14px;
        border-radius: 14px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

col1, col2 = st.columns([4, 1])

with col1:
    st.markdown(
        """
        # 📊 Multi-Agent Math Assistant

        ## 🧑🏻‍💻 Developer: Raniel Andrade

        Assistente inteligente com:

        - Ferramentas matemáticas
        - Memória contextual
        - OpenAI/Ollama
        - Conversação natural
        """
    )

with col2:
    st.write("")
    st.write("")
    st.link_button(
        "🔗 LinkedIn",
        "https://www.linkedin.com/in/raniel-andrade-25a9ba2bb",
    )


def build_llm_client():
    provider = os.getenv(
        "LLM_PROVIDER",
        "ollama",
    ).lower()

    if provider == "openai":
        return OpenAIClient()

    return OllamaClient()


def format_number(
    value: int | float,
) -> str:
    if isinstance(value, float) and value.is_integer():
        return str(int(value))

    return str(value)


def build_expression_response(
    result: float,
    user_language: str,
) -> str:
    formatted_result = format_number(result)

    if user_language == "pt":
        return f"O resultado é {formatted_result}."

    if user_language == "es":
        return f"El resultado es {formatted_result}."

    return f"The result is {formatted_result}."


def build_division_by_zero_response(
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


def is_division_by_zero_request(
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


def build_fallback_response(
    intent: str,
    user_language: str,
) -> str:
    if user_language == "pt":
        responses = {
            "empty": "Digite uma operação matemática para começarmos.",
            "greeting": (
                "Olá! Eu posso ajudar com operações matemáticas básicas. "
                "Tente algo como: 5 + 4."
            ),
            "unclear": (
                "Não consegui entender sua mensagem. "
                "Tente escrever uma operação como: 10 - 3."
            ),
            "invalid_math": (
                "Não consegui identificar uma operação matemática válida. "
                "Use apenas números e uma operação, como: 2 + 4."
            ),
            "missing_context": (
                "Preciso de um resultado anterior para continuar. "
                "Comece com uma operação completa, como: 5 + 4."
            ),
            "out_of_scope": (
                "Eu só consigo ajudar com operações matemáticas básicas: "
                "soma, subtração, multiplicação e divisão."
            ),
        }

        return responses.get(
            intent,
            "Não consegui processar essa solicitação.",
        )

    if user_language == "es":
        responses = {
            "empty": "Escribe una operación matemática para empezar.",
            "greeting": (
                "¡Hola! Puedo ayudar con operaciones matemáticas básicas. "
                "Prueba algo como: 5 + 4."
            ),
            "unclear": (
                "No pude entender tu mensaje. "
                "Intenta escribir una operación como: 10 - 3."
            ),
            "invalid_math": (
                "No pude identificar una operación matemática válida. "
                "Usa solo números y una operación, como: 2 + 4."
            ),
            "missing_context": (
                "Necesito un resultado anterior para continuar. "
                "Empieza con una operación completa, como: 5 + 4."
            ),
            "out_of_scope": (
                "Solo puedo ayudar con operaciones matemáticas básicas: "
                "suma, resta, multiplicación y división."
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


def build_error_response(
    error: Exception,
    user_language: str,
) -> str:
    error_message = str(error)

    if "Division by zero" in error_message or "zero" in error_message:
        return build_division_by_zero_response(
            user_language
        )

    if isinstance(error, InvalidMathExpressionError):
        return build_fallback_response(
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
        return build_fallback_response(
            intent="missing_context",
            user_language=user_language,
        )

    if isinstance(error, UnsupportedMathRequestError):
        return build_fallback_response(
            intent="out_of_scope",
            user_language=user_language,
        )

    return str(error)


def build_parsed_request_from_intent(
    intent_result: dict,
) -> dict:
    return {
        "operation": intent_result["operation"],
        "first_number": intent_result["first_number"],
        "second_number": intent_result["second_number"],
    }


def handle_expression_response(
    user_message: str,
    user_language: str,
) -> bool:
    expression = st.session_state.expression_tool.extract_expression(
        user_message
    )

    if expression is None:
        return False

    try:
        result = st.session_state.expression_tool.evaluate(
            expression
        )
    except ValueError as error:
        error_message = str(error)

        if (
            "Division by zero" in error_message
            or "zero" in error_message
        ):
            response = build_division_by_zero_response(
                user_language
            )

            st.session_state.memory.add_message(
                role="assistant",
                content=response,
            )

            st.rerun()

        return False

    st.session_state.memory.set_last_result(
        result=result,
    )

    response = build_expression_response(
        result=result,
        user_language=user_language,
    )

    st.session_state.memory.add_message(
        role="assistant",
        content=response,
    )

    st.rerun()

    return True


def handle_local_parser_response(
    user_message: str,
    user_language: str,
) -> bool:
    try:
        parsed_request = st.session_state.parser.parse(
            message=user_message,
            last_result=st.session_state.memory.get_last_result(),
        )

        st.session_state.orchestrator.handle_math_request(
            operation=parsed_request["operation"],
            first_number=parsed_request["first_number"],
            second_number=parsed_request["second_number"],
            user_language=user_language,
        )

        st.rerun()

        return True

    except (
        InvalidMathExpressionError,
        MissingContextError,
        UnsupportedMathRequestError,
        ValueError,
    ):
        return False


def handle_conversation_response(
    user_message: str,
    intent: str,
    user_language: str,
) -> None:
    text_math_context = extract_text_math_context(
        user_message
    )

    try:
        with st.spinner("💬 Gerando resposta..."):
            conversation_response = (
                st.session_state.conversation_agent.execute(
                    user_message=user_message,
                    intent=intent,
                    user_language=user_language,
                    text_math_context=text_math_context,
                )
            )
    except ValueError:
        conversation_response = build_fallback_response(
            intent=intent,
            user_language=user_language,
        )

    st.session_state.memory.add_message(
        role="assistant",
        content=conversation_response,
    )

    st.rerun()


if "llm_client" not in st.session_state:
    st.session_state.llm_client = build_llm_client()

if "memory" not in st.session_state:
    st.session_state.memory = SessionMemory()

if "orchestrator" not in st.session_state:
    st.session_state.orchestrator = ChatbotOrchestrator(
        mathematical_agent=MathematicalAgent(),
        writer_agent=WriterAgent(),
        memory=st.session_state.memory,
    )

if "conversation_agent" not in st.session_state:
    st.session_state.conversation_agent = ConversationAgent(
        llm_client=st.session_state.llm_client,
    )

if "expression_tool" not in st.session_state:
    st.session_state.expression_tool = ExpressionTool()

if "parser" not in st.session_state:
    st.session_state.parser = MathParser()

if "math_validator" not in st.session_state:
    st.session_state.math_validator = MathValidator()

if "language_detector" not in st.session_state:
    st.session_state.language_detector = LanguageDetector()

if "intent_detector" not in st.session_state:
    st.session_state.intent_detector = IntentDetector()

if "intent_agent" not in st.session_state:
    st.session_state.intent_agent = IntentAgent(
        llm_client=st.session_state.llm_client,
    )

if not st.session_state.memory.get_messages():
    st.info(
        """
        👋 Bem-vindo ao Multi-Agent Math Assistant

        Exemplos que você pode testar:

        • Quanto é 5 + 4?

        • Agora multiplica isso por 3

        • Quanto é raiz quadrada de 81?

        • Tenho 3 caixas com 10 itens cada e perdi 5

        • Quanto é 50% de 200?

        • Quanto é (5 + 3) * 2?
        """
    )
with st.sidebar:
    st.title("⚙️ Configurações")

    provider = os.getenv(
        "LLM_PROVIDER",
        "ollama",
    ).upper()

    st.success(
        f"Modelo: {provider}"
    )

    st.metric(
        "Mensagens",
        len(
            st.session_state.memory.get_messages()
        ),
    )

    last_result = (
        st.session_state.memory.get_last_result()
    )

    st.metric(
        "Último Resultado",
        (
            str(last_result)
            if last_result is not None
            else "-"
        ),
    )

    st.markdown("---")

    st.markdown(
        """
        ### 🏗️ Arquitetura

        Usuário
            ↓
        Intent Agent
            ↓
        Expression Tool
            ↓
        Mathematical Agent
            ↓
        Writer Agent
            ↓
        Session Memory
        """
    )

    st.markdown("---")

    if st.button(
        "🗑️ Limpar Conversa"
    ):
        st.session_state.memory = SessionMemory()
        st.rerun()

for message in st.session_state.memory.get_messages():
    with st.chat_message(message["role"]):
        st.write(message["content"])
        
user_message = st.chat_input(
    "Enter a mathematical operation..."
)

if user_message:
    user_language = st.session_state.language_detector.detect(
        user_message
    )

    st.session_state.memory.add_message(
        role="user",
        content=user_message,
    )

    if is_division_by_zero_request(
        user_message
    ):
        response = build_division_by_zero_response(
            user_language
        )

        st.session_state.memory.add_message(
            role="assistant",
            content=response,
        )

        st.rerun()

    try:
        if handle_expression_response(
            user_message=user_message,
            user_language=user_language,
        ):
            st.stop()

        if handle_local_parser_response(
            user_message=user_message,
            user_language=user_language,
        ):
            st.stop()

        try:
            with st.spinner("🧠 Interpretando sua solicitação..."):
                intent_result = st.session_state.intent_agent.interpret(
                    message=user_message,
                    last_result=st.session_state.memory.get_last_result(),
                )
        except ValueError:
            handle_conversation_response(
                user_message=user_message,
                intent="unclear",
                user_language=user_language,
            )

        user_language = intent_result.get(
            "language",
            user_language,
        )

        intent = intent_result.get(
            "intent",
            "unclear",
        )

        if intent != "math_operation":
            handle_conversation_response(
                user_message=user_message,
                intent=intent,
                user_language=user_language,
            )

        parsed_request = build_parsed_request_from_intent(
            intent_result
        )

        if (
            parsed_request["operation"] is None
            or parsed_request["first_number"] is None
            or parsed_request["second_number"] is None
        ):
            handle_conversation_response(
                user_message=user_message,
                intent="invalid_math",
                user_language=user_language,
            )

        st.session_state.orchestrator.handle_math_request(
            operation=parsed_request["operation"],
            first_number=parsed_request["first_number"],
            second_number=parsed_request["second_number"],
            user_language=user_language,
        )

        st.rerun()

    except (
        AmbiguousMathRequestError,
        InvalidMathExpressionError,
        MissingContextError,
        UnsupportedMathRequestError,
        ValueError,
    ) as error:
        error_response = build_error_response(
            error=error,
            user_language=user_language,
        )

        st.session_state.memory.add_message(
            role="assistant",
            content=error_response,
        )

        st.rerun()