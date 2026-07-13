import os
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient

from classpath.core.config import Settings
from classpath.main import create_app


@pytest.fixture
def settings() -> Settings:
    return Settings(
        app_env="test",
        database_url=os.getenv(
            "DATABASE_URL",
            "postgresql+psycopg://classpath:classpath_test@localhost:5432/classpath_test",
        ),
    )


@pytest.fixture
def client(settings: Settings) -> Generator[TestClient, None, None]:
    with TestClient(create_app(settings)) as test_client:
        yield test_client
