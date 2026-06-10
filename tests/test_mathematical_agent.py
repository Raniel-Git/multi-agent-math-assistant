import pytest

from agents.mathematical_agent import MathematicalAgent


def test_mathematical_agent_executes_addition() -> None:
    agent = MathematicalAgent()

    result = agent.execute(
        operation="add",
        first_number=5,
        second_number=4,
    )

    assert result == {
        "operation": "add",
        "first_number": 5,
        "second_number": 4,
        "result": 9,
    }


def test_mathematical_agent_executes_division() -> None:
    agent = MathematicalAgent()

    result = agent.execute(
        operation="divide",
        first_number=20,
        second_number=5,
    )

    assert result == {
        "operation": "divide",
        "first_number": 20,
        "second_number": 5,
        "result": 4,
    }


def test_mathematical_agent_rejects_unsupported_operation() -> None:
    agent = MathematicalAgent()

    with pytest.raises(ValueError, match="Unsupported operation"):
        agent.execute(
            operation="power",
            first_number=2,
            second_number=3,
        )