"""Create the initial LearnStep schema.

Revision ID: 20260713_0001
Revises: None
"""

from collections.abc import Sequence

import sqlalchemy as sa
from pgvector.sqlalchemy import Vector

from alembic import op

revision: str = "20260713_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_users")),
        sa.UniqueConstraint("email", name=op.f("uq_users_email")),
    )

    op.create_table(
        "student_profiles",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("class_level", sa.SmallInteger(), nullable=False),
        sa.Column("subject", sa.String(length=16), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.CheckConstraint("class_level BETWEEN 5 AND 8", name="profile_class_level"),
        sa.CheckConstraint("subject IN ('mathematics', 'science')", name="profile_subject"),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_student_profiles_user_id_users"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_student_profiles")),
        sa.UniqueConstraint("user_id", name=op.f("uq_student_profiles_user_id")),
    )
    op.create_index("ix_student_profiles_user_id", "student_profiles", ["user_id"])

    op.create_table(
        "curriculum_concepts",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("stable_key", sa.String(length=100), nullable=False),
        sa.Column("class_level", sa.SmallInteger(), nullable=False),
        sa.Column("subject", sa.String(length=16), nullable=False),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("taxonomy_version", sa.String(length=40), nullable=False),
        sa.Column("review_status", sa.String(length=32), nullable=False),
        sa.Column("source_type", sa.String(length=32), nullable=False),
        sa.Column("embedding", Vector(384), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.CheckConstraint("class_level BETWEEN 5 AND 8", name="concept_class_level"),
        sa.CheckConstraint("subject IN ('mathematics', 'science')", name="concept_subject"),
        sa.CheckConstraint("review_status = 'synthetic_demo'", name="concept_demo_review"),
        sa.CheckConstraint("source_type = 'synthetic_demo'", name="concept_demo_source"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_curriculum_concepts")),
        sa.UniqueConstraint("stable_key", name=op.f("uq_curriculum_concepts_stable_key")),
    )
    op.create_index(
        "ix_curriculum_concepts_scope",
        "curriculum_concepts",
        ["class_level", "subject", "taxonomy_version", "review_status"],
    )


def downgrade() -> None:
    op.drop_index("ix_curriculum_concepts_scope", table_name="curriculum_concepts")
    op.drop_table("curriculum_concepts")
    op.drop_index("ix_student_profiles_user_id", table_name="student_profiles")
    op.drop_table("student_profiles")
    op.drop_table("users")
    op.execute("DROP EXTENSION IF EXISTS vector")
