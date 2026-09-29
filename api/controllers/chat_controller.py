from api.schemas.chat import (
    ChatRequest,
    ChatResponse,
    ChatResponseData,
    ClearMemoryResponse,
)
from services.chatbot_session_manager import ChatbotSessionManager


class ChatController:
    """Coordinates chatbot API operations.

    Attributes:
        session_manager: Manager responsible for isolated chatbot sessions.
    """

    def __init__(
        self,
        session_manager: ChatbotSessionManager,
    ) -> None:
        """Initialize the chat controller.

        Args:
            session_manager: Manager responsible for chatbot sessions.
        """
        self.session_manager = session_manager

    def process_message(
        self,
        request: ChatRequest,
    ) -> ChatResponse:
        """Process a chatbot message in an isolated conversation session.

        Args:
            request: Validated chatbot request.

        Returns:
            Structured chatbot response.
        """
        chatbot_service = self.session_manager.get_service(
            conversation_id=str(request.conversation_id),
        )

        response = chatbot_service.process_message(
            message=request.message,
        )

        return ChatResponse(
            success=True,
            message="Message processed successfully.",
            data=ChatResponseData(
                response=response,
                messages=chatbot_service.get_messages(),
                last_result=chatbot_service.get_last_result(),
            ),
        )

    def clear_memory(
        self,
        conversation_id: str,
    ) -> ClearMemoryResponse:
        """Clear memory for a specific conversation session.

        Args:
            conversation_id: Unique conversation identifier.

        Returns:
            Confirmation that the conversation memory was cleared.
        """
        self.session_manager.clear_session(
            conversation_id=conversation_id,
        )

        return ClearMemoryResponse(
            success=True,
            message="Chatbot memory cleared successfully.",
        )
