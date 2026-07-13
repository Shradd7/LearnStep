from collections.abc import Generator
from typing import cast
from unittest.mock import MagicMock

from fastapi import FastAPI
from fastapi.testclient import TestClient
from pytest import MonkeyPatch
from sqlalchemy.orm import Session

from classpath.api.dependencies import get_db_session
from classpath.services.health import ReadinessResult


def test_liveness_does_not_require_database(client: TestClient) -> None:
    response = client.get("/health/live")
    assert response.status_code == 200
    assert response.json() == {
        "status": "alive",
        "service": "LearnStep",
        "environment": "test",
    }


def test_development_frontend_origin_is_allowlisted(client: TestClient) -> None:
    response = client.options(
        "/health/live",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:5173"


def test_readiness_returns_safe_503_for_failed_dependency(
    client: TestClient, monkeypatch: MonkeyPatch
) -> None:
    app = cast(FastAPI, client.app)

    def override_session() -> Generator[Session, None, None]:
        yield MagicMock(spec=Session)

    app.dependency_overrides[get_db_session] = override_session
    monkeypatch.setattr(
        "classpath.api.health.check_readiness",
        lambda _session, _settings: ReadinessResult(
            ready=False,
            checks={"database": False, "pgvector": False, "vector_dimension": False},
        ),
    )
    response = client.get("/health/ready")
    assert response.status_code == 503
    assert response.json()["status"] == "not_ready"
    assert "database_url" not in response.text
