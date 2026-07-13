"""Run a real PostgreSQL/pgvector retrieval evaluation with ownership attacks."""

from __future__ import annotations

import json
import statistics
import time
from datetime import UTC, datetime, timedelta
from pathlib import Path
from uuid import uuid4

from sqlalchemy.orm import Session

from classpath.core.config import get_settings
from classpath.db.session import get_engine
from classpath.models.demo import DemoDocument, DemoDocumentChunk
from classpath.models.user import User
from classpath.repositories.demo import search_student_chunks
from classpath.services.auth import PASSWORD_HASHER
from classpath.services.nlp.extraction import CONCEPT_ALIASES
from classpath.services.retrieval.hashing import (
    HASH_EMBEDDING_MODEL,
    HASH_EMBEDDING_VERSION,
    hash_embedding,
)

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    engine = get_engine(get_settings().database_url)
    run_id = uuid4().hex
    latencies: list[float] = []
    ranks: list[int | None] = []
    wrong_class = wrong_concept = cross_user = 0
    with Session(engine) as session:
        users = [
            User(
                email=f"retrieval-{run_id}-{index}@example.invalid",
                password_hash=PASSWORD_HASHER.hash(run_id),
                is_demo=True,
                notice_version="evaluation-only",
            )
            for index in range(2)
        ]
        session.add_all(users)
        session.flush()
        documents: dict[tuple[int, str], DemoDocument] = {}
        expected_chunks: dict[tuple[int, str], DemoDocumentChunk] = {}
        for user_index, user in enumerate(users):
            for concept_index, (concept, aliases) in enumerate(CONCEPT_ALIASES.items()):
                subject = "mathematics" if concept_index < 4 else "science"
                class_level = 5 + concept_index % 4
                document = DemoDocument(
                    user_id=user.id,
                    display_name=f"synthetic-{concept}.pdf",
                    storage_key=f"{uuid4().hex}.pdf",
                    sha256=uuid4().hex + uuid4().hex,
                    class_level=class_level,
                    subject=subject,
                    status="ready",
                    extraction_pipeline_version="retrieval-evaluation-v1",
                    expires_at=datetime.now(UTC) + timedelta(hours=1),
                )
                session.add(document)
                session.flush()
                text = f"Definition: {concept.replace('_', ' ')} includes {', '.join(aliases)}."
                chunk = DemoDocumentChunk(
                    document_id=document.id,
                    user_id=user.id,
                    class_level=class_level,
                    subject=subject,
                    concept_key=concept,
                    content_type="definition",
                    page_number=1,
                    chunk_index=0,
                    original_text=text,
                    text_hash=(uuid4().hex + uuid4().hex),
                    embedding_model=HASH_EMBEDDING_MODEL,
                    embedding_version=HASH_EMBEDDING_VERSION,
                    embedding=hash_embedding(text),
                )
                session.add(chunk)
                documents[(user_index, concept)] = document
                expected_chunks[(user_index, concept)] = chunk
        session.commit()
        concepts = list(CONCEPT_ALIASES)
        for query_index in range(120):
            user_index = query_index % 2
            concept = concepts[query_index % len(concepts)]
            document = documents[(user_index, concept)]
            expected = expected_chunks[(user_index, concept)]
            started = time.perf_counter()
            results = search_student_chunks(
                session,
                user_id=users[user_index].id,
                document_version_ids=[document.id],
                class_level=document.class_level,
                subject=document.subject,
                concept_ids=[concept],
                content_types=None,
                query_text=f"Explain {concept.replace('_', ' ')}",
                limit=5,
            )
            latencies.append((time.perf_counter() - started) * 1000)
            ids = [item.id for item in results]
            ranks.append(ids.index(expected.id) + 1 if expected.id in ids else None)
            wrong_class += sum(item.class_level != document.class_level for item in results)
            wrong_concept += sum(item.concept_key != concept for item in results)
            other_user = users[1 - user_index]
            attack = search_student_chunks(
                session,
                user_id=other_user.id,
                document_version_ids=[document.id],
                class_level=document.class_level,
                subject=document.subject,
                concept_ids=[concept],
                content_types=None,
                query_text=concept,
                limit=5,
            )
            cross_user += len(attack)
        for user in users:
            session.delete(user)
        session.commit()
    metrics = {
        "scope": "120 synthetic queries over real PostgreSQL 16/pgvector with two isolated users",
        "embedding": "deterministic synthetic hash baseline; not MiniLM",
        "recall_at_1": sum(rank == 1 for rank in ranks) / len(ranks),
        "recall_at_5": sum(rank is not None and rank <= 5 for rank in ranks) / len(ranks),
        "mrr_at_10": sum((1 / rank) if rank and rank <= 10 else 0 for rank in ranks) / len(ranks),
        "no_result_rate": sum(rank is None for rank in ranks) / len(ranks),
        "wrong_class_count": wrong_class,
        "wrong_concept_count": wrong_concept,
        "cross_user_result_count": cross_user,
        "latency_ms": {
            "median": statistics.median(latencies),
            "p95": sorted(latencies)[max(0, int(len(latencies) * 0.95) - 1)],
        },
        "limitations": [
            "Relevant chunks and queries are generator-controlled synthetic fixtures.",
            "Strict metadata filters make this primarily an isolation/filtering baseline.",
            "Semantic retrieval quality on varied school language is not established.",
        ],
    }
    output_root = ROOT / "artifacts" / "evaluation"
    output_root.mkdir(parents=True, exist_ok=True)
    (output_root / "retrieval_metrics.json").write_text(
        json.dumps(metrics, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
