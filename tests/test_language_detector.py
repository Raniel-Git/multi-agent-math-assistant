from utils.language_detector import LanguageDetector


def test_detect_portuguese_language() -> None:
    detector = LanguageDetector()

    result = detector.detect("subtrair 2")

    assert result == "pt"


def test_detect_english_language() -> None:
    detector = LanguageDetector()

    result = detector.detect("subtract 2")

    assert result == "en"