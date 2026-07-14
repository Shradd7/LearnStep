# LearnStep

> **Upload. Learn. Ace it. 🚀**

[![CI](https://github.com/Shradd7/LearnStep/actions/workflows/ci.yml/badge.svg)](https://github.com/Shradd7/LearnStep/actions/workflows/ci.yml)

LearnStep is an NLP-first learning companion portfolio demo for Classes 5–8 Mathematics and Science. Students often struggle because an explanation is too advanced, too generic, or disconnected from their chapter. LearnStep explores a different flow: upload learning material, extract structured evidence, teach one clear concept, practise with staged hints, receive deterministic feedback, and decide what to revise next.

This repository is a **controlled synthetic demonstration**, not a public product for children. Demo accounts, chapters, PDFs, questions, labels, and evaluation corpora are synthetic. Nothing here is official, reviewed, CBSE/NCERT-endorsed, or evidence of educational improvement. Do not enter real child information.

## Try it out

| Resource | URL | Availability |
| --- | --- | --- |
| Public repository and evidence | <https://github.com/Shradd7/LearnStep> | Public |
| Local application | <http://localhost:5173> | After Docker setup below |
| Local controlled demo | <http://localhost:5173/demo> | After Docker setup below |
| Local API documentation | <http://localhost:8000/docs> | After Docker setup below |

There is currently **no public live application**. For a Devpost “Try it out” field, use the public repository URL and state that the executable demo is local-only.

## What works

- two synthetic demo identities with Argon2 password hashes and short-lived signed tokens;
- private temporary PDF storage with generated keys, validation, automatic expiry, and owner-authorized deletion;
- page-preserving PyMuPDF extraction with deterministic educational content labels;
- mandatory user, document, class, subject, and concept filters before pgvector retrieval;
- deterministic lessons with sources, evidence IDs, confidence wording, and limitations;
- hint 1 and hint 2 before solution reveal;
- exact multiple-choice and numeric-with-unit/tolerance evaluation;
- immutable attempt observations and non-ranking progress guidance;
- reproducible synthetic extraction, TF-IDF baseline, retrieval/isolation, and assessment evaluations;
- a complete synthetic journey: login → optional upload → lesson → hint → answer → feedback → progress → deletion.

## Architecture

```mermaid
flowchart LR
    UI["React + TypeScript<br/>accessible learning flow"] -->|"JSON + temporary PDF"| API["FastAPI modular monolith"]
    API --> NLP["PyMuPDF + deterministic<br/>educational NLP"]
    API --> TEACH["Deterministic lessons,<br/>hints and evaluators"]
    NLP --> DB["PostgreSQL 16 + pgvector"]
    TEACH --> DB
    API --> STORE["Private expiring<br/>file storage"]
```

The runtime has no external LLM, agents, queues, public file paths, student rankings, or cross-student comparisons. The controlled retrieval demo uses a clearly labeled deterministic 384-dimensional hash vector; it is not a claim about MiniLM semantic quality.

## Demo screenshots

All screenshots below were captured from the running synthetic demo at 1440×960 (3:2) and are under 5 MB.

| Screenshot | What it shows |
| --- | --- |
| ![LearnStep landing page](docs/media/devpost/01-landing.png) | Landing page, product boundary, and live service state |
| ![Synthetic learner selection](docs/media/devpost/02-synthetic-learner-selection.png) | Class 5 Mathematics and Class 6 Science synthetic identities |
| ![Synthetic chapter selection](docs/media/devpost/03-chapter-selection.png) | Class-filtered chapters with source and confidence wording |
| ![Source-grounded lesson](docs/media/devpost/04-source-grounded-lesson.png) | Structured lesson, source details, and practice question |
| ![Staged hint](docs/media/devpost/05-staged-hint.png) | Hint-first interaction before answer reveal |
| ![Deterministic feedback and progress](docs/media/devpost/06-feedback-and-progress.png) | Transparent answer feedback and non-ranking learning evidence |

## Run locally with Docker

Prerequisites: Docker Desktop with the Linux engine running. Git is optional for local testing.

```powershell
docker compose up -d db
docker compose run --rm backend alembic upgrade head
docker compose run --rm backend python -m classpath.scripts.seed_demo_curriculum
docker compose up -d --build backend frontend
docker compose ps
```

Open <http://localhost:5173/demo>. The UI enters either synthetic account without requiring manual credentials. Direct API testing may use:

| Account | Password | Scope |
| --- | --- | --- |
| `math-demo@example.invalid` | `Demo-Math-2026` | Class 5 Mathematics |
| `science-demo@example.invalid` | `Demo-Science-2026` | Class 6 Science |

These public credentials are intentional fixtures and must never be reused for a real deployment.

## Synthetic controlled-demo results

Measured locally on 2026-07-13. These results verify deterministic behavior on generator-controlled fixtures; they do not establish curriculum quality, educational effectiveness, or real-document generalization.

| Evaluation | Synthetic scope | Measured result |
| --- | --- | --- |
| PDF extraction | 60 generated PDFs, 8 concepts, 3 layouts | 60/60 extracted; content-type micro F1 1.00; concept micro F1 1.00 |
| Cognitive classifier | 384 unreviewed synthetic questions; grouped test n=64 | Majority macro F1 0.0556; TF-IDF macro F1 1.00 |
| Difficulty classifier | Same grouped test | Majority macro F1 0.1818; TF-IDF macro F1 1.00 |
| Retrieval and isolation | 120 synthetic queries, real PostgreSQL/pgvector, 2 users | Recall@5 1.00; MRR@10 1.00; 0 cross-user, wrong-class, or wrong-concept results |
| Assessment | 100 MCQ + 100 numeric synthetic cases | Rule-outcome accuracy 1.00 for each implemented answer type |

The perfect synthetic scores are expected because fixtures and labels are generator-controlled. DistilBERT was **not trained**: the repository does not yet have approved human-reviewed labels, a frozen real-world test set, inter-annotator review, or 100 reviewed classifier errors. No classifier is promoted.

## Built with Codex and GPT-5.6

Codex was used to plan, scaffold, implement, test, audit, and document LearnStep. GPT-5.6/Codex helped iterate on the modular architecture, deterministic test cases, child-safety boundaries, ownership isolation, and synthetic evaluation artifacts. The final system was verified using the documented controlled-demo test suite and real local PostgreSQL/pgvector integration checks.

Codex and GPT-5.6 did **not** independently validate curriculum quality, perform human educational review, run a student study, or create evidence for claims beyond the committed synthetic artifacts. Generated suggestions were treated as engineering input and checked against executable tests and recorded outputs.

## Verification commands

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

Evaluation regeneration commands are documented in [docs/evaluation.md](docs/evaluation.md). Media regeneration is documented in [docs/media/devpost/README.md](docs/media/devpost/README.md).

## Safety, privacy, and limitations

- No real student data, private school PDFs, or external curriculum sources are included.
- Demo uploads expire after 60 minutes and can be deleted immediately by their synthetic owner.
- Learning evidence is not a mastery score and never ranks or compares learners.
- No DistilBERT training has been completed.
- No real-school document validation or qualified curriculum review has been completed.
- The 100-package human-review queue remains 0/100 completed.
- No public child-facing deployment exists.
- No student study has been conducted, so no educational-improvement claim is made.
- A real release still requires qualified privacy/legal review, educational-content review, rate-limit and abuse testing, operational monitoring, backup/restore rehearsal, and deployment-specific consent/retention decisions.

## Documentation

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

## Deployment status

The repository includes buildable containers and an intentionally inert Azure Container Apps workflow. No cloud resources or public app URL exist. Provisioning remains blocked until the owner explicitly approves a subscription, region, spend, credentials, private storage, database, and public hostname.
