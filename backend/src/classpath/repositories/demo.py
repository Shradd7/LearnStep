from datetime import UTC, datetime
from pathlib import Path
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from classpath.models.demo import DemoDocument, DemoDocumentChunk
from classpath.services.retrieval.hashing import hash_embedding
from classpath.services.storage import delete_pdf


def get_owned_document(
    session: Session, *, user_id: UUID, document_id: UUID
) -> DemoDocument | None:
    return session.scalar(
        select(DemoDocument).where(
            DemoDocument.id == document_id,
            DemoDocument.user_id == user_id,
            DemoDocument.expires_at > datetime.now(UTC),
        )
    )


def search_student_chunks(
    session: Session,
    *,
    user_id: UUID,
    document_version_ids: list[UUID],
    class_level: int,
    subject: str,
    concept_ids: list[str],
    content_types: list[str] | None,
    query_text: str,
    limit: int,
) -> list[DemoDocumentChunk]:
    """Search only after every ownership and learning-context filter is present."""

    if not document_version_ids or not concept_ids:
        return []
    query = (
        select(DemoDocumentChunk)
        .where(
            DemoDocumentChunk.user_id == user_id,
            DemoDocumentChunk.document_id.in_(document_version_ids),
            DemoDocumentChunk.class_level == class_level,
            DemoDocumentChunk.subject == subject,
            DemoDocumentChunk.concept_key.in_(concept_ids),
        )
        .order_by(DemoDocumentChunk.embedding.cosine_distance(hash_embedding(query_text)))
        .limit(min(max(limit, 1), 20))
    )
    if content_types:
        query = query.where(DemoDocumentChunk.content_type.in_(content_types))
    return list(session.scalars(query))


def purge_expired_documents(session: Session, *, storage_root: Path) -> int:
    expired = list(
        session.scalars(select(DemoDocument).where(DemoDocument.expires_at <= datetime.now(UTC)))
    )
    for document in expired:
        delete_pdf(root=storage_root, storage_key=document.storage_key)
    if expired:
        session.execute(
            delete(DemoDocument).where(DemoDocument.id.in_([item.id for item in expired]))
        )
        session.commit()
    return len(expired)
