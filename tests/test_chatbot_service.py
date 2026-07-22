from typing import Any

from services.chatbot_service import ChatbotService


class FakeLLMClient:
    """Provides deterministic responses for chatbot service tests."""

    def generate_text(self, prompt: str) -> str:
        return "Resposta simulada."

    def generate_json(self, prompt: str) -> dict[str, Any]:
        return {
            "intent": "unclear",
            "operation": None,
            "first_number": None,
            "second_number": None,
            "language": "pt",
        }


def build_chatbot_service() -> ChatbotService:
    return ChatbotService(
        llm_client=FakeLLMClient(),
    )


def test_process_message_executes_addition() -> None:
    service = build_chatbot_service()

    response = service.process_message("5 + 5")

    assert response == "O resultado é 10."
    assert service.get_last_result() == 10.0


def test_process_message_uses_previous_result() -> None:
    service = build_chatbot_service()

    service.process_message("5 + 5")
    response = service.process_message(
        "Agora multiplica isso por 3",
    )

    assert response == "O resultado é 30."
    assert service.get_last_result() == 30.0


def test_process_message_handles_division_by_zero() -> None:
    service = build_chatbot_service()

    response = service.process_message("10 dividido por 0")

    assert response == (
        "Não é possível dividir por zero. "
        "Essa operação é inválida matematicamente."
    )


def test_process_message_stores_conversation_history() -> None:
    service = build_chatbot_service()

    service.process_message("5 + 5")

    messages = service.get_messages()

    assert messages == [
        {
            "role": "user",
            "content": "5 + 5",
        },
        {
            "role": "assistant",
            "content": "O resultado é 10.",
        },
    ]


def test_clear_memory_removes_session_data() -> None:
    service = build_chatbot_service()

    service.process_message("5 + 5")
    service.clear_memory()

    assert service.get_messages() == []
    assert service.get_last_result() is None