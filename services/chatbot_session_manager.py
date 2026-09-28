from factories.chatbot_factory import ChatbotFactory
from services.chatbot_service import ChatbotService


class ChatbotSessionManager:
    """Manages isolated chatbot services for conversation sessions."""

    def __init__(
        self,
        factory: ChatbotFactory,
    ) -> None:
        """Initialize the chatbot session manager.

        Args:
            factory: Factory used to create chatbot services.
        """
        self.factory = factory
        self._sessions: dict[str, ChatbotService] = {}

    def get_service(
        self,
        conversation_id: str,
    ) -> ChatbotService:
        """Return the chatbot service associated with a conversation.

        Args:
            conversation_id: Unique conversation identifier.

        Returns:
            Chatbot service associated with the conversation.
        """
        if conversation_id not in self._sessions:
            self._sessions[conversation_id] = self.factory.create_service()

        return self._sessions[conversation_id]

    def clear_session(
        self,
        conversation_id: str,
    ) -> None:
        """Remove a conversation session from memory.

        Args:
            conversation_id: Unique conversation identifier.
        """
        self._sessions.pop(conversation_id, None)
