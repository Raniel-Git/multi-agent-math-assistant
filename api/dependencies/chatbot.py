from functools import lru_cache

from config.settings import Settings
from factories.chatbot_factory import ChatbotFactory
from services.chatbot_service import ChatbotService


@lru_cache
def get_chatbot_service() -> ChatbotService:
    """Return the shared chatbot service instance.

    Returns:
        Configured chatbot service.
    """
    settings = Settings.from_environment()
    factory = ChatbotFactory(settings=settings)

    return factory.create_service()
