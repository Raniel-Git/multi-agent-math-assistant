import streamlit as st

from agents.mathematical_agent import MathematicalAgent
from agents.writer_agent import WriterAgent
from memory.session_memory import SessionMemory
from orchestration.orchestrator import ChatbotOrchestrator
from utils.language_detector import LanguageDetector
from utils.math_parser import MathParser

st.set_page_config(
    page_title="Multi-Agent Chatbot",
    page_icon="🤖",
)

st.title("🤖 Multi-Agent Chatbot")

if "memory" not in st.session_state:
    st.session_state.memory = SessionMemory()

if "orchestrator" not in st.session_state:
    st.session_state.orchestrator = ChatbotOrchestrator(
        mathematical_agent=MathematicalAgent(),
        writer_agent=WriterAgent(),
        memory=st.session_state.memory,
    )

if "parser" not in st.session_state:
    st.session_state.parser = MathParser()

if "language_detector" not in st.session_state:
    st.session_state.language_detector = LanguageDetector()

for message in st.session_state.memory.get_messages():
    with st.chat_message(message["role"]):
        st.write(message["content"])

user_message = st.chat_input(
    "Enter a mathematical operation..."
)

if user_message:
    try:
        parsed_request = st.session_state.parser.parse(
            message=user_message,
            last_result=st.session_state.memory.get_last_result(),
        )

        user_language = st.session_state.language_detector.detect(
            user_message
        )

        st.session_state.orchestrator.handle_math_request(
            operation=parsed_request["operation"],
            first_number=parsed_request["first_number"],
            second_number=parsed_request["second_number"],
            user_message=user_message,
            user_language=user_language,
        )

        st.rerun()

    except ValueError as error:
        st.error(str(error))