from uuid import UUID

from fastapi import APIRouter, Depends, status

from api.controllers.chat_controller import ChatController
from api.dependencies.chatbot import get_chatbot_session_manager
from api.schemas.chat import ChatRequest, ChatResponse, ClearMemoryResponse
from services.chatbot_session_manager import ChatbotSessionManager

router = APIRouter(
    prefix="/chat",
    tags=["Chat"],
)


def get_chat_controller(
    session_manager: ChatbotSessionManager = Depends(
        dependency=get_chatbot_session_manager,
    ),
) -> ChatController:
    """Create the chat controller with its required session manager.

    Args:
        session_manager: Injected chatbot session manager.

    Returns:
        Configured chat controller.
    """
    return ChatController(
        session_manager=session_manager,
    )


@router.post(
    "/messages",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
)
def process_message(
    request: ChatRequest,
    controller: ChatController = Depends(get_chat_controller),
) -> ChatResponse:
    """Process a message through the chatbot."""
    return controller.process_message(request=request)


@router.delete(
    "/memory",
    response_model=ClearMemoryResponse,
    status_code=status.HTTP_200_OK,
)
def clear_memory(
    conversation_id: UUID,
    controller: ChatController = Depends(get_chat_controller),
) -> ClearMemoryResponse:
    """Clear the memory for a specific conversation."""
    return controller.clear_memory(
        conversation_id=str(conversation_id),
    )
