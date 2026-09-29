from functools import lru_cache

from config.settings import Settings
from factories.chatbot_factory import ChatbotFactory
from services.chatbot_session_manager import ChatbotSessionManager


@lru_cache
def get_chatbot_session_manager() -> ChatbotSessionManager:
    """Return the shared chatbot session manager.

    Returns:
        Configured chatbot session manager.
    """
    settings = Settings.from_environment()
    factory = ChatbotFactory(settings=settings)

    return ChatbotSessionManager(factory=factory)
