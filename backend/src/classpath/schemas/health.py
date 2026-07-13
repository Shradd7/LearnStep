from typing import Literal

from pydantic import BaseModel, ConfigDict


class LiveResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: Literal["alive"]
    service: str
    environment: str


class ReadyResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: Literal["ready", "not_ready"]
    checks: dict[str, bool]
    embedding_model: str
    embedding_dimension: int
