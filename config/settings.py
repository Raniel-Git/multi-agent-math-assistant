import os
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    """Stores application configuration loaded from environment variables.

    Attributes:
        llm_provider: Language model provider used by the application.
        api_title: Title displayed in the API documentation.
        api_description: Description displayed in the API documentation.
        api_version: Current API version.
        api_host: Host used to run the API.
        api_port: Port used to run the API.
        cors_allowed_origins: Origins allowed to access the API.
    """

    llm_provider: str = "ollama"
    api_title: str = "Multi-Agent Math Assistant API"
    api_description: str = (
        "REST API for processing mathematical and conversational "
        "requests through specialized agents."
    )
    api_version: str = "1.0.0"
    api_host: str = "127.0.0.1"
    api_port: int = 8000
    cors_allowed_origins: tuple[str, ...] = (
        "http://localhost:3000",
    )

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
                cls.llm_provider,
            ).lower(),
            api_title=os.getenv(
                "API_TITLE",
                cls.api_title,
            ),
            api_description=os.getenv(
                "API_DESCRIPTION",
                cls.api_description,
            ),
            api_version=os.getenv(
                "API_VERSION",
                cls.api_version,
            ),
            api_host=os.getenv(
                "API_HOST",
                cls.api_host,
            ),
            api_port=int(
                os.getenv(
                    "API_PORT",
                    str(cls.api_port),
                ),
            ),
            cors_allowed_origins=cls._parse_origins(
                os.getenv(
                    "CORS_ALLOWED_ORIGINS",
                    ",".join(cls.cors_allowed_origins),
                ),
            ),
        )

    @staticmethod
    def _parse_origins(
        origins: str,
    ) -> tuple[str, ...]:
        return tuple(
            origin.strip()
            for origin in origins.split(",")
            if origin.strip()
        )
