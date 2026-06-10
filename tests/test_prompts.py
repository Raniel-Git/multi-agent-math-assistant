from prompts.mathematical_prompt import MATHEMATICAL_AGENT_PROMPT
from prompts.writer_prompt import WRITER_AGENT_PROMPT


def test_mathematical_agent_prompt_exists() -> None:
    assert MATHEMATICAL_AGENT_PROMPT


def test_writer_agent_prompt_exists() -> None:
    assert WRITER_AGENT_PROMPT