from typing import Any
from unittest.mock import Mock

import pytest

from agents.conversation_agent import ConversationAgent
from agents.intent_agent import IntentAgent
from memory.session_memory import SessionMemory
from orchestration.orchestrator import ChatbotOrchestrator
from tools.expression_tools import ExpressionTool
from utils.language_detector import LanguageDetector
from utils.math_parser import MathParser
from utils.parser_exceptions import (
    AmbiguousMathRequestError,
    InvalidMathExpressionError,
    MissingContextError,
    UnsupportedMathRequestError,
)
from workflows.chatbot_workflow import ChatbotWorkflow


@pytest.fixture
def workflow_dependencies() -> dict[str, Any]:
    memory = SessionMemory()
    orchestrator = Mock(spec=ChatbotOrchestrator)
    conversation_agent = Mock(spec=ConversationAgent)
    intent_agent = Mock(spec=IntentAgent)
    expression_tool = Mock(spec=ExpressionTool)
    parser = Mock(spec=MathParser)
    language_detector = Mock(spec=LanguageDetector)

    language_detector.detect.return_value = "en"
    expression_tool.extract_expression.return_value = None
    parser.parse.side_effect = UnsupportedMathRequestError()

    return {
        "memory": memory,
        "orchestrator": orchestrator,
        "conversation_agent": conversation_agent,
        "intent_agent": intent_agent,
        "expression_tool": expression_tool,
        "parser": parser,
        "language_detector": language_detector,
    }


@pytest.fixture
def chatbot_workflow(
    workflow_dependencies: dict[str, Any],
) -> ChatbotWorkflow:
    return ChatbotWorkflow(
        memory=workflow_dependencies["memory"],
        orchestrator=workflow_dependencies["orchestrator"],
        conversation_agent=workflow_dependencies["conversation_agent"],
        intent_agent=workflow_dependencies["intent_agent"],
        expression_tool=workflow_dependencies["expression_tool"],
        parser=workflow_dependencies["parser"],
        language_detector=workflow_dependencies["language_detector"],
    )


def test_process_message_uses_expression_result(
    chatbot_workflow: ChatbotWorkflow,
    workflow_dependencies: dict[str, Any],
) -> None:
    workflow_dependencies[
        "expression_tool"
    ].extract_expression.return_value = "5 + 5"
    workflow_dependencies["expression_tool"].evaluate.return_value = 10.0

    response = chatbot_workflow.process_message("5 + 5")

    assert response == "The result is 10."
    assert chatbot_workflow.get_last_result() == 10.0
    assert chatbot_workflow.get_messages() == [
        {
            "role": "user",
            "content": "5 + 5",
        },
        {
            "role": "assistant",
            "content": "The result is 10.",
        },
    ]


def test_process_message_uses_spanish_expression_response(
    chatbot_workflow: ChatbotWorkflow,
    workflow_dependencies: dict[str, Any],
) -> None:
    workflow_dependencies["language_detector"].detect.return_value = "es"
    workflow_dependencies[
        "expression_tool"
    ].extract_expression.return_value = "5 + 5"
    workflow_dependencies["expression_tool"].evaluate.return_value = 10.0

    response = chatbot_workflow.process_message("5 + 5")

    assert response == "El resultado es 10."


def test_process_message_handles_expression_division_by_zero(
    chatbot_workflow: ChatbotWorkflow,
    workflow_dependencies: dict[str, Any],
) -> None:
    workflow_dependencies[
        "expression_tool"
    ].extract_expression.return_value = "10 / 0"
    workflow_dependencies["expression_tool"].evaluate.side_effect = ValueError(
        "Division by zero"
    )

    response = chatbot_workflow.process_message("calculate 10 / zero")

    assert response == (
        "Division by zero is not allowed. "
        "That operation is mathematically invalid."
    )


def test_process_message_uses_local_parser(
    chatbot_workflow: ChatbotWorkflow,
    workflow_dependencies: dict[str, Any],
) -> None:
    workflow_dependencies["parser"].parse.side_effect = None
    workflow_dependencies["parser"].parse.return_value = {
        "operation": "add",
        "first_number": 5.0,
        "second_number": 5.0,
    }
    workflow_dependencies[
        "orchestrator"
    ].handle_math_request.return_value = {
        "final_response": "The result is 10.",
    }

    response = chatbot_workflow.process_message("five plus five")

    assert response == "The result is 10."
    workflow_dependencies[
        "orchestrator"
    ].handle_math_request.assert_called_once_with(
        operation="add",
        first_number=5.0,
        second_number=5.0,
        user_language="en",
    )


