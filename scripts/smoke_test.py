"""Fail-fast LearnStep API health smoke check using the Python standard library."""

import json
import os
import sys
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import urlopen


def get_json(url: str) -> dict[str, Any]:
    with urlopen(url, timeout=5) as response:  # noqa: S310 - fixed operator-provided URL
        payload = json.load(response)
    if not isinstance(payload, dict):
        raise ValueError(f"Expected a JSON object from {url}")
    return payload


def main() -> int:
    base_url = os.environ.get("SMOKE_BASE_URL", "http://localhost:8000").rstrip("/")
    try:
        live = get_json(f"{base_url}/health/live")
        ready = get_json(f"{base_url}/health/ready")
    except (HTTPError, URLError, TimeoutError, ValueError, json.JSONDecodeError) as error:
        print(f"Smoke check failed: {error}", file=sys.stderr)
        return 1
    if live.get("status") != "alive":
        print("Smoke check failed: liveness contract mismatch", file=sys.stderr)
        return 1
    required_checks = {"database", "pgvector", "vector_dimension"}
    checks = ready.get("checks")
    if ready.get("status") != "ready" or not isinstance(checks, dict):
        print("Smoke check failed: readiness contract mismatch", file=sys.stderr)
        return 1
    if not required_checks.issubset(checks) or not all(
        checks.get(key) is True for key in required_checks
    ):
        print("Smoke check failed: one or more readiness dependencies failed", file=sys.stderr)
        return 1
    if ready.get("embedding_dimension") != 384:
        print("Smoke check failed: embedding dimension mismatch", file=sys.stderr)
        return 1
    print("Smoke check passed: API, PostgreSQL, pgvector, and vector dimension are ready.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
