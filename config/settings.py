import os
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    """Stores application configuration loaded from environment variables.

    Attributes:
        llm_provider: Language model provider used by the application.
    """

    llm_provider: str

    @classmethod
    def from_environment(
        cls,
    ) -> "Settings":
        """Create settings from environment variables.

        Returns:
            Application settings loaded from the environment.
        """
        load_dotenv()

        return cls(
            llm_provider=os.getenv(
                "LLM_PROVIDER",
                "ollama",
            ).lower(),
        )
