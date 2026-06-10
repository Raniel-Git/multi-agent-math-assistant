from agents.mathematical_agent import MathematicalAgent
from agents.writer_agent import WriterAgent
from memory.session_memory import SessionMemory
from orchestration.orchestrator import ChatbotOrchestrator


def test_orchestrator_handles_math_request() -> None:
    memory = SessionMemory()
    orchestrator = ChatbotOrchestrator(
        mathematical_agent=MathematicalAgent(),
        writer_agent=WriterAgent(),
        memory=memory,
    )

    result = orchestrator.handle_math_request(
        operation="add",
        first_number=5,
        second_number=4,
        user_message="5 + 4",
        user_language="en",
    )

    assert result["math_result"] == {
        "operation": "add",
        "first_number": 5,
        "second_number": 4,
        "result": 9,
    }
    assert result["final_response"] == "The result is 9."
    assert result["last_result"] == 9
    assert result["messages"] == [
        {
            "role": "user",
            "content": "5 + 4",
        },
        {
            "role": "assistant",
            "content": "The result is 9.",
        },
    ]


def test_orchestrator_handles_portuguese_response() -> None:
    memory = SessionMemory()
    orchestrator = ChatbotOrchestrator(
        mathematical_agent=MathematicalAgent(),
        writer_agent=WriterAgent(),
        memory=memory,
    )

    result = orchestrator.handle_math_request(
        operation="subtract",
        first_number=9,
        second_number=2,
        user_message="subtrair 2",
        user_language="pt",
    )

    assert result["final_response"] == "O resultado é 7."
    assert result["last_result"] == 7