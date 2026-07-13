# LearnStep

> **Upload. Learn. Ace it.**

LearnStep is an NLP-first learning companion portfolio demo for Classes 5–8 Mathematics and Science. It accepts text-based PDF learning material, preserves page evidence, detects educational content types and known synthetic concepts, retrieves owner-scoped evidence with PostgreSQL/pgvector, and guides a learner through a deterministic lesson → question → hint → feedback → revision flow without an external LLM.

This repository is a controlled demonstration, not a public product for children. Demo accounts and bundled chapters are synthetic. The content is not official, reviewed, CBSE/NCERT-endorsed, or evidence of educational improvement. Do not enter real child information.

## What works

- two synthetic demo identities with Argon2 password hashes and short-lived signed tokens;
- private PDF storage with generated keys, extension/MIME/magic-byte/size/page/encryption/text checks;
- automatic one-hour expiry cleanup plus immediate owner-authorized deletion;
- page-preserving extraction and deterministic labels for heading, definition, fact, formula, explanation, worked example, activity, question, and solution;
- mandatory user/document/class/subject/concept filters before pgvector retrieval;
- pre-authored synthetic lessons with sources, evidence IDs, confidence wording, and limitations;
- staged hints that do not reveal the answer;
- exact MCQ and numeric-with-unit/tolerance evaluation;
- immutable attempt observations and non-ranking progress guidance;
- reproducible synthetic extraction, classifier-baseline, retrieval, and assessment evaluations.

## Architecture

```text
React/Vite/Nginx
       │ HTTPS / JSON / temporary PDF
       ▼
FastAPI modular monolith
  ├─ demo authentication and ownership
  ├─ private upload storage + expiry cleanup
  ├─ PyMuPDF + deterministic educational NLP
  ├─ scoped retrieval + deterministic teaching
  └─ answer-type evaluator + progress observations
       │
       ▼
PostgreSQL 16 + pgvector
```

The runtime remains one modular monolith. There are no agents, external LLMs, queues, public file paths, student rankings, or cross-student comparisons.

## Run with Docker

Prerequisites: Docker Desktop with its Linux engine running. Git is optional for local testing.

```powershell
docker compose up -d db
docker compose run --rm backend alembic upgrade head
docker compose run --rm backend python -m classpath.scripts.seed_demo_curriculum
docker compose up -d --build backend frontend
docker compose ps
```

Open:

- LearnStep: <http://localhost:5173>
- controlled demo: <http://localhost:5173/demo>
- API documentation: <http://localhost:8000/docs>
- readiness: <http://localhost:8000/health/ready>

The UI signs into the synthetic accounts automatically. Direct API testing may use:

| Account | Password | Scope |
| --- | --- | --- |
| `math-demo@example.invalid` | `Demo-Math-2026` | Class 5 Mathematics |
| `science-demo@example.invalid` | `Demo-Science-2026` | Class 6 Science |

These public credentials are intentional demo fixtures and must never be reused for a real deployment.

## Generate and evaluate synthetic evidence

Windows PowerShell:

```powershell
.\backend\.venv\Scripts\python.exe scripts\generate_synthetic_evaluation_data.py
$env:PYTHONPATH="backend/src"
.\backend\.venv\Scripts\python.exe scripts\evaluate_extraction.py
.\backend\.venv\Scripts\python.exe scripts\evaluate_classifiers.py
.\backend\.venv\Scripts\python.exe scripts\evaluate_assessment.py
$env:DATABASE_URL="postgresql+psycopg://classpath:classpath_dev@localhost:5432/classpath"
.\backend\.venv\Scripts\python.exe scripts\evaluate_retrieval.py
```

Measured on 2026-07-13 on this local development machine:

| Evaluation | Scope | Measured result |
| --- | --- | --- |
| PDF extraction | 60 generator-controlled synthetic PDFs, 8 concepts, 3 layouts | 60/60 extracted; content-type micro F1 1.00; concept micro F1 1.00 |
| Cognitive classifier | 384 unreviewed synthetic questions; grouped test n=64 | majority macro F1 0.0556; TF-IDF macro F1 1.00 |
| Difficulty classifier | same grouped test | majority macro F1 0.1818; TF-IDF macro F1 1.00 |
| Retrieval | 120 synthetic queries, real PostgreSQL/pgvector, two users | Recall@5 1.00; MRR@10 1.00; 0 cross-user/wrong-class/wrong-concept results |
| Assessment | 100 MCQ + 100 numeric synthetic cases | rule-outcome accuracy 1.00 for each type |

The perfect synthetic scores are expected from generator-controlled fixtures and are not real-world performance claims. DistilBERT was not trained because the required human-reviewed labels, frozen test set, and 100-error review do not exist. No classifier is promoted.

## Verification

```powershell
cd backend
.\.venv\Scripts\ruff.exe check . ..\scripts
.\.venv\Scripts\ruff.exe format --check . ..\scripts
.\.venv\Scripts\mypy.exe src tests ..\scripts
.\.venv\Scripts\pytest.exe -m "not integration"
$env:APP_ENV="test"
$env:DATABASE_URL="postgresql+psycopg://classpath:classpath_dev@localhost:5432/classpath"
.\.venv\Scripts\pytest.exe -m integration
cd ..
pnpm --dir frontend verify
docker compose build backend frontend
```

## Portfolio evidence and honest gaps

- [Architecture](docs/architecture.md)
- [API](docs/api.md)
- [Evaluation and failure boundaries](docs/evaluation.md)
- [Dataset card](data/DATASET_CARD.md)
- [Synthetic TF-IDF baseline model card](artifacts/models/tfidf-synthetic-baseline/MODEL_CARD.md)
- [Child safety and privacy](docs/child-safety-and-privacy.md)
- [Threat model](docs/threat-model.md)
- [Deployment design](docs/deployment.md)
- [Human review protocol](docs/content-review.md)
- [Portfolio evidence checklist](docs/portfolio-evidence.md)

Still required before public or child-facing use: qualified privacy/legal review, educational-content review, 100 completed package reviews, a licensed/human-reviewed classifier dataset, DistilBERT comparison, varied real-world document evaluation, abuse/rate-limit testing, operational monitoring, backup/restore rehearsal, and a properly designed student study before any educational-improvement claim.

## Git

The local repository is connected to `https://github.com/Shradd7/LearnStep.git`. Nothing is pushed by the setup or evaluation commands.
