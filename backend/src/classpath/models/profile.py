from enum import StrEnum
from uuid import UUID

from sqlalchemy import (
    CheckConstraint,
    ForeignKey,
    Index,
    SmallInteger,
    String,
    UniqueConstraint,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from classpath.db.base import Base
from classpath.models.common import CreatedAtMixin, UUIDPrimaryKeyMixin


class Subject(StrEnum):
    MATHEMATICS = "mathematics"
    SCIENCE = "science"


class StudentProfile(UUIDPrimaryKeyMixin, CreatedAtMixin, Base):
    __tablename__ = "student_profiles"
    __table_args__ = (
        CheckConstraint("class_level BETWEEN 5 AND 8", name="profile_class_level"),
        CheckConstraint("subject IN ('mathematics', 'science')", name="profile_subject"),
        UniqueConstraint("user_id", name="uq_student_profiles_user_id"),
        Index("ix_student_profiles_user_id", "user_id"),
    )

    user_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    class_level: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    subject: Mapped[str] = mapped_column(String(16), nullable=False)
    user: Mapped["User"] = relationship(back_populates="student_profile")


from classpath.models.user import User  # noqa: E402
