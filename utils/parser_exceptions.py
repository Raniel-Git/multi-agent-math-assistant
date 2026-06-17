class UnsupportedMathRequestError(ValueError):
    """
    Raised when the user message is outside the chatbot math scope.
    """


class MissingContextError(ValueError):
    """
    Raised when a follow-up request needs previous context.
    """


class InvalidMathExpressionError(ValueError):
    """
    Raised when a message looks like math but has invalid values.
    """


class AmbiguousMathRequestError(ValueError):
    """
    Raised when the user message contains unclear mathematical intent.
    """