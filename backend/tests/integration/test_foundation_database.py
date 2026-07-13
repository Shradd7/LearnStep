from uuid import uuid4

import pytest
from sqlalchemy import delete, func, inspect, select, text

from classpath.core.config import get_settings
from classpath.db.session import get_engine, get_session_factory
from classpath.models.curriculum import CurriculumConcept
from classpath.models.profile import StudentProfile, Subject
from classpath.models.user import User
from classpath.scripts.seed_demo_curriculum import seed_demo_curriculum
from classpath.services.auth import PASSWORD_HASHER
from classpath.services.health import check_readiness

pytestmark = pytest.mark.integration


def test_migrated_schema_has_pgvector_and_expected_dimension() -> None:
    settings = get_settings()
    engine = get_engine(settings.database_url)
    assert {"users", "student_profiles", "curriculum_concepts"}.issubset(
        set(inspect(engine).get_table_names())
    )
    with get_session_factory(settings.database_url)() as session:
        result = check_readiness(session, settings)
    assert result.ready is True
    assert result.checks == {"database": True, "pgvector": True, "vector_dimension": True}


def test_profile_has_enforceable_owner_and_database_cascade() -> None:
    settings = get_settings()
    email = f"synthetic-{uuid4()}@example.invalid"
    with get_session_factory(settings.database_url)() as session:
        user = User(email=email, password_hash=PASSWORD_HASHER.hash(str(uuid4())))
        user.student_profile = StudentProfile(class_level=5, subject=Subject.MATHEMATICS)
        session.add(user)
        session.commit()
        user_id = user.id
        profile_id = user.student_profile.id

        session.execute(delete(User).where(User.id == user_id))
        session.commit()
        assert session.scalar(select(StudentProfile).where(StudentProfile.id == profile_id)) is None
        remaining_users = session.scalar(
            text("SELECT count(*) FROM users WHERE email = :email"), {"email": email}
        )
        assert remaining_users == 0


def test_synthetic_demo_seed_is_idempotent() -> None:
    settings = get_settings()
    assert seed_demo_curriculum() == 4
    assert seed_demo_curriculum() == 4
    with get_session_factory(settings.database_url)() as session:
        count = session.scalar(
            select(func.count())
            .select_from(CurriculumConcept)
            .where(CurriculumConcept.review_status == "synthetic_demo")
        )
    assert count == 4
