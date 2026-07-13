import json
from importlib.resources import files
from typing import Any

from sqlalchemy.dialects.postgresql import insert

from classpath.core.config import get_settings
from classpath.db.session import get_session_factory
from classpath.models.curriculum import CurriculumConcept


def load_demo_records() -> list[dict[str, Any]]:
    fixture = files("classpath.fixtures").joinpath("demo_curriculum.json")
    payload = json.loads(fixture.read_text(encoding="utf-8"))
    records = payload["records"]
    if not isinstance(records, list):
        raise ValueError("Synthetic curriculum fixture must contain a records list")
    return records


def seed_demo_curriculum() -> int:
    settings = get_settings()
    records = load_demo_records()
    statement = insert(CurriculumConcept).values(records)
    statement = statement.on_conflict_do_update(
        index_elements=[CurriculumConcept.stable_key],
        set_={
            "class_level": statement.excluded.class_level,
            "subject": statement.excluded.subject,
            "name": statement.excluded.name,
            "description": statement.excluded.description,
            "taxonomy_version": statement.excluded.taxonomy_version,
            "review_status": statement.excluded.review_status,
            "source_type": statement.excluded.source_type,
        },
    )
    with get_session_factory(settings.database_url)() as session:
        session.execute(statement)
        session.commit()
    return len(records)


def main() -> None:
    count = seed_demo_curriculum()
    print(f"Seeded {count} explicitly synthetic_demo curriculum records.")


if __name__ == "__main__":
    main()
