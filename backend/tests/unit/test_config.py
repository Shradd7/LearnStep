import pytest
from pydantic import ValidationError

from classpath.core.config import Settings


def test_settings_accept_supported_embedding_contract() -> None:
    settings = Settings(
        database_url="postgresql+psycopg://user:password@localhost/database",
        embedding_dimension=384,
    )
    assert settings.embedding_dimension == 384


def test_settings_reject_model_dimension_mismatch() -> None:
    with pytest.raises(ValidationError, match="EMBEDDING_DIMENSION must be 384"):
        Settings(
            database_url="postgresql+psycopg://user:password@localhost/database",
            embedding_dimension=768,
        )


def test_settings_reject_non_postgresql_database() -> None:
    with pytest.raises(ValidationError, match="must use PostgreSQL"):
        Settings(database_url="sqlite:///local.db")


def test_settings_reject_debug_in_production() -> None:
    with pytest.raises(ValidationError, match="APP_DEBUG must be false"):
        Settings(
            app_env="production",
            app_debug=True,
            database_url="postgresql+psycopg://user:password@localhost/database",
        )


def test_settings_reject_wildcard_cors() -> None:
    with pytest.raises(ValidationError, match="explicit allowlist"):
        Settings(
            database_url="postgresql+psycopg://user:password@localhost/database",
            cors_origins=["*"],
        )
