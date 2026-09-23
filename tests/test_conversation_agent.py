from unittest.mock import Mock

import pytest

from agents.conversation_agent import ConversationAgent
from clients.llm_client import LLMClient


@pytest.fixture
def llm_client() -> Mock:
    return Mock(spec=LLMClient)


@pytest.fixture
def conversation_agent(llm_client: Mock) -> ConversationAgent:
    return ConversationAgent(llm_client=llm_client)


def test_execute_includes_conversation_history_in_prompt(
    conversation_agent: ConversationAgent,
    llm_client: Mock,
) -> None:
    llm_client.generate_text.return_value = "Your name is Raniel."
    conversation_history = [
        {
            "role": "user",
            "content": "My name is Raniel",
        },
        {
            "role": "assistant",
            "content": "Hello, Raniel!",
        },
    ]

    response = conversation_agent.execute(
        user_message="What is my name?",
        intent="out_of_scope",
        user_language="en",
        conversation_history=conversation_history,
    )

    prompt = llm_client.generate_text.call_args.kwargs["prompt"]

    assert response == "Your name is Raniel."
    assert "My name is Raniel" in prompt
    assert "What is my name?" in prompt
    assert "Recent conversation history:" in prompt


def test_execute_limits_conversation_history_to_ten_messages(
    conversation_agent: ConversationAgent,
    llm_client: Mock,
) -> None:
    llm_client.generate_text.return_value = "Response"
    conversation_history = [
        {
            "role": "user",
            "content": f"message-{index}",
        }
        for index in range(12)
    ]

    conversation_agent.execute(
        user_message="Current message",
        intent="out_of_scope",
        user_language="en",
        conversation_history=conversation_history,
    )

    prompt = llm_client.generate_text.call_args.kwargs["prompt"]

    assert "'content': 'message-0'" not in prompt
    assert "'content': 'message-1'" not in prompt
    assert "'content': 'message-2'" in prompt
    assert "'content': 'message-11'" in prompt


def test_execute_uses_empty_history_when_history_is_none(
    conversation_agent: ConversationAgent,
    llm_client: Mock,
) -> None:
    llm_client.generate_text.return_value = "Hello!"

    response = conversation_agent.execute(
        user_message="Hello",
        intent="greeting",
        user_language="en",
    )

    prompt = llm_client.generate_text.call_args.kwargs["prompt"]

    assert response == "Hello!"
    assert "Recent conversation history:\n[]" in prompt


def test_execute_builds_portuguese_prompt_with_history(
    conversation_agent: ConversationAgent,
    llm_client: Mock,
) -> None:
    llm_client.generate_text.return_value = "Seu nome é Raniel."
    conversation_history = [
        {
            "role": "user",
            "content": "Meu nome é Raniel",
        },
    ]

    response = conversation_agent.execute(
        user_message="Qual é o meu nome?",
        intent="out_of_scope",
        user_language="pt",
        conversation_history=conversation_history,
    )

    prompt = llm_client.generate_text.call_args.kwargs["prompt"]

    assert response == "Seu nome é Raniel."
    assert "Meu nome é Raniel" in prompt
    assert "Qual é o meu nome?" in prompt
    assert "Histórico recente da conversa:" in prompt


def test_execute_uses_default_response_without_llm_client() -> None:
    agent = ConversationAgent()

    response = agent.execute(
        user_message="Hello",
        intent="greeting",
        user_language="en",
    )

    assert response == (
        "Hello! I can help with basic math operations, "
        "such as 5 + 4 or 10 divided by 2."
    )


def test_execute_uses_default_response_when_llm_client_fails(
    conversation_agent: ConversationAgent,
    llm_client: Mock,
) -> None:
    llm_client.generate_text.side_effect = ValueError("LLM unavailable")

    response = conversation_agent.execute(
        user_message="Hello",
        intent="greeting",
        user_language="en",
    )

    assert response == (
        "Hello! I can help with basic math operations, "
        "such as 5 + 4 or 10 divided by 2."
    )


@pytest.mark.parametrize(
    ("intent", "expected_response"),
    [
        (
            "greeting",
            (
                "Olá! Posso ajudar com operações matemáticas básicas, "
                "como 5 + 4 ou quanto é 10 dividido por 2."
            ),
        ),
        (
            "out_of_scope",
            (
                "Eu sou focado em operações matemáticas básicas. "
                "Tente me enviar uma soma, subtração, multiplicação "
                "ou divisão."
            ),
        ),
        (
            "invalid_math",
            (
                "Não consegui identificar uma operação matemática "
                "válida. Tente usar dois números, como 2 + 4."
            ),
        ),
        (
            "missing_context",
            (
                "Preciso de um resultado anterior para continuar. "
                "Comece com uma operação completa, como 5 + 4."
            ),
        ),
        (
            "unknown",
            (
                "Não consegui entender totalmente, mas posso ajudar "
                "com matemática básica."
            ),
        ),
    ],
)
def test_execute_uses_portuguese_default_responses(
    intent: str,
    expected_response: str,
) -> None:
    agent = ConversationAgent()

    response = agent.execute(
        user_message="Mensagem",
        intent=intent,
        user_language="pt",
    )

    assert response == expected_response


@pytest.mark.parametrize(
    ("intent", "expected_response"),
    [
        (
            "out_of_scope",
            (
                "I focus on basic math operations. Try sending an addition, "
                "subtraction, multiplication or division."
            ),
        ),
        (
            "invalid_math",
            (
                "I could not identify a valid math operation. "
                "Try using two numbers, such as 2 + 4."
            ),
        ),
        (
            "missing_context",
            (
                "I need a previous result to continue. "
                "Start with a complete operation, such as 5 + 4."
            ),
        ),
        (
            "unknown",
            ("I could not fully understand, but I can help with basic math."),
        ),
    ],
)
def test_execute_uses_english_default_responses(
    intent: str,
    expected_response: str,
) -> None:
    agent = ConversationAgent()

    response = agent.execute(
        user_message="Message",
        intent=intent,
        user_language="en",
    )

    assert response == expected_response


def test_execute_uses_portuguese_text_math_context() -> None:
    agent = ConversationAgent()
    text_math_context = {
        "word": "casa",
        "first_number": 2.0,
        "letter_count": 4,
        "possible_result": 8.0,
    }

    response = agent.execute(
        user_message="2 vezes casa",
        intent="invalid_math",
        user_language="pt",
        text_math_context=text_math_context,
    )

    assert response == (
        "Essa não é uma operação matemática direta, porque "
        "'casa' é uma palavra. Uma possível interpretação "
        "seria usar a quantidade de letras de 'casa', que é "
        "4; nesse caso, 2 com 4 resultaria em 8."
    )


def test_execute_uses_english_text_math_context() -> None:
    agent = ConversationAgent()
    text_math_context = {
        "word": "house",
        "first_number": 2.5,
        "letter_count": 5,
        "possible_result": 12.5,
    }

    response = agent.execute(
        user_message="2.5 times house",
        intent="invalid_math",
        user_language="en",
        text_math_context=text_math_context,
    )

    assert response == (
        "This is not a direct math operation because 'house' is "
        "a word. One possible interpretation is to use the number "
        "of letters in 'house', which is 5; in that "
        "case, the result would be 12.5."
    )
