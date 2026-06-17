from utils.intent_detector import IntentDetector


def test_detect_empty_intent() -> None:
    detector = IntentDetector()

    result = detector.detect("")

    assert result == "empty"


def test_detect_greeting_intent() -> None:
    detector = IntentDetector()

    result = detector.detect("oi")

    assert result == "greeting"


def test_detect_math_operation_with_symbols() -> None:
    detector = IntentDetector()

    result = detector.detect("5 + 4")

    assert result == "math_operation"


def test_detect_math_operation_with_natural_language() -> None:
    detector = IntentDetector()

    result = detector.detect("quanto é 5 mais 4?")

    assert result == "math_operation"


def test_detect_unclear_intent() -> None:
    detector = IntentDetector()

    result = detector.detect("asdfghjkl")

    assert result == "unclear"


def test_detect_out_of_scope_intent() -> None:
    detector = IntentDetector()

    result = detector.detect("quem é neymar?")

    assert result == "out_of_scope"