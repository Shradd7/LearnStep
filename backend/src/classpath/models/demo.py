from datetime import datetime
from uuid import UUID

from pgvector.sqlalchemy import Vector
from sqlalchemy import (
    JSON,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    SmallInteger,
    String,
    Text,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column

from classpath.db.base import Base
from classpath.models.common import CreatedAtMixin, UUIDPrimaryKeyMixin


class DemoDocument(UUIDPrimaryKeyMixin, CreatedAtMixin, Base):
    __tablename__ = "demo_documents"
    __table_args__ = (
        CheckConstraint("class_level BETWEEN 5 AND 8", name="demo_document_class_level"),
        CheckConstraint("subject IN ('mathematics', 'science')", name="demo_document_subject"),
        CheckConstraint("status IN ('ready', 'failed')", name="demo_document_status"),
        Index("ix_demo_documents_owner_expiry", "user_id", "expires_at"),
    )

    user_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    display_name: Mapped[str] = mapped_column(String(160), nullable=False)
    storage_key: Mapped[str] = mapped_column(String(80), nullable=False, unique=True)
    sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    class_level: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    subject: Mapped[str] = mapped_column(String(16), nullable=False)
    status: Mapped[str] = mapped_column(String(16), nullable=False)
    extraction_pipeline_version: Mapped[str] = mapped_column(String(40), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class DemoDocumentChunk(UUIDPrimaryKeyMixin, CreatedAtMixin, Base):
    __tablename__ = "demo_document_chunks"
    __table_args__ = (
        CheckConstraint("class_level BETWEEN 5 AND 8", name="demo_chunk_class_level"),
        CheckConstraint("subject IN ('mathematics', 'science')", name="demo_chunk_subject"),
        Index(
            "ix_demo_chunks_retrieval_scope",
            "user_id",
            "document_id",
            "class_level",
            "subject",
            "concept_key",
        ),
    )

    document_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("demo_documents.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    class_level: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    subject: Mapped[str] = mapped_column(String(16), nullable=False)
    concept_key: Mapped[str | None] = mapped_column(String(100), nullable=True)
    content_type: Mapped[str] = mapped_column(String(32), nullable=False)
    page_number: Mapped[int] = mapped_column(Integer, nullable=False)
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    original_text: Mapped[str] = mapped_column(Text, nullable=False)
    text_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    embedding_model: Mapped[str] = mapped_column(String(80), nullable=False)
    embedding_version: Mapped[str] = mapped_column(String(40), nullable=False)
    embedding: Mapped[list[float]] = mapped_column(Vector(384), nullable=False)


class DemoLearningSession(UUIDPrimaryKeyMixin, CreatedAtMixin, Base):
    __tablename__ = "demo_learning_sessions"
    __table_args__ = (Index("ix_demo_sessions_owner_created", "user_id", "created_at"),)

    user_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    document_id: Mapped[UUID | None] = mapped_column(
        Uuid, ForeignKey("demo_documents.id", ondelete="SET NULL"), nullable=True
    )
    package_key: Mapped[str] = mapped_column(String(100), nullable=False)
    concept_key: Mapped[str] = mapped_column(String(100), nullable=False)
    lesson_template_version: Mapped[str] = mapped_column(String(40), nullable=False)
    hint_count: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=0)


class DemoAttempt(UUIDPrimaryKeyMixin, CreatedAtMixin, Base):
    __tablename__ = "demo_attempts"
    __table_args__ = (
        CheckConstraint("hint_count BETWEEN 0 AND 2", name="demo_attempt_hint_count"),
        Index("ix_demo_attempts_owner_session", "user_id", "session_id"),
    )

    session_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("demo_learning_sessions.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    question_key: Mapped[str] = mapped_column(String(100), nullable=False)
    response_text: Mapped[str] = mapped_column(Text, nullable=False)
    outcome: Mapped[str] = mapped_column(String(24), nullable=False)
    evaluation_features: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False)
    rubric_version: Mapped[str] = mapped_column(String(40), nullable=False)
    confidence: Mapped[str] = mapped_column(String(16), nullable=False)
    hint_count: Mapped[int] = mapped_column(SmallInteger, nullable=False)
