from api.schemas.chat import (
    ChatRequest,
    ChatResponse,
    ChatResponseData,
    ClearMemoryResponse,
)
from services.chatbot_service import ChatbotService


class ChatController:
    """Coordinates chatbot API operations.

    Attributes:
        chatbot_service: Service responsible for chatbot operations.
    """

    def __init__(
        self,
        chatbot_service: ChatbotService,
    ) -> None:
        """Initialize the chat controller.

        Args:
            chatbot_service: Service responsible for chatbot operations.
        """
        self.chatbot_service = chatbot_service

    def process_message(
        self,
        request: ChatRequest,
    ) -> ChatResponse:
        """Process a chatbot message.

        Args:
            request: Validated chatbot request.

        Returns:
            Structured chatbot response.
        """
        response = self.chatbot_service.process_message(
            message=request.message,
        )

        return ChatResponse(
            success=True,
            message="Message processed successfully.",
            data=ChatResponseData(
                response=response,
                messages=self.chatbot_service.get_messages(),
                last_result=self.chatbot_service.get_last_result(),
            ),
        )

    def clear_memory(
        self,
    ) -> ClearMemoryResponse:
        """Clear the current chatbot conversation memory.

        Returns:
            Confirmation that the memory was cleared.
        """
        self.chatbot_service.clear_memory()

        return ClearMemoryResponse(
            success=True,
            message="Chatbot memory cleared successfully.",
        )
