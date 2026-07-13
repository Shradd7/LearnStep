from pgvector.sqlalchemy import Vector
from sqlalchemy import CheckConstraint, Index, SmallInteger, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from classpath.db.base import Base
from classpath.models.common import CreatedAtMixin, UUIDPrimaryKeyMixin


class CurriculumConcept(UUIDPrimaryKeyMixin, CreatedAtMixin, Base):
    """Synthetic demo records only; no row claims reviewed curriculum status."""

    __tablename__ = "curriculum_concepts"
    __table_args__ = (
        CheckConstraint("class_level BETWEEN 5 AND 8", name="concept_class_level"),
        CheckConstraint("subject IN ('mathematics', 'science')", name="concept_subject"),
        CheckConstraint("review_status = 'synthetic_demo'", name="concept_demo_review"),
        CheckConstraint("source_type = 'synthetic_demo'", name="concept_demo_source"),
        Index(
            "ix_curriculum_concepts_scope",
            "class_level",
            "subject",
            "taxonomy_version",
            "review_status",
        ),
    )

    stable_key: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    class_level: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    subject: Mapped[str] = mapped_column(String(16), nullable=False)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    taxonomy_version: Mapped[str] = mapped_column(String(40), nullable=False)
    review_status: Mapped[str] = mapped_column(String(32), nullable=False)
    source_type: Mapped[str] = mapped_column(String(32), nullable=False)
    embedding: Mapped[list[float] | None] = mapped_column(Vector(384), nullable=True)
