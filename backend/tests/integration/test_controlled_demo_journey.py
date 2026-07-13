from __future__ import annotations

from datetime import UTC, datetime, timedelta
from pathlib import Path
from uuid import uuid4

import fitz
import pytest
from fastapi.testclient import TestClient

from classpath.core.config import Settings
from classpath.db.session import get_session_factory
from classpath.main import create_app
from classpath.models.demo import DemoDocument
from classpath.models.user import User
from classpath.repositories.demo import purge_expired_documents
from classpath.services.auth import PASSWORD_HASHER

pytestmark = pytest.mark.integration


def synthetic_fraction_pdf() -> bytes:
    document = fitz.open()
    page = document.new_page()
    page.insert_text(
        (72, 72),
        "CHAPTER: FRACTIONS\nDefinition: A fraction describes selected equal parts of a whole.\n"
        "Question: Which fraction names three parts out of four?",
    )
    data = bytes(document.tobytes())
    document.close()
    return data


def login(client: TestClient, email: str, password: str) -> str:
    response = client.post("/api/v1/demo/login", json={"email": email, "password": password})
    assert response.status_code == 200, response.text
    return str(response.json()["access_token"])


def test_upload_lesson_hint_feedback_progress_and_cross_user_isolation(
    settings: Settings, tmp_path: Path
) -> None:
    active_settings = Settings(
        app_env="test",
        database_url=settings.database_url,
        private_data_root=str(tmp_path),
        demo_token_secret=f"integration-{tmp_path.name}-{uuid4().hex}",
    )
    client = TestClient(create_app(active_settings))
    math_token = login(client, "math-demo@example.invalid", "Demo-Math-2026")
    science_token = login(client, "science-demo@example.invalid", "Demo-Science-2026")
    math_headers = {"Authorization": f"Bearer {math_token}"}
    science_headers = {"Authorization": f"Bearer {science_token}"}

    upload = client.post(
        "/api/v1/documents",
        headers=math_headers,
        data={"class_level": "5", "subject": "mathematics"},
        files={
            "file": ("../../synthetic-fractions.pdf", synthetic_fraction_pdf(), "application/pdf")
        },
    )
    assert upload.status_code == 201, upload.text
    document = upload.json()
    assert document["display_name"] == "synthetic-fractions.pdf"
    assert document["detected_concepts"] == ["fractions"]
    assert list(tmp_path.glob("*.pdf"))

    isolated = client.post(
        "/api/v1/retrieval/search",
        headers=science_headers,
        json={
            "document_ids": [document["id"]],
            "class_level": 5,
            "subject": "mathematics",
            "concept_keys": ["fractions"],
            "query": "equal fraction parts",
            "limit": 5,
        },
    )
    assert isolated.status_code == 200
    assert isolated.json() == []

    started = client.post(
        "/api/v1/demo/sessions",
        headers=math_headers,
        json={"package_key": "class5-math-fractions", "document_id": document["id"]},
    )
    assert started.status_code == 201, started.text
    session_data = started.json()
    assert session_data["evidence_chunk_ids"]
    assert "accepted_answer" not in session_data["question"]

    hint = client.post(
        f"/api/v1/demo/sessions/{session_data['session_id']}/hints/1", headers=math_headers
    )
    assert hint.status_code == 200
    assert hint.json()["answer_revealed"] is False

    attempt = client.post(
        f"/api/v1/demo/sessions/{session_data['session_id']}/attempts",
        headers=math_headers,
        json={"response": "3/4"},
    )
    assert attempt.status_code == 201, attempt.text
    assert attempt.json()["outcome"] == "correct"
    assert attempt.json()["hint_count"] == 1

    progress = client.get("/api/v1/demo/progress", headers=math_headers)
    assert progress.status_code == 200
    assert progress.json()["observations"][0]["attempts_observed"] >= 1
    assert "mastery" in progress.json()["limitation"]

    deleted = client.delete(f"/api/v1/documents/{document['id']}", headers=math_headers)
    assert deleted.status_code == 204
    assert not list(tmp_path.glob("*.pdf"))


def test_expiry_cleanup_removes_private_file_and_database_record(
    settings: Settings, tmp_path: Path
) -> None:
    storage_key = f"{uuid4().hex}.pdf"
    (tmp_path / storage_key).write_bytes(b"%PDF synthetic expired fixture")
    with get_session_factory(settings.database_url)() as session:
        user = User(
            email=f"expiry-{uuid4()}@example.invalid",
            password_hash=PASSWORD_HASHER.hash(str(uuid4())),
            is_demo=True,
            notice_version="test-only",
        )
        session.add(user)
        session.flush()
        document = DemoDocument(
            user_id=user.id,
            display_name="expired-synthetic.pdf",
            storage_key=storage_key,
            sha256=uuid4().hex + uuid4().hex,
            class_level=5,
            subject="mathematics",
            status="ready",
            extraction_pipeline_version="test-v1",
            expires_at=datetime.now(UTC) - timedelta(minutes=1),
        )
        session.add(document)
        session.commit()
        document_id = document.id

        assert purge_expired_documents(session, storage_root=tmp_path) == 1
        assert session.get(DemoDocument, document_id) is None
        assert not (tmp_path / storage_key).exists()
        session.delete(user)
        session.commit()
