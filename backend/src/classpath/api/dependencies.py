from collections.abc import Generator
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from classpath.core.config import Settings, get_settings
from classpath.db.session import get_session_factory
from classpath.models.user import User
from classpath.services.auth import decode_access_token

bearer_scheme = HTTPBearer(auto_error=False)


def get_db_session(
    settings: Annotated[Settings, Depends(get_settings)],
) -> Generator[Session, None, None]:
    """Provide a request-scoped session using the app factory's active settings."""

    with get_session_factory(settings.database_url)() as session:
        yield session


def get_current_demo_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    session: Annotated[Session, Depends(get_db_session)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> User:
    if credentials is None or credentials.scheme.casefold() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Demo sign-in required"
        )
    user_id = decode_access_token(token=credentials.credentials, settings=settings)
    user = (
        session.scalar(select(User).where(User.id == user_id, User.is_demo.is_(True)))
        if user_id
        else None
    )
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid demo token")
    return user
