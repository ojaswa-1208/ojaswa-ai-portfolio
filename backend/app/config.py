
from functools import lru_cache

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "Ojaswa AI Portfolio Assistant"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"

    # Groq configuration
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "openai/gpt-oss-120b"

    # Frontend configuration
    FRONTEND_URL: str = "http://localhost:3000"

    # API configuration
    API_PREFIX: str = "/api/v1"
    LOG_LEVEL: str = "INFO"
    RATE_LIMIT: str = "60/minute"

    # Qdrant Cloud configuration
    QDRANT_URL: str = ""
    QDRANT_API_KEY: str = ""
    QDRANT_TIMEOUT_SECONDS: int = 15
    QDRANT_COLLECTION: str = "ojaswa_portfolio"

    # Embedding configuration
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    EMBEDDING_DIMENSION: int = 384

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    @field_validator("ENVIRONMENT")
    @classmethod
    def validate_environment(cls, value: str) -> str:
        allowed = {"development", "testing", "production"}

        if value not in allowed:
            raise ValueError(
                f"ENVIRONMENT must be one of {allowed}"
            )

        return value

    @field_validator("LOG_LEVEL")
    @classmethod
    def validate_log_level(cls, value: str) -> str:
        allowed = {
            "DEBUG",
            "INFO",
            "WARNING",
            "ERROR",
            "CRITICAL",
        }

        value = value.upper()

        if value not in allowed:
            raise ValueError("Invalid LOG_LEVEL")

        return value

    @field_validator("EMBEDDING_DIMENSION")
    @classmethod
    def validate_embedding_dimension(cls, value: int) -> int:
        if value != 384:
            raise ValueError(
                "all-MiniLM-L6-v2 requires 384 dimensions"
            )

        return value

    @field_validator("QDRANT_URL")
    @classmethod
    def validate_qdrant_url(cls, value: str) -> str:
        value = value.strip().rstrip("/")

        if value and not value.startswith("https://"):
            raise ValueError(
                "QDRANT_URL must use HTTPS"
            )

        return value

    @model_validator(mode="after")
    def validate_qdrant_credentials(self):
        if not self.QDRANT_URL or not self.QDRANT_API_KEY:
            raise ValueError(
                "QDRANT_URL and QDRANT_API_KEY are required."
            )

        if self.QDRANT_TIMEOUT_SECONDS <= 0:
            raise ValueError(
                "QDRANT_TIMEOUT_SECONDS must be positive."
            )

        return self

    @property
    def allowed_origins(self) -> list[str]:
        return [
            origin.strip().rstrip("/")
            for origin in self.FRONTEND_URL.split(",")
            if origin.strip()
        ]


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
