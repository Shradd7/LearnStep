from dataclasses import dataclass

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from classpath.core.config import Settings


@dataclass(frozen=True, slots=True)
class ReadinessResult:
    ready: bool
    checks: dict[str, bool]


def check_readiness(session: Session, settings: Settings) -> ReadinessResult:
    """Check database, pgvector, and configured/schema dimension contracts."""

    checks = {"database": False, "pgvector": False, "vector_dimension": False}
    try:
        checks["database"] = session.scalar(text("SELECT 1")) == 1
        checks["pgvector"] = bool(
            session.scalar(
                text("SELECT EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'vector')")
            )
        )
        if checks["pgvector"]:
            schema_type = session.scalar(
                text(
                    """
                    SELECT format_type(attribute.atttypid, attribute.atttypmod)
                    FROM pg_attribute AS attribute
                    JOIN pg_class AS relation ON relation.oid = attribute.attrelid
                    JOIN pg_namespace AS namespace ON namespace.oid = relation.relnamespace
                    WHERE namespace.nspname = current_schema()
                      AND relation.relname = 'curriculum_concepts'
                      AND attribute.attname = 'embedding'
                      AND NOT attribute.attisdropped
                    """
                )
            )
            probe = "[" + ",".join("0" for _ in range(settings.embedding_dimension)) + "]"
            probe_dimension = session.scalar(
                text("SELECT vector_dims(CAST(:probe AS vector))"), {"probe": probe}
            )
            checks["vector_dimension"] = (
                schema_type == f"vector({settings.embedding_dimension})"
                and probe_dimension == settings.embedding_dimension
            )
    except SQLAlchemyError:
        session.rollback()
    return ReadinessResult(ready=all(checks.values()), checks=checks)
