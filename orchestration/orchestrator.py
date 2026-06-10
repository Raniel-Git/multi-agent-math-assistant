from typing import Any

from agents.mathematical_agent import MathematicalAgent
from agents.writer_agent import WriterAgent
from memory.session_memory import SessionMemory


class ChatbotOrchestrator:
    """
    Orchestrates the interaction between agents and session memory.

    Attributes:
        mathematical_agent (MathematicalAgent): Agent responsible for
            executing mathematical operations.
        writer_agent (WriterAgent): Agent responsible for generating
            user-friendly responses.
        memory (SessionMemory): Memory responsible for storing
            conversation context.
    """

    def __init__(
        self,
        mathematical_agent: MathematicalAgent,
        writer_agent: WriterAgent,
        memory: SessionMemory,
    ) -> None:
        """
        Initializes the chatbot orchestrator.

        Args:
            mathematical_agent (MathematicalAgent): Mathematical agent
                dependency.
            writer_agent (WriterAgent): Writer agent dependency.
            memory (SessionMemory): Session memory dependency.
        """
        self.mathematical_agent = mathematical_agent
        self.writer_agent = writer_agent
        self.memory = memory

    def handle_math_request(
        self,
        operation: str,
        first_number: float,
        second_number: float,
        user_message: str,
        user_language: str = "en",
    ) -> dict[str, Any]:
        """
        Handles a mathematical request using agents and memory.

        Args:
            operation (str): Mathematical operation name.
            first_number (float): First operand.
            second_number (float): Second operand.
            user_message (str): Original user message.
            user_language (str): User language code.

        Returns:
            dict[str, Any]: Structured orchestration result.
        """
        self.memory.add_message(
            role="user",
            content=user_message,
        )

        math_result = self.mathematical_agent.execute(
            operation=operation,
            first_number=first_number,
            second_number=second_number,
        )

        self.memory.set_last_result(
            result=math_result["result"],
        )

        final_response = self.writer_agent.execute(
            math_result=math_result,
            user_language=user_language,
        )

        self.memory.add_message(
            role="assistant",
            content=final_response,
        )

        return {
            "math_result": math_result,
            "final_response": final_response,
            "messages": self.memory.get_messages(),
            "last_result": self.memory.get_last_result(),
        }