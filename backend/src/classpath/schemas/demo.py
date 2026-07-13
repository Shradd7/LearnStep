from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


class DemoLoginRequest(BaseModel):
    email: str = Field(min_length=3, max_length=320)
    password: str = Field(min_length=8, max_length=128)


class DemoProfileResponse(BaseModel):
    class_level: int
    subject: str


class DemoLoginResponse(BaseModel):
    access_token: str
    token_type: Literal["bearer"]
    expires_in_seconds: int
    account_label: str
    profile: DemoProfileResponse
    notice_version: str
    limitations: list[str]


class DemoSource(BaseModel):
    source_id: str
    label: str
    page: int


class DemoChapterResponse(BaseModel):
    package_key: str
    title: str
    class_level: int
    subject: str
    concept_key: str
    review_status: str
    source: DemoSource
    confidence: str


class DemoDocumentResponse(BaseModel):
    id: UUID
    display_name: str
    class_level: int
    subject: str
    status: str
    expires_at: datetime
    detected_concepts: list[str]
    chunk_count: int
    extraction_pipeline_version: str


class RetrievalRequest(BaseModel):
    document_ids: list[UUID] = Field(min_length=1, max_length=10)
    class_level: int = Field(ge=5, le=8)
    subject: Literal["mathematics", "science"]
    concept_keys: list[str] = Field(min_length=1, max_length=10)
    content_types: list[str] | None = None
    query: str = Field(min_length=2, max_length=300)
    limit: int = Field(default=5, ge=1, le=20)


class RetrievedChunkResponse(BaseModel):
    chunk_id: UUID
    document_id: UUID
    page_number: int
    content_type: str
    concept_key: str | None
    text: str
    embedding_version: str


class StartSessionRequest(BaseModel):
    package_key: str = Field(min_length=3, max_length=100)
    document_id: UUID | None = None


class LessonContent(BaseModel):
    goal: str
    prerequisites: str
    explanation: str
    example: str
    recap: str


class DemoQuestion(BaseModel):
    question_key: str
    text: str
    answer_type: str
    options: list[str]
    cognitive_level: str
    difficulty: str


class StartSessionResponse(BaseModel):
    session_id: UUID
    package_key: str
    title: str
    review_status: str
    confidence: str
    lesson: LessonContent
    question: DemoQuestion
    source: DemoSource
    evidence_chunk_ids: list[UUID]
    known_limitations: list[str]


class HintResponse(BaseModel):
    session_id: UUID
    level: int
    hint: str
    answer_revealed: Literal[False] = False


class AttemptRequest(BaseModel):
    response: str = Field(min_length=1, max_length=500)


class AttemptResponse(BaseModel):
    attempt_id: UUID
    outcome: str
    confidence: str
    feedback: str
    explanation: str
    accepted_answer: str
    features: dict[str, object]
    hint_count: int


class ProgressObservation(BaseModel):
    concept_key: str
    attempts_observed: int
    correct_observations: int
    supported_observations: int
    next_action: str


class ProgressResponse(BaseModel):
    policy_version: str
    observations: list[ProgressObservation]
    limitation: str
