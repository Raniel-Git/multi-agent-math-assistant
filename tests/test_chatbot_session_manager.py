from unittest.mock import Mock

from factories.chatbot_factory import ChatbotFactory
from services.chatbot_service import ChatbotService
from services.chatbot_session_manager import ChatbotSessionManager


def test_get_service_returns_same_service_for_same_conversation() -> None:
    factory = Mock(spec=ChatbotFactory)
    chatbot_service = Mock(spec=ChatbotService)
    factory.create_service.return_value = chatbot_service

    manager = ChatbotSessionManager(factory=factory)

    first_service = manager.get_service(
        conversation_id="conversation-a",
    )
    second_service = manager.get_service(
        conversation_id="conversation-a",
    )

    assert first_service is second_service
    factory.create_service.assert_called_once_with()


def test_get_service_creates_isolated_services_for_conversations() -> None:
    factory = Mock(spec=ChatbotFactory)
    service_a = Mock(spec=ChatbotService)
    service_b = Mock(spec=ChatbotService)

    factory.create_service.side_effect = [
        service_a,
        service_b,
    ]

    manager = ChatbotSessionManager(factory=factory)

    result_a = manager.get_service(
        conversation_id="conversation-a",
    )
    result_b = manager.get_service(
        conversation_id="conversation-b",
    )

    assert result_a is service_a
    assert result_b is service_b
    assert result_a is not result_b
    assert factory.create_service.call_count == 2


def test_clear_session_removes_only_requested_conversation() -> None:
    factory = Mock(spec=ChatbotFactory)
    service_a = Mock(spec=ChatbotService)
    service_b = Mock(spec=ChatbotService)
    new_service_a = Mock(spec=ChatbotService)

    factory.create_service.side_effect = [
        service_a,
        service_b,
        new_service_a,
    ]

    manager = ChatbotSessionManager(factory=factory)

    manager.get_service(
        conversation_id="conversation-a",
    )
    manager.get_service(
        conversation_id="conversation-b",
    )

    manager.clear_session(
        conversation_id="conversation-a",
    )

    result_b = manager.get_service(
        conversation_id="conversation-b",
    )
    result_a = manager.get_service(
        conversation_id="conversation-a",
    )

    assert result_b is service_b
    assert result_a is new_service_a
    assert factory.create_service.call_count == 3


def test_clear_unknown_session_does_not_raise_error() -> None:
    factory = Mock(spec=ChatbotFactory)
    manager = ChatbotSessionManager(factory=factory)

    manager.clear_session(
        conversation_id="unknown-conversation",
    )

    factory.create_service.assert_not_called()
