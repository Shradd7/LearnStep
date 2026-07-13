from functools import lru_cache
from typing import Literal, Self

from pydantic import Field, SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

SUPPORTED_EMBEDDING_DIMENSIONS = {"sentence-transformers/all-MiniLM-L6-v2": 384}


class Settings(BaseSettings):
    """Validated process configuration loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"), env_file_encoding="utf-8", extra="ignore", frozen=True
    )

    app_name: str = Field(default="LearnStep", min_length=1, max_length=100)
    app_env: Literal["development", "test", "production"] = "development"
    app_debug: bool = False
    database_url: str = "postgresql+psycopg://classpath:classpath_dev@localhost:5432/classpath"
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    embedding_dimension: int = Field(default=384, gt=0, le=4096)
    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:5173"])
    demo_token_secret: SecretStr = SecretStr("local-demo-secret-change-before-deployment")
    demo_token_minutes: int = Field(default=60, ge=5, le=1440)
    private_data_root: str = "uploads"
    upload_max_bytes: int = Field(default=5_000_000, ge=1_000, le=10_000_000)
    upload_max_pages: int = Field(default=10, ge=1, le=20)
    upload_min_text_chars: int = Field(default=40, ge=1, le=10_000)
    demo_upload_ttl_minutes: int = Field(default=60, ge=5, le=1440)

    @model_validator(mode="after")
    def validate_runtime_contracts(self) -> Self:
        if not self.database_url.startswith("postgresql+psycopg://"):
            raise ValueError("DATABASE_URL must use PostgreSQL with the psycopg driver")
        expected = SUPPORTED_EMBEDDING_DIMENSIONS.get(self.embedding_model)
        if expected is None:
            raise ValueError("EMBEDDING_MODEL is not supported by this application version")
        if self.embedding_dimension != expected:
            raise ValueError(f"EMBEDDING_DIMENSION must be {expected} for {self.embedding_model}")
        if self.app_env == "production" and self.app_debug:
            raise ValueError("APP_DEBUG must be false in production")
        if self.app_env == "production" and self.demo_token_secret.get_secret_value() == (
            "local-demo-secret-change-before-deployment"
        ):
            raise ValueError("DEMO_TOKEN_SECRET must be changed in production")
        if not self.cors_origins or "*" in self.cors_origins:
            raise ValueError("CORS_ORIGINS must be a non-empty explicit allowlist")
        if any(not origin.startswith(("http://", "https://")) for origin in self.cors_origins):
            raise ValueError("Every CORS origin must use http or https")
        return self


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
