from agents.writer_agent import WriterAgent


def test_writer_agent_generates_english_response() -> None:
    agent = WriterAgent()

    response = agent.execute(
        math_result={
            "operation": "add",
            "first_number": 5,
            "second_number": 4,
            "result": 9,
        },
        user_language="en",
    )

    assert response == "The result is 9."


def test_writer_agent_generates_portuguese_response() -> None:
    agent = WriterAgent()

    response = agent.execute(
        math_result={
            "operation": "subtract",
            "first_number": 9,
            "second_number": 2,
            "result": 7,
        },
        user_language="pt",
    )

    assert response == "O resultado é 7."


def test_writer_agent_formats_decimal_result() -> None:
    agent = WriterAgent()

    response = agent.execute(
        math_result={
            "operation": "divide",
            "first_number": 7.5,
            "second_number": 2,
            "result": 3.75,
        },
        user_language="en",
    )

    assert response == "The result is 3.75."