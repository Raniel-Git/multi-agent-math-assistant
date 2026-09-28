from collections.abc import Generator
from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient

from api.dependencies.chatbot import get_chatbot_session_manager
from main import app
from services.chatbot_service import ChatbotService
from services.chatbot_session_manager import ChatbotSessionManager

CONVERSATION_ID = "550e8400-e29b-41d4-a716-446655440000"


@pytest.fixture
def chatbot_service() -> Mock:
    service = Mock(spec=ChatbotService)

    service.process_message.return_value = "The result is 10."
    service.get_messages.return_value = [
        {
            "role": "user",
            "content": "5 + 5",
        },
        {
            "role": "assistant",
            "content": "The result is 10.",
        },
    ]
    service.get_last_result.return_value = 10.0

    return service


@pytest.fixture
def session_manager(
    chatbot_service: Mock,
) -> Mock:
    manager = Mock(spec=ChatbotSessionManager)
    manager.get_service.return_value = chatbot_service

    return manager


@pytest.fixture
def client(
    session_manager: Mock,
) -> Generator[TestClient, None, None]:
    def override_session_manager() -> Mock:
        return session_manager

    app.dependency_overrides[get_chatbot_session_manager] = override_session_manager

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


def test_health_check_returns_healthy_status(
    client: TestClient,
) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "healthy",
    }


def test_process_message_returns_chatbot_response(
    client: TestClient,
    chatbot_service: Mock,
    session_manager: Mock,
) -> None:
    response = client.post(
        "/api/v1/chat/messages",
        json={
            "message": "5 + 5",
            "conversation_id": CONVERSATION_ID,
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "success": True,
        "message": "Message processed successfully.",
        "data": {
            "response": "The result is 10.",
            "messages": [
                {
                    "role": "user",
                    "content": "5 + 5",
                },
                {
                    "role": "assistant",
                    "content": "The result is 10.",
                },
            ],
            "last_result": 10.0,
        },
    }

    session_manager.get_service.assert_called_once_with(
        conversation_id=CONVERSATION_ID,
    )
    chatbot_service.process_message.assert_called_once_with(
        message="5 + 5",
    )


def test_process_message_rejects_missing_message(
    client: TestClient,
) -> None:
    response = client.post(
        "/api/v1/chat/messages",
        json={
            "conversation_id": CONVERSATION_ID,
        },
    )

    assert response.status_code == 422


def test_process_message_rejects_empty_message(
    client: TestClient,
) -> None:
    response = client.post(
        "/api/v1/chat/messages",
        json={
            "message": "",
            "conversation_id": CONVERSATION_ID,
        },
    )

    assert response.status_code == 422


def test_process_message_rejects_missing_conversation_id(
    client: TestClient,
) -> None:
    response = client.post(
        "/api/v1/chat/messages",
        json={
            "message": "5 + 5",
        },
    )

    assert response.status_code == 422


def test_process_message_rejects_invalid_conversation_id(
    client: TestClient,
) -> None:
    response = client.post(
        "/api/v1/chat/messages",
        json={
            "message": "5 + 5",
            "conversation_id": "invalid-id",
        },
    )

    assert response.status_code == 422


def test_clear_memory_returns_success_response(
    client: TestClient,
    session_manager: Mock,
) -> None:
    response = client.delete(
        "/api/v1/chat/memory",
        params={
            "conversation_id": CONVERSATION_ID,
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "success": True,
        "message": "Chatbot memory cleared successfully.",
    }

    session_manager.clear_session.assert_called_once_with(
        conversation_id=CONVERSATION_ID,
    )


def test_clear_memory_rejects_missing_conversation_id(
    client: TestClient,
) -> None:
    response = client.delete(
        "/api/v1/chat/memory",
    )

    assert response.status_code == 422


def test_clear_memory_rejects_invalid_conversation_id(
    client: TestClient,
) -> None:
    response = client.delete(
        "/api/v1/chat/memory",
        params={
            "conversation_id": "invalid-id",
        },
    )

    assert response.status_code == 422


def test_cors_allows_configured_origin(
    client: TestClient,
) -> None:
    response = client.options(
        "/api/v1/chat/messages",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "POST",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:3000"


def test_cors_does_not_allow_unconfigured_origin(
    client: TestClient,
) -> None:
    response = client.options(
        "/api/v1/chat/messages",
        headers={
            "Origin": "http://localhost:4000",
            "Access-Control-Request-Method": "POST",
        },
    )

    assert "access-control-allow-origin" not in response.headers
