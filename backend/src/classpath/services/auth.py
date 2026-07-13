from datetime import UTC, datetime, timedelta
from uuid import UUID

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from sqlalchemy import select
from sqlalchemy.orm import Session

from classpath.core.config import Settings
from classpath.models.profile import StudentProfile
from classpath.models.user import User

DEMO_ACCOUNTS = (
    ("math-demo@example.invalid", "Demo-Math-2026", 5, "mathematics"),
    ("science-demo@example.invalid", "Demo-Science-2026", 6, "science"),
)
JWT_ALGORITHM = "HS256"
PASSWORD_HASHER = PasswordHasher(time_cost=2, memory_cost=19456, parallelism=1)


def seed_demo_accounts(session: Session) -> None:
    """Idempotently create synthetic accounts; no real child information is used."""

    changed = False
    for email, password, class_level, subject in DEMO_ACCOUNTS:
        user = session.scalar(select(User).where(User.email == email))
        if user is None:
            user = User(
                email=email,
                password_hash=PASSWORD_HASHER.hash(password),
                is_demo=True,
                notice_version="demo-notice-v1",
            )
            session.add(user)
            session.flush()
            session.add(StudentProfile(user_id=user.id, class_level=class_level, subject=subject))
            changed = True
    if changed:
        session.commit()


def authenticate_demo(session: Session, email: str, password: str) -> User | None:
    user = session.scalar(
        select(User).where(User.email == email.casefold(), User.is_demo.is_(True))
    )
    if user is None:
        return None
    try:
        valid = PASSWORD_HASHER.verify(user.password_hash, password)
    except VerifyMismatchError:
        return None
    return user if valid else None


def create_access_token(*, user_id: UUID, settings: Settings) -> str:
    now = datetime.now(UTC)
    payload = {
        "sub": str(user_id),
        "iat": now,
        "exp": now + timedelta(minutes=settings.demo_token_minutes),
        "scope": "synthetic_demo",
    }
    return jwt.encode(
        payload, settings.demo_token_secret.get_secret_value(), algorithm=JWT_ALGORITHM
    )


def decode_access_token(*, token: str, settings: Settings) -> UUID | None:
    try:
        payload = jwt.decode(
            token, settings.demo_token_secret.get_secret_value(), algorithms=[JWT_ALGORITHM]
        )
        if payload.get("scope") != "synthetic_demo":
            return None
        return UUID(str(payload["sub"]))
    except (jwt.InvalidTokenError, KeyError, ValueError):
        return None
