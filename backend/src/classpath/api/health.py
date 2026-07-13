from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from classpath.api.dependencies import get_db_session
from classpath.core.config import Settings, get_settings
from classpath.schemas.health import LiveResponse, ReadyResponse
from classpath.services.health import check_readiness

router = APIRouter(tags=["health"])


@router.get("/health/live", response_model=LiveResponse)
def live(settings: Annotated[Settings, Depends(get_settings)]) -> LiveResponse:
    return LiveResponse(status="alive", service=settings.app_name, environment=settings.app_env)


@router.get(
    "/health/ready",
    response_model=ReadyResponse,
    responses={status.HTTP_503_SERVICE_UNAVAILABLE: {"model": ReadyResponse}},
)
def ready(
    session: Annotated[Session, Depends(get_db_session)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> ReadyResponse | JSONResponse:
    result = check_readiness(session, settings)
    response = ReadyResponse(
        status="ready" if result.ready else "not_ready",
        checks=result.checks,
        embedding_model=settings.embedding_model,
        embedding_dimension=settings.embedding_dimension,
    )
    if not result.ready:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, content=response.model_dump()
        )
    return response
