from memory.session_memory import SessionMemory


def test_add_message_stores_message() -> None:
    memory = SessionMemory()

    memory.add_message(
        role="user",
        content="5 + 4",
    )

    assert memory.get_messages() == [
        {
            "role": "user",
            "content": "5 + 4",
        }
    ]


def test_set_last_result_stores_result() -> None:
    memory = SessionMemory()

    memory.set_last_result(9)

    assert memory.get_last_result() == 9


def test_initial_memory_is_empty() -> None:
    memory = SessionMemory()

    assert memory.get_messages() == []
    assert memory.get_last_result() is None