def test_process_message_uses_valid_intent_result(
    chatbot_workflow: ChatbotWorkflow,
    workflow_dependencies: dict[str, Any],
) -> None:
    workflow_dependencies["intent_agent"].interpret.return_value = {
        "intent": "math_operation",
        "operation": "multiply",
        "first_number": 4.0,
        "second_number": 3.0,
        "language": "en",
    }
    workflow_dependencies[
        "orchestrator"
    ].handle_math_request.return_value = {
        "final_response": "The result is 12.",
    }

    response = chatbot_workflow.process_message(
        "Please multiply four by three",
    )

    assert response == "The result is 12."


def test_process_message_uses_conversation_for_non_math_intent(
    chatbot_workflow: ChatbotWorkflow,
    workflow_dependencies: dict[str, Any],
) -> None:
    workflow_dependencies["intent_agent"].interpret.return_value = {
        "intent": "greeting",
        "operation": None,
        "first_number": None,
        "second_number": None,
        "language": "en",
    }
    workflow_dependencies[
        "conversation_agent"
    ].execute.return_value = "Hello! How can I help?"

    response = chatbot_workflow.process_message("Hello")

    assert response == "Hello! How can I help?"


def test_process_message_uses_conversation_for_incomplete_math_intent(
    chatbot_workflow: ChatbotWorkflow,
    workflow_dependencies: dict[str, Any],
) -> None:
    workflow_dependencies["intent_agent"].interpret.return_value = {
        "intent": "math_operation",
        "operation": "add",
        "first_number": 5.0,
        "second_number": None,
        "language": "en",
    }
    workflow_dependencies[
        "conversation_agent"
    ].execute.return_value = "Invalid operation."

    response = chatbot_workflow.process_message("Add five")

    assert response == "Invalid operation."
    workflow_dependencies[
        "conversation_agent"
    ].execute.assert_called_once()


def test_process_message_handles_intent_client_failure(
    chatbot_workflow: ChatbotWorkflow,
    workflow_dependencies: dict[str, Any],
) -> None:
    workflow_dependencies["intent_agent"].interpret.side_effect = ValueError(
        "Client unavailable"
    )
    workflow_dependencies[
        "conversation_agent"
    ].execute.return_value = "I could not understand."

    response = chatbot_workflow.process_message("Unknown request")

    assert response == "I could not understand."


def test_process_message_uses_fallback_when_conversation_fails(
    chatbot_workflow: ChatbotWorkflow,
    workflow_dependencies: dict[str, Any],
) -> None:
    workflow_dependencies["intent_agent"].interpret.return_value = {
        "intent": "greeting",
        "operation": None,
        "first_number": None,
        "second_number": None,
        "language": "en",
    }
    workflow_dependencies["conversation_agent"].execute.side_effect = (
        ValueError("Client unavailable")
    )

    response = chatbot_workflow.process_message("Hello")

    assert response == (
        "Hello! I can help with basic mathematical operations. "
        "Try something like: 5 + 4."
    )


@pytest.mark.parametrize(
    ("error", "expected_response"),
    [
        (
            InvalidMathExpressionError(),
            (
                "I could not identify a valid mathematical operation. "
                "Use only numbers and one operation, such as: 2 + 4."
            ),
        ),
        (
            AmbiguousMathRequestError(),
            (
                "Your request is incomplete. "
                "Please specify the mathematical operation."
            ),
        ),
        (
            MissingContextError(),
            (
                "I need a previous result to continue. "
                "Start with a complete operation, such as: 5 + 4."
            ),
        ),
        (
            UnsupportedMathRequestError(),
            (
                "I can only help with basic mathematical operations: "
                "addition, subtraction, multiplication and division."
            ),
        ),
    ],
)
def test_process_message_handles_domain_errors(
    chatbot_workflow: ChatbotWorkflow,
    workflow_dependencies: dict[str, Any],
    error: Exception,
    expected_response: str,
) -> None:
    workflow_dependencies[
        "expression_tool"
    ].extract_expression.side_effect = error

    response = chatbot_workflow.process_message("Invalid request")

    assert response == expected_response


def test_clear_memory_preserves_shared_memory_instance(
    chatbot_workflow: ChatbotWorkflow,
    workflow_dependencies: dict[str, Any],
) -> None:
    memory = workflow_dependencies["memory"]
    memory.add_message(
        role="user",
        content="5 + 5",
    )
    memory.set_last_result(10.0)

    chatbot_workflow.clear_memory()

    assert chatbot_workflow.memory is memory
    assert chatbot_workflow.get_messages() == []
    assert chatbot_workflow.get_last_result() is None
