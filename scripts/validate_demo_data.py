"""Validate that bundled curriculum metadata is explicitly synthetic."""

import json
from pathlib import Path

ALLOWED_CLASSES = {5, 6, 7, 8}
ALLOWED_SUBJECTS = {"mathematics", "science"}


def main() -> int:
    path = Path("backend/src/classpath/fixtures/demo_curriculum.json")
    payload = json.loads(path.read_text(encoding="utf-8"))
    records = payload.get("records")
    if not isinstance(records, list) or not 1 <= len(records) <= 8:
        raise ValueError("demo curriculum must contain between one and eight records")
    stable_keys: set[str] = set()
    for record in records:
        if not isinstance(record, dict):
            raise ValueError("each demo record must be an object")
        if record.get("review_status") != "synthetic_demo":
            raise ValueError("every demo record must be marked synthetic_demo")
        if record.get("source_type") != "synthetic_demo":
            raise ValueError("every demo record must have synthetic_demo source_type")
        if record.get("class_level") not in ALLOWED_CLASSES:
            raise ValueError("demo record has an unsupported class")
        if record.get("subject") not in ALLOWED_SUBJECTS:
            raise ValueError("demo record has an unsupported subject")
        stable_key = record.get("stable_key")
        if not isinstance(stable_key, str) or stable_key in stable_keys:
            raise ValueError("demo record stable keys must be non-empty and unique")
        stable_keys.add(stable_key)
    print(f"Validated {len(records)} synthetic_demo curriculum records; no real source data used.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
