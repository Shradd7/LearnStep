from datetime import UTC, datetime, timedelta
from decimal import Decimal
from pathlib import Path
from typing import Annotated, Any
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from classpath.api.dependencies import get_current_demo_user, get_db_session
from classpath.core.config import Settings, get_settings
from classpath.models.demo import DemoAttempt, DemoDocument, DemoDocumentChunk, DemoLearningSession
from classpath.models.user import User
from classpath.repositories.demo import (
    get_owned_document,
    purge_expired_documents,
    search_student_chunks,
)
from classpath.schemas.demo import (
    AttemptRequest,
    AttemptResponse,
    DemoChapterResponse,
    DemoDocumentResponse,
    DemoLoginRequest,
    DemoLoginResponse,
    DemoProfileResponse,
    HintResponse,
    ProgressObservation,
    ProgressResponse,
    RetrievalRequest,
    RetrievedChunkResponse,
    StartSessionRequest,
    StartSessionResponse,
)
from classpath.services.assessment.evaluator import QuestionSnapshot, evaluate_attempt
from classpath.services.auth import authenticate_demo, create_access_token, seed_demo_accounts
from classpath.services.demo_content import get_demo_package, load_demo_packages
from classpath.services.nlp.extraction import (
    PdfValidationError,
    detect_content_blocks,
    validate_and_extract_pdf,
)
from classpath.services.retrieval.hashing import (
    HASH_EMBEDDING_MODEL,
    HASH_EMBEDDING_VERSION,
    hash_embedding,
)
from classpath.services.storage import delete_pdf, safe_display_name, store_pdf

router = APIRouter(prefix="/api/v1", tags=["controlled-demo"])
BEARER_SCHEME = "bearer"


