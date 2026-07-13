"""Fail-fast HTTP smoke test for the controlled LearnStep user journey."""

from __future__ import annotations

import sys
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[1]
BASE_URL = "http://localhost:8000"


def require(response: httpx.Response, expected: int) -> dict[str, object]:
    if response.status_code != expected:
        raise RuntimeError(f"Unexpected HTTP {response.status_code}: {response.text[:300]}")
    if expected == 204:
        return {}
    payload = response.json()
    if not isinstance(payload, dict):
        raise RuntimeError("Expected a JSON object")
    return payload


def main() -> int:
    with httpx.Client(base_url=BASE_URL, timeout=30) as client:
        login = require(
            client.post(
                "/api/v1/demo/login",
                json={
                    "email": "math-demo@example.invalid",
                    "password": "Demo-Math-2026",
                },
            ),
            200,
        )
        headers = {"Authorization": f"Bearer {login['access_token']}"}
        sample = ROOT / "data" / "synthetic" / "samples" / "synthetic_chapter_01_fractions.pdf"
        with sample.open("rb") as handle:
            upload = require(
                client.post(
                    "/api/v1/documents",
                    headers=headers,
                    data={"class_level": "5", "subject": "mathematics"},
                    files={"file": (sample.name, handle, "application/pdf")},
                ),
                201,
            )
        try:
            session = require(
                client.post(
                    "/api/v1/demo/sessions",
                    headers=headers,
                    json={
                        "package_key": "class5-math-fractions",
                        "document_id": upload["id"],
                    },
                ),
                201,
            )
            require(
                client.post(
                    f"/api/v1/demo/sessions/{session['session_id']}/hints/1",
                    headers=headers,
                ),
                200,
            )
            attempt = require(
                client.post(
                    f"/api/v1/demo/sessions/{session['session_id']}/attempts",
                    headers=headers,
                    json={"response": "3/4"},
                ),
                201,
            )
            progress = require(client.get("/api/v1/demo/progress", headers=headers), 200)
            if attempt.get("outcome") != "correct" or not progress.get("observations"):
                raise RuntimeError("Journey completed without expected feedback/progress")
        finally:
            require(client.delete(f"/api/v1/documents/{upload['id']}", headers=headers), 204)
    print(
        "LearnStep demo journey passed: login -> upload -> lesson -> hint -> feedback -> "
        "progress -> delete"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (httpx.HTTPError, RuntimeError) as error:
        print(f"LearnStep demo journey failed: {error}", file=sys.stderr)
        raise SystemExit(1) from error
