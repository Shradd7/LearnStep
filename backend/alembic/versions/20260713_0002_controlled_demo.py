"""Add controlled synthetic demo records.

Revision ID: 20260713_0002
Revises: 20260713_0001
"""

from collections.abc import Sequence

import sqlalchemy as sa
from pgvector.sqlalchemy import Vector

from alembic import op

revision: str = "20260713_0002"
down_revision: str | None = "20260713_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("users", sa.Column("password_hash", sa.String(255), nullable=True))
    op.add_column(
        "users", sa.Column("is_demo", sa.Boolean(), nullable=False, server_default=sa.true())
    )
    op.add_column(
        "users",
        sa.Column("notice_version", sa.String(40), nullable=False, server_default="demo-notice-v1"),
    )
    op.execute(
        "UPDATE users SET password_hash = 'demo-account-reset-required' WHERE password_hash IS NULL"
    )
    op.alter_column("users", "password_hash", nullable=False)
    op.create_table(
        "demo_documents",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("display_name", sa.String(160), nullable=False),
        sa.Column("storage_key", sa.String(80), nullable=False),
        sa.Column("sha256", sa.String(64), nullable=False),
        sa.Column("class_level", sa.SmallInteger(), nullable=False),
        sa.Column("subject", sa.String(16), nullable=False),
        sa.Column("status", sa.String(16), nullable=False),
        sa.Column("extraction_pipeline_version", sa.String(40), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.CheckConstraint("class_level BETWEEN 5 AND 8", name="demo_document_class_level"),
        sa.CheckConstraint("subject IN ('mathematics', 'science')", name="demo_document_subject"),
        sa.CheckConstraint("status IN ('ready', 'failed')", name="demo_document_status"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("storage_key"),
    )
    op.create_index("ix_demo_documents_owner_expiry", "demo_documents", ["user_id", "expires_at"])
    op.create_table(
        "demo_document_chunks",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("document_id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("class_level", sa.SmallInteger(), nullable=False),
        sa.Column("subject", sa.String(16), nullable=False),
        sa.Column("concept_key", sa.String(100), nullable=True),
        sa.Column("content_type", sa.String(32), nullable=False),
        sa.Column("page_number", sa.Integer(), nullable=False),
        sa.Column("chunk_index", sa.Integer(), nullable=False),
        sa.Column("original_text", sa.Text(), nullable=False),
        sa.Column("text_hash", sa.String(64), nullable=False),
        sa.Column("embedding_model", sa.String(80), nullable=False),
        sa.Column("embedding_version", sa.String(40), nullable=False),
        sa.Column("embedding", Vector(384), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.CheckConstraint("class_level BETWEEN 5 AND 8", name="demo_chunk_class_level"),
        sa.CheckConstraint("subject IN ('mathematics', 'science')", name="demo_chunk_subject"),
        sa.ForeignKeyConstraint(["document_id"], ["demo_documents.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_demo_chunks_retrieval_scope",
        "demo_document_chunks",
        ["user_id", "document_id", "class_level", "subject", "concept_key"],
    )
    op.create_table(
        "demo_learning_sessions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("document_id", sa.Uuid(), nullable=True),
        sa.Column("package_key", sa.String(100), nullable=False),
        sa.Column("concept_key", sa.String(100), nullable=False),
        sa.Column("lesson_template_version", sa.String(40), nullable=False),
        sa.Column("hint_count", sa.SmallInteger(), nullable=False, server_default="0"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["document_id"], ["demo_documents.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_demo_sessions_owner_created", "demo_learning_sessions", ["user_id", "created_at"]
    )
    op.create_table(
        "demo_attempts",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("session_id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("question_key", sa.String(100), nullable=False),
        sa.Column("response_text", sa.Text(), nullable=False),
        sa.Column("outcome", sa.String(24), nullable=False),
        sa.Column("evaluation_features", sa.JSON(), nullable=False),
        sa.Column("rubric_version", sa.String(40), nullable=False),
        sa.Column("confidence", sa.String(16), nullable=False),
        sa.Column("hint_count", sa.SmallInteger(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.CheckConstraint("hint_count BETWEEN 0 AND 2", name="demo_attempt_hint_count"),
        sa.ForeignKeyConstraint(["session_id"], ["demo_learning_sessions.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_demo_attempts_owner_session", "demo_attempts", ["user_id", "session_id"])


def downgrade() -> None:
    op.drop_table("demo_attempts")
    op.drop_table("demo_learning_sessions")
    op.drop_table("demo_document_chunks")
    op.drop_table("demo_documents")
    op.drop_column("users", "notice_version")
    op.drop_column("users", "is_demo")
    op.drop_column("users", "password_hash")
