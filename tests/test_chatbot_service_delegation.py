from typing import Any
from unittest.mock import Mock

from services.chatbot_service import ChatbotService
from workflows.chatbot_workflow import ChatbotWorkflow


def test_process_message_delegates_to_workflow() -> None:
    workflow = Mock(spec=ChatbotWorkflow)
    workflow.process_message.return_value = "The result is 10."
    service = ChatbotService(workflow=workflow)

    response = service.process_message("5 + 5")

    workflow.process_message.assert_called_once_with("5 + 5")
    assert response == "The result is 10."


def test_get_messages_delegates_to_workflow() -> None:
    messages: list[dict[str, Any]] = [
        {
            "role": "user",
            "content": "5 + 5",
        },
    ]
    workflow = Mock(spec=ChatbotWorkflow)
    workflow.get_messages.return_value = messages
    service = ChatbotService(workflow=workflow)

    result = service.get_messages()

    workflow.get_messages.assert_called_once_with()
    assert result == messages


def test_get_last_result_delegates_to_workflow() -> None:
    workflow = Mock(spec=ChatbotWorkflow)
    workflow.get_last_result.return_value = 10.0
    service = ChatbotService(workflow=workflow)

    result = service.get_last_result()

    workflow.get_last_result.assert_called_once_with()
    assert result == 10.0


def test_clear_memory_delegates_to_workflow() -> None:
    workflow = Mock(spec=ChatbotWorkflow)
    service = ChatbotService(workflow=workflow)

    service.clear_memory()

    workflow.clear_memory.assert_called_once_with()