@router.post("/demo/login", response_model=DemoLoginResponse)
def login_demo(
    request: DemoLoginRequest,
    session: Annotated[Session, Depends(get_db_session)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> DemoLoginResponse:
    seed_demo_accounts(session)
    user = authenticate_demo(session, request.email, request.password)
    if user is None or user.student_profile is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid demo credentials"
        )
    return DemoLoginResponse(
        access_token=create_access_token(user_id=user.id, settings=settings),
        token_type=BEARER_SCHEME,
        expires_in_seconds=settings.demo_token_minutes * 60,
        account_label="Synthetic mathematics demo"
        if user.student_profile.subject == "mathematics"
        else "Synthetic science demo",
        profile=DemoProfileResponse(
            class_level=user.student_profile.class_level, subject=user.student_profile.subject
        ),
        notice_version=user.notice_version,
        limitations=[
            "Use only synthetic sample content; do not enter real child information.",
            "Content is a portfolio demonstration, not reviewed or endorsed curriculum.",
            f"Uploads expire automatically after {settings.demo_upload_ttl_minutes} minutes.",
        ],
    )


@router.get("/demo/chapters", response_model=list[DemoChapterResponse])
def list_chapters(user: Annotated[User, Depends(get_current_demo_user)]) -> list[dict[str, Any]]:
    profile = user.student_profile
    if profile is None:
        return []
    keys = set(DemoChapterResponse.model_fields)
    return [
        {key: value for key, value in package.items() if key in keys}
        for package in load_demo_packages()
        if package["class_level"] == profile.class_level and package["subject"] == profile.subject
    ]


def _document_response(session: Session, document: DemoDocument) -> DemoDocumentResponse:
    chunks = list(
        session.scalars(
            select(DemoDocumentChunk).where(DemoDocumentChunk.document_id == document.id)
        )
    )
    return DemoDocumentResponse(
        id=document.id,
        display_name=document.display_name,
        class_level=document.class_level,
        subject=document.subject,
        status=document.status,
        expires_at=document.expires_at,
        detected_concepts=sorted({chunk.concept_key for chunk in chunks if chunk.concept_key}),
        chunk_count=len(chunks),
        extraction_pipeline_version=document.extraction_pipeline_version,
    )


@router.post("/documents", response_model=DemoDocumentResponse, status_code=status.HTTP_201_CREATED)
def upload_document(
    user: Annotated[User, Depends(get_current_demo_user)],
    session: Annotated[Session, Depends(get_db_session)],
    settings: Annotated[Settings, Depends(get_settings)],
    file: Annotated[UploadFile, File()],
    class_level: Annotated[int, Form(ge=5, le=8)],
    subject: Annotated[str, Form(pattern="^(mathematics|science)$")],
) -> DemoDocumentResponse:
    profile = user.student_profile
    if profile is None or profile.class_level != class_level or profile.subject != subject:
        raise HTTPException(status_code=403, detail="Upload context must match the demo profile")
    purge_expired_documents(session, storage_root=Path(settings.private_data_root))
    data = file.file.read(settings.upload_max_bytes + 1)
    try:
        extracted = validate_and_extract_pdf(
            data=data,
            filename=file.filename or "upload",
            content_type=file.content_type or "",
            max_bytes=settings.upload_max_bytes,
            max_pages=settings.upload_max_pages,
            min_text_chars=settings.upload_min_text_chars,
        )
    except PdfValidationError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    duplicate = session.scalar(
        select(DemoDocument).where(
            DemoDocument.user_id == user.id,
            DemoDocument.sha256 == extracted.sha256,
            DemoDocument.expires_at > datetime.now(UTC),
        )
    )
    if duplicate is not None:
        raise HTTPException(status_code=409, detail="This demo PDF is already active")
    storage_key = store_pdf(root=Path(settings.private_data_root), data=data)
    try:
        document = DemoDocument(
            user_id=user.id,
            display_name=safe_display_name(file.filename or "demo-upload.pdf"),
            storage_key=storage_key,
            sha256=extracted.sha256,
            class_level=class_level,
            subject=subject,
            status="ready",
            extraction_pipeline_version=extracted.pipeline_version,
            expires_at=datetime.now(UTC) + timedelta(minutes=settings.demo_upload_ttl_minutes),
        )
        session.add(document)
        session.flush()
        for block in detect_content_blocks(extracted):
            session.add(
                DemoDocumentChunk(
                    document_id=document.id,
                    user_id=user.id,
                    class_level=class_level,
                    subject=subject,
                    concept_key=block.concept_key,
                    content_type=block.content_type,
                    page_number=block.page_number,
                    chunk_index=block.block_index,
                    original_text=block.original_text,
                    text_hash=__import__("hashlib")
                    .sha256(block.original_text.encode())
                    .hexdigest(),
                    embedding_model=HASH_EMBEDDING_MODEL,
                    embedding_version=HASH_EMBEDDING_VERSION,
                    embedding=hash_embedding(block.original_text),
                )
            )
        session.commit()
    except Exception:
        session.rollback()
        delete_pdf(root=Path(settings.private_data_root), storage_key=storage_key)
        raise
    return _document_response(session, document)


@router.get("/documents", response_model=list[DemoDocumentResponse])
def list_documents(
    user: Annotated[User, Depends(get_current_demo_user)],
    session: Annotated[Session, Depends(get_db_session)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> list[DemoDocumentResponse]:
    purge_expired_documents(session, storage_root=Path(settings.private_data_root))
    documents = session.scalars(
        select(DemoDocument)
        .where(DemoDocument.user_id == user.id)
        .order_by(DemoDocument.created_at)
    )
    return [_document_response(session, document) for document in documents]


@router.delete("/documents/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(
    document_id: UUID,
    user: Annotated[User, Depends(get_current_demo_user)],
    session: Annotated[Session, Depends(get_db_session)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> None:
    document = get_owned_document(session, user_id=user.id, document_id=document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Demo document not found")
    delete_pdf(root=Path(settings.private_data_root), storage_key=document.storage_key)
    session.delete(document)
    session.commit()


@router.post("/retrieval/search", response_model=list[RetrievedChunkResponse])
def retrieve_chunks(
    request: RetrievalRequest,
    user: Annotated[User, Depends(get_current_demo_user)],
    session: Annotated[Session, Depends(get_db_session)],
) -> list[RetrievedChunkResponse]:
    results = search_student_chunks(
        session,
        user_id=user.id,
        document_version_ids=request.document_ids,
        class_level=request.class_level,
        subject=request.subject,
        concept_ids=request.concept_keys,
        content_types=request.content_types,
        query_text=request.query,
        limit=request.limit,
    )
    return [
        RetrievedChunkResponse(
            chunk_id=chunk.id,
            document_id=chunk.document_id,
            page_number=chunk.page_number,
            content_type=chunk.content_type,
            concept_key=chunk.concept_key,
            text=chunk.original_text,
            embedding_version=chunk.embedding_version,
        )
        for chunk in results
    ]


@router.post("/demo/sessions", response_model=StartSessionResponse, status_code=201)
def start_session(
    request: StartSessionRequest,
    user: Annotated[User, Depends(get_current_demo_user)],
    session: Annotated[Session, Depends(get_db_session)],
) -> StartSessionResponse:
    package = get_demo_package(request.package_key)
    profile = user.student_profile
    if package is None or profile is None:
        raise HTTPException(status_code=404, detail="Synthetic demo package not found")
    if package["class_level"] != profile.class_level or package["subject"] != profile.subject:
        raise HTTPException(status_code=403, detail="Package is outside the demo profile")
    evidence = []
    if request.document_id is not None:
        document = get_owned_document(session, user_id=user.id, document_id=request.document_id)
        if document is None:
            raise HTTPException(status_code=404, detail="Demo document not found")
        evidence = search_student_chunks(
            session,
            user_id=user.id,
            document_version_ids=[document.id],
            class_level=profile.class_level,
            subject=profile.subject,
            concept_ids=[package["concept_key"]],
            content_types=None,
            query_text=package["lesson"]["goal"],
            limit=5,
        )
        if not evidence:
            raise HTTPException(
                status_code=422, detail="Uploaded evidence does not support this demo concept"
            )
    learning_session = DemoLearningSession(
        user_id=user.id,
        document_id=request.document_id,
        package_key=package["package_key"],
        concept_key=package["concept_key"],
        lesson_template_version="synthetic-template-v1",
        hint_count=0,
    )
    session.add(learning_session)
    session.commit()
    question = {
        key: package["question"][key]
        for key in (
            "question_key",
            "text",
            "answer_type",
            "options",
            "cognitive_level",
            "difficulty",
        )
    }
    return StartSessionResponse(
        session_id=learning_session.id,
        package_key=package["package_key"],
        title=package["title"],
        review_status=package["review_status"],
        confidence=package["confidence"],
        lesson=package["lesson"],
        question=question,
        source=package["source"],
        evidence_chunk_ids=[chunk.id for chunk in evidence],
        known_limitations=[
            (
                "This deterministic package is original synthetic content and has not "
                "received educational review."
            ),
            "Confidence describes template/evidence matching, not learning effectiveness.",
        ],
    )


def _owned_learning_session(
    session: Session, *, user_id: UUID, session_id: UUID
) -> DemoLearningSession:
    item = session.scalar(
        select(DemoLearningSession).where(
            DemoLearningSession.id == session_id, DemoLearningSession.user_id == user_id
        )
    )
    if item is None:
        raise HTTPException(status_code=404, detail="Demo learning session not found")
    return item


@router.post("/demo/sessions/{session_id}/hints/{level}", response_model=HintResponse)
def reveal_hint(
    session_id: UUID,
    level: int,
    user: Annotated[User, Depends(get_current_demo_user)],
    session: Annotated[Session, Depends(get_db_session)],
) -> HintResponse:
    item = _owned_learning_session(session, user_id=user.id, session_id=session_id)
    if level not in (1, 2) or level > item.hint_count + 1:
        raise HTTPException(status_code=409, detail="Hints must be revealed in order")
    package = get_demo_package(item.package_key)
    if package is None:
        raise HTTPException(status_code=404, detail="Demo package no longer available")
    item.hint_count = max(item.hint_count, level)
    session.commit()
    return HintResponse(session_id=item.id, level=level, hint=package["question"][f"hint_{level}"])


@router.post(
    "/demo/sessions/{session_id}/attempts", response_model=AttemptResponse, status_code=201
)
def submit_attempt(
    session_id: UUID,
    request: AttemptRequest,
    user: Annotated[User, Depends(get_current_demo_user)],
    session: Annotated[Session, Depends(get_db_session)],
) -> AttemptResponse:
    item = _owned_learning_session(session, user_id=user.id, session_id=session_id)
    package = get_demo_package(item.package_key)
    if package is None:
        raise HTTPException(status_code=404, detail="Demo package no longer available")
    question = package["question"]
    result = evaluate_attempt(
        question=QuestionSnapshot(
            question_key=question["question_key"],
            answer_type=question["answer_type"],
            accepted_answer=question["accepted_answer"],
            accepted_unit=question["accepted_unit"],
            tolerance=Decimal(question["tolerance"]),
            rubric_version=question["rubric_version"],
        ),
        response=request.response,
    )
    attempt = DemoAttempt(
        session_id=item.id,
        user_id=user.id,
        question_key=question["question_key"],
        response_text=request.response,
        outcome=result.outcome,
        evaluation_features=result.features,
        rubric_version=question["rubric_version"],
        confidence=result.confidence,
        hint_count=item.hint_count,
    )
    session.add(attempt)
    session.commit()
    accepted = question["accepted_answer"] + (
        f" {question['accepted_unit']}" if question["accepted_unit"] else ""
    )
    return AttemptResponse(
        attempt_id=attempt.id,
        outcome=result.outcome,
        confidence=result.confidence,
        feedback=result.feedback,
        explanation=question["explanation"],
        accepted_answer=accepted,
        features=result.features,
        hint_count=item.hint_count,
    )


@router.get("/demo/progress", response_model=ProgressResponse)
def get_progress(
    user: Annotated[User, Depends(get_current_demo_user)],
    session: Annotated[Session, Depends(get_db_session)],
) -> ProgressResponse:
    rows = session.execute(
        select(
            DemoLearningSession.concept_key,
            func.count(DemoAttempt.id),
            func.count(DemoAttempt.id).filter(DemoAttempt.outcome == "correct"),
            func.count(DemoAttempt.id).filter(DemoAttempt.hint_count > 0),
        )
        .join(DemoAttempt, DemoAttempt.session_id == DemoLearningSession.id)
        .where(DemoLearningSession.user_id == user.id)
        .group_by(DemoLearningSession.concept_key)
    )
    observations = [
        ProgressObservation(
            concept_key=concept,
            attempts_observed=attempts,
            correct_observations=correct,
            supported_observations=supported,
            next_action=(
                "Try a second question in another form before drawing a conclusion."
                if attempts < 2
                else "Review the evidence and choose another practice item."
            ),
        )
        for concept, attempts, correct, supported in rows
    ]
    return ProgressResponse(
        policy_version="demo-progress-v1",
        observations=observations,
        limitation=(
            "Observations are not mastery scores and do not measure ability or educational "
            "improvement."
        ),
    )
