from fastapi import APIRouter, Depends, status

from api.controllers.chat_controller import ChatController
from api.dependencies.chatbot import get_chatbot_service
from api.schemas.chat import (
    ChatRequest,
    ChatResponse,
    ClearMemoryResponse,
)
from services.chatbot_service import ChatbotService

router = APIRouter(
    prefix="/chat",
    tags=["Chat"],
)


def get_chat_controller(
    chatbot_service: ChatbotService = Depends(get_chatbot_service),
) -> ChatController:
    """Create the chat controller with its required service.

    Args:
        chatbot_service: Injected chatbot service.

    Returns:
        Configured chat controller.
    """
    return ChatController(
        chatbot_service=chatbot_service,
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
    controller: ChatController = Depends(get_chat_controller),
) -> ClearMemoryResponse:
    """Clear the current chatbot memory."""
    return controller.clear_memory()
