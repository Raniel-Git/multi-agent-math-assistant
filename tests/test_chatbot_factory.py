from typing import Any

from config.settings import Settings
from factories.chatbot_factory import ChatbotFactory
from services.chatbot_service import ChatbotService


class FakeLLMClient:
    def generate_text(
        self,
        prompt: str,
    ) -> str:
        return "Generated response."

    def generate_json(
        self,
        prompt: str,
    ) -> dict[str, Any]:
        return {
            "intent": "unclear",
            "operation": None,
            "first_number": None,
            "second_number": None,
            "language": "en",
        }


def test_create_service_returns_configured_service() -> None:
    factory = ChatbotFactory(
        settings=Settings(
            llm_provider="ollama",
        ),
    )

    service = factory.create_service(
        llm_client=FakeLLMClient(),
    )

    assert isinstance(service, ChatbotService)
    assert service.get_messages() == []
    assert service.get_last_result() is None
