# PRD — ResumeLens Interview Coach

**Status:** Build-ready v1 specification  
**Product type:** NLP-first résumé analysis and interview-preparation web application  
**Primary users:** Students and early-career candidates preparing for Data Analyst, Business Analyst, Data Science, Product/Analytics, and entry-level software interviews  
**Core constraint:** This is a coaching product. It must not rank candidates for employers or make hiring decisions.

## 1. Product summary

ResumeLens lets a user upload a résumé PDF, converts it into structured evidence, identifies interview topics supported by that evidence, and conducts a personalized interview-preparation session. It asks questions about the user's projects, skills, experience, achievements, and likely role requirements. After each answer, it gives evidence-grounded feedback, tracks demonstrated strengths and weak areas, and recommends a preparation plan.

The product is intentionally **NLP-first and RAG-supported**:

1. NLP parses and structures résumé text.
2. A fine-tuned deep-learning classifier categorizes interview questions by topic and difficulty.
3. A planning engine maps résumé evidence to interview topics.
4. RAG retrieves the relevant résumé chunks and curated preparation content.
5. A controlled question/feedback engine uses only the retrieved evidence and explicit rubrics.

RAG does not replace model training. Embeddings are used for retrieval; the trained NLP classifier is a separately evaluated model artifact.

## 2. Problem statement

Generic interview-question lists are poorly matched to a candidate's actual résumé. Generic PDF chat applications can retrieve text, but they usually do not:

- create a structured candidate profile;
- plan balanced interview coverage;
- distinguish question topic and difficulty with a trained model;
- evaluate answer quality against explicit evidence and rubrics;
- track progress over several sessions; or
- explain why a strength, weakness, or preparation recommendation was produced.

The product should convert an uploaded résumé into an auditable, personalized preparation workflow.

## 3. Goals and non-goals

### 3.1 Goals for v1

- Accept a text-based PDF résumé of at most 10 MB and 10 pages.
- Extract readable text while preserving page and section references.
- Detect common résumé sections: summary, education, experience, projects, skills, achievements, certifications, and positions of responsibility.
- Extract candidate-mentioned skills, organizations, job titles, project names, metrics, dates, and action statements.
- Create semantically coherent chunks with traceable source metadata.
- Store document embeddings in PostgreSQL using `pgvector`.
- Train and evaluate a DistilBERT-based interview-question classifier.
- Generate a personalized interview plan for one selected target role.
- Conduct question-by-question practice sessions.
- Provide grounded answer feedback and show the résumé evidence used.
- Produce strength, weakness, and preparation-topic summaries with confidence and evidence.
- Save session history and show progress over time.
- Run locally with Docker Compose and deploy using a simple, documented production path.

### 3.2 Non-goals for v1

- Employer-facing candidate ranking, screening, rejection, or hiring recommendations.
- Video, voice, facial-expression, emotion, or personality analysis.
- Automatic job application or résumé rewriting.
- Training a large language model from scratch.
- Complex agent frameworks, knowledge graphs, Kubernetes, Kafka, microservices, or distributed training.
- OCR for arbitrary scanned documents. A scanned résumé must return a clear unsupported-file message in v1.
- Support for multiple document types beyond résumé PDF and curated interview-preparation text.
- Claims that a user is objectively “good” or “bad” at a topic based only on résumé wording.

## 4. User personas

### 4.1 Primary persona

A student or early-career candidate who has a project-heavy résumé and is targeting analyst, data, product, or entry-level technical roles. The user wants realistic questions, a structured practice plan, and feedback tied to their own work.

### 4.2 Secondary persona

A mentor reviewing a candidate's preparation history. Mentor access is not part of v1 authentication; the user may export or show their session summary.

## 5. Core user journeys

### 5.1 First-time setup

1. User creates an account or uses a local demo account.
2. User accepts a privacy notice explaining résumé storage and deletion.
3. User uploads a PDF résumé.
4. System validates type, size, page count, and extractable text.
5. System displays extracted sections and asks the user to confirm or correct obvious parsing errors.
6. User selects a target role and desired interview difficulty.
7. System creates a preparation dashboard.

### 5.2 Practice session

1. User chooses a session type: mixed, résumé deep-dive, technical, behavioral, or weak-area revision.
2. System selects questions using the interview plan, trained classifier, prior performance, and retrieved evidence.
3. One question is shown at a time.
4. User types an answer.
5. System evaluates the answer using an explicit rubric and relevant evidence.
6. User receives feedback, a stronger answer structure, missing points, and source evidence.
7. Session summary updates strengths, weak areas, and next topics.

### 5.3 Updated résumé

1. User uploads a new version.
2. System creates a new immutable document version.
3. Only the new version's chunks are embedded.
4. Old sessions remain linked to the old résumé version.
5. User may activate the new version for future sessions.

### 5.4 Data deletion

1. User deletes a document or account.
2. Related chunks, embeddings, analyses, and files are deleted according to foreign-key and storage rules.
3. The UI confirms the completed deletion.

## 6. Functional requirements

### FR-01 Authentication and ownership

- Email/password authentication is sufficient for v1.
- Passwords must be hashed with Argon2 or bcrypt.
- Every document, session, answer, and analysis query must be scoped to the authenticated user.
- A user must never retrieve another user's résumé chunks through vector search.

### FR-02 PDF upload and validation

- Allow only `%PDF` content with MIME and extension validation.
- Maximum 10 MB and 10 pages, configurable through environment variables.
- Use PyMuPDF for extraction.
- Reject encrypted, malformed, empty, or image-only PDFs with useful errors.
- Do not execute embedded PDF scripts, links, or attachments.
- Store the original file outside the public web root.
- Compute SHA-256 to detect duplicate uploads.

### FR-03 NLP résumé pipeline

The pipeline must run in this order:

1. text extraction and normalization;
2. page-boundary preservation;
3. section detection;
4. bullet and sentence segmentation;
5. entity/phrase extraction;
6. skill normalization against a versioned taxonomy;
7. metric and date extraction;
8. evidence-statement creation;
9. section-aware chunking;
10. embedding and indexing.

Use understandable methods first:

- regex and deterministic rules for dates, percentages, currency, counts, and section headings;
- spaCy for sentence segmentation and general named entities;
- a maintained alias dictionary for skills such as `Postgres` → `PostgreSQL`;
- confidence scores and `unknown` values rather than forced classifications.

### FR-04 Chunking and embeddings

- Chunk by section and bullet boundaries before applying a token limit.
- Target 250–450 tokens per chunk with 40–60 token overlap only when a long block must be split.
- Never combine unrelated résumé sections in one chunk.
- Store `document_id`, `document_version`, `user_id`, `section`, `page_start`, `page_end`, `chunk_index`, `text`, `token_count`, `embedding_model`, and `embedding_version`.
- Use `sentence-transformers/all-MiniLM-L6-v2` initially.
- Embedding model changes require a new embedding version and re-index command.

### FR-05 Trained deep-learning NLP model

Train a manageable `distilbert-base-uncased` sequence classifier that predicts:

- **question category:** resume verification, project deep-dive, data/SQL, machine learning, product/business analytics, behavioral, problem solving, software/backend, role motivation, or general technical;
- **difficulty:** foundational, intermediate, or advanced.

Implementation may use either two classifier heads or two separately trained classifiers. Prefer two separate models for v1 if the multi-task implementation materially complicates evaluation.

The model is used to:

- tag collected questions consistently;
- validate generated/template questions;
- balance categories and difficulty in a session;
- route questions to the correct feedback rubric;
- measure topic coverage.

It must not infer employability, personality, honesty, protected traits, or hiring suitability.

### FR-06 Dataset collection and labeling

Create a reproducible dataset pipeline, not an undocumented CSV.

Allowed data:

- public interview-question datasets with a verified license;
- questions from public documentation or educational sources whose license permits reuse;
- original questions written for this project;
- clearly marked synthetic paraphrases created from licensed/original seed questions.

Do not scrape sites whose terms or robots rules disallow it. Do not ingest candidate résumés, interview transcripts, emails, or private data without explicit consent.

Dataset target for v1:

- 5,000–15,000 final question examples;
- at least 300 human-reviewed examples in every retained category;
- at least 500 human-reviewed examples in the test set overall;
- source, license, collection date, original/synthetic flag, parent question ID, labels, and reviewer status for every row.

Required files:

- `data/raw/` — immutable source snapshots or source manifests;
- `data/interim/` — normalized and deduplicated data;
- `data/processed/train.jsonl`;
- `data/processed/validation.jsonl`;
- `data/processed/test.jsonl`;
- `data/DATASET_CARD.md`;
- `data/source_manifest.csv`;
- `src/ml/data/collect.py`;
- `src/ml/data/clean.py`;
- `src/ml/data/split.py`.

Leakage controls:

- normalize text and cluster near-duplicates before splitting;
- keep every synthetic paraphrase and its parent in the same split;
- if sources are templated, group by template before splitting;
- never tune thresholds or labels using the test set.

### FR-07 Training, evaluation, and model registry

Training must be reproducible with fixed seeds and saved configuration.

Track:

- dataset version/hash;
- model and tokenizer name;
- hyperparameters;
- random seed;
- code commit when available;
- train/validation curves;
- per-class precision, recall, and F1;
- macro F1 and weighted F1;
- confusion matrix;
- difficulty accuracy and macro F1;
- inference latency on CPU;
- error-analysis sample.

Acceptance gates:

- category macro F1 ≥ 0.75 on the untouched test set;
- no retained category recall below 0.60;
- difficulty macro F1 ≥ 0.65;
- majority-class and TF-IDF + logistic-regression baselines are recorded;
- DistilBERT must outperform the TF-IDF baseline by either ≥ 0.03 macro F1 or show a clear documented advantage on minority categories. Otherwise deploy the simpler baseline and record the honest result.

The latest model is promoted only after evaluation. Store artifacts under `artifacts/models/<model_name>/<version>/` with a model card.

### FR-08 RAG retrieval

Maintain two logical collections in PostgreSQL:

- user résumé chunks, strictly filtered by `user_id` and active `document_id`;
- curated interview-preparation chunks, filtered by role, topic, difficulty, source, and license.

Retrieval pipeline:

1. create a structured query from target role, requested session, résumé topics, and desired difficulty;
2. apply metadata filters before or during similarity search;
3. retrieve top-k candidates;
4. remove near-duplicates;
5. optionally apply a simple cross-encoder reranker only after the base system works;
6. return chunk IDs and similarity scores with every generated result.

Start with vector similarity plus metadata filtering. Do not add hybrid search or a reranker until retrieval evaluation shows a concrete need.

Retrieval evaluation set:

- at least 100 human-labeled queries;
- relevant chunk IDs for each query;
- Recall@5, MRR@10, and `no relevant result` rate;
- separate reporting for résumé retrieval and preparation-content retrieval.

### FR-09 Interview plan generation

The planner combines:

- target-role topic weights from a versioned YAML configuration;
- résumé evidence coverage;
- classifier category/difficulty;
- past answer performance;
- user-selected session type.

It produces:

- recommended topics;
- question counts by category and difficulty;
- résumé evidence linked to each personalized question;
- an explanation of why each topic was included.

Do not label a topic as a weakness merely because it is absent from the résumé. Use `not evidenced in résumé` until the user has answered related questions.

### FR-10 Question creation

Question sources, in priority order:

1. reviewed question bank with résumé entities inserted into safe templates;
2. retrieved licensed preparation questions adapted with controlled templates;
3. optional LLM provider behind a service interface, disabled by default.

Every question must store:

- final text;
- origin question/template ID;
- predicted and accepted category/difficulty;
- linked résumé chunk IDs;
- target skill/topic;
- generation method and version.

Question generation must avoid inventing tools, metrics, employers, or results not present in the résumé.

### FR-11 Answer feedback

V1 evaluates typed answers using transparent features:

- relevance to the question;
- coverage of rubric concepts;
- use of specific résumé evidence;
- answer structure, including STAR where applicable;
- specificity through actions, metrics, decisions, and outcomes;
- semantic similarity to retrieved reference concepts, used as one signal only.

Return:

- what was covered;
- what was missing;
- one actionable improvement;
- a suggested answer outline, not a fabricated personal story;
- evidence and preparation sources used;
- confidence: low, medium, or high.

Scores are coaching indicators, not ground truth. Low-evidence feedback must say so.

### FR-12 Strengths, weak areas, and preparation topics

Use three distinct states:

- **résumé evidence strength:** how strongly the résumé demonstrates a topic;
- **interview performance:** how well the user answered questions on a topic;
- **preparation priority:** combination of role importance, weak performance, and low coverage.

A strength requires at least two supporting observations or one strong résumé observation plus one satisfactory answer. A weak area requires at least two answered questions, unless the user explicitly marks it as weak. Missing résumé evidence alone is not weakness.

### FR-13 Dashboard

Pages:

- sign in/register;
- upload and parsing review;
- dashboard;
- résumé evidence explorer;
- interview setup;
- active interview session;
- session report;
- model/data transparency page;
- settings and delete-data controls.

Dashboard cards:

- active résumé version;
- target role;
- preparation priorities;
- topic coverage;
- recent sessions;
- strengths with evidence;
- weak areas with sample feedback;
- next recommended session.

### FR-14 Export

- Export a session report as JSON in v1.
- PDF export is a post-v1 enhancement.

## 7. Proposed system architecture

### 7.1 Technology choices

| Layer | Choice | Reason |
| --- | --- | --- |
| Frontend | React + TypeScript + Vite | Familiar, simple SPA development |
| Styling | CSS modules or Tailwind | Use one consistently; avoid a large UI framework |
| API | FastAPI + Pydantic | Python-native ML integration and clear schemas |
| ORM/migrations | SQLAlchemy 2 + Alembic | Mature PostgreSQL workflow |
| Database | PostgreSQL 16 + pgvector | Relational data and vectors in one system |
| PDF parsing | PyMuPDF | Practical text and page extraction |
| NLP | spaCy, regex, Transformers | Deterministic extraction plus trainable classifier |
| Embeddings | sentence-transformers MiniLM | Lightweight local embedding baseline |
| Training | PyTorch + Hugging Face Trainer | Accessible fine-tuning workflow |
| Background work | FastAPI background task in v1 | Avoid Celery/Redis until workloads require them |
| Testing | pytest, Vitest, React Testing Library | Standard backend/frontend tests |
| Local runtime | Docker Compose | Reproducible app + PostgreSQL |
| Deployment | Docker image + managed PostgreSQL | Simple production path |

### 7.2 Logical components

- **Web client:** upload, analysis review, sessions, dashboards.
- **FastAPI application:** authentication, business rules, ownership enforcement, API schemas.
- **Document pipeline:** parse, normalize, structure, chunk, embed.
- **NLP model service module:** load classifier once per process and return labels/probabilities.
- **Retrieval module:** scoped pgvector queries and traceable results.
- **Interview engine:** plan sessions, select/adapt questions, evaluate answers, update progress.
- **Training package:** collection, cleaning, labeling checks, baselines, fine-tuning, evaluation, promotion.
- **PostgreSQL:** application records, model metadata, chunks, and embeddings.

Keep these as modules in one backend repository. Do not split them into microservices in v1.

## 8. Data model

Minimum tables:

| Table | Purpose |
| --- | --- |
| `users` | Account and authentication fields |
| `documents` | Logical résumé and active version |
| `document_versions` | File metadata, hash, parse state, pipeline version |
| `resume_sections` | Parsed sections and page references |
| `resume_entities` | Skills, organizations, metrics, dates, projects, roles |
| `document_chunks` | Text, metadata, vector, embedding version |
| `target_roles` | Role definitions and topic weights |
| `question_bank` | Reviewed questions, labels, source/license metadata |
| `knowledge_chunks` | Curated preparation content and vectors |
| `interview_plans` | Planned category/topic/difficulty coverage |
| `interview_sessions` | Session configuration and status |
| `session_questions` | Selected/adapted question and evidence links |
| `answers` | User answer, rubric feedback, confidence, features |
| `topic_progress` | Aggregated evidence, performance, and priority |
| `model_versions` | Artifact path, dataset hash, metrics, promotion status |
| `audit_events` | Upload, parse, deletion, model/pipeline version events |

Use UUID primary keys, UTC timestamps, foreign keys, indexes on ownership/filter columns, and explicit delete behavior. Do not store raw passwords, access tokens, or PDF bytes in database rows.

## 9. API surface

Suggested endpoints:

```text
POST   /api/v1/auth/register
POST   /api/v1/auth/login
GET    /api/v1/me
POST   /api/v1/documents
GET    /api/v1/documents
GET    /api/v1/documents/{document_id}
GET    /api/v1/documents/{document_id}/analysis
PATCH  /api/v1/documents/{document_id}/analysis
DELETE /api/v1/documents/{document_id}
POST   /api/v1/interview-plans
GET    /api/v1/interview-plans/{plan_id}
POST   /api/v1/sessions
GET    /api/v1/sessions/{session_id}
POST   /api/v1/sessions/{session_id}/next-question
POST   /api/v1/sessions/{session_id}/answers
POST   /api/v1/sessions/{session_id}/complete
GET    /api/v1/sessions/{session_id}/report
GET    /api/v1/progress
GET    /api/v1/transparency/models
DELETE /api/v1/account
GET    /health/live
GET    /health/ready
```

Long-running upload analysis may return `202 Accepted` with a status endpoint. Avoid WebSockets in v1; polling is sufficient.

## 10. Non-functional requirements

### Security and privacy

- Validate file signatures, size, page count, and extraction result.
- Sanitize filenames and generate server-side storage names.
- Enforce user filters in every retrieval query.
- Use short-lived access tokens and secure cookie or documented bearer-token handling.
- Keep secrets in environment variables.
- Do not log résumé text, answers, passwords, tokens, or embeddings.
- Provide document and account deletion.
- Treat text inside PDFs as untrusted data, never as system instructions.
- Curated knowledge content must be reviewed before indexing.

### Performance targets

- Normal API p95 latency under 500 ms excluding model inference and upload processing.
- Question classifier p95 CPU inference under 300 ms per single question after warm-up.
- Vector retrieval p95 under 500 ms for the expected v1 dataset.
- A typical two-page résumé should finish parsing and embedding within 30 seconds on the reference local machine.

### Reliability and observability

- Structured logs with request ID, user ID hash, route, duration, status, and pipeline/model version.
- Health checks for API, database, vector extension, and model artifact availability.
- Failed document states must be retryable without duplicate chunks.
- Pipeline steps must be idempotent for a document version.

### Accessibility

- Keyboard-accessible interview flow.
- Form labels, visible focus states, semantic headings, and adequate color contrast.
- Do not encode performance by color alone.

## 11. Evaluation framework

The product is not complete merely because the UI works.

### 11.1 PDF/NLP extraction evaluation

- Build a consented or synthetic test set of at least 50 varied résumés.
- Manually annotate section boundaries and a subset of skills, metrics, projects, and dates.
- Report section accuracy/F1 and entity precision/recall/F1.
- Report extraction failure rate and parsing time.

### 11.2 Classifier evaluation

- Use untouched grouped test split.
- Compare majority, TF-IDF logistic regression, and DistilBERT.
- Publish per-class metrics and confusion matrix.
- Review at least 100 errors and categorize failure causes.

### 11.3 Retrieval evaluation

- Human-labeled query-to-chunk relevance set.
- Recall@5, MRR@10, no-result rate, and wrong-user retrieval count.
- Wrong-user retrieval count must always be zero.

### 11.4 Question-quality evaluation

Human reviewers score at least 100 generated/adapted questions for:

- supported by résumé evidence;
- relevant to target role;
- clear and answerable;
- correct category and difficulty;
- non-duplication;
- absence of invented claims.

Target: at least 90% supported and answerable, with zero cross-user evidence leaks.

### 11.5 Feedback evaluation

Human reviewers evaluate at least 50 question-answer-feedback triples for rubric alignment, evidence support, usefulness, and unsupported claims. Store reviewer notes and revise rules before release.

## 12. Success metrics

### Product metrics

- upload-to-analysis completion rate;
- percentage of users starting a session after analysis;
- session completion rate;
- repeated session rate within seven days;
- user-rated question relevance and feedback usefulness;
- deletion success rate.

### Quality guardrails

- unsupported résumé claim rate;
- cross-user retrieval incidents;
- low-confidence feedback rate;
- duplicate-question rate per session;
- classifier performance by category;
- retrieval Recall@5.

Do not optimize engagement at the expense of honest feedback or privacy.

## 13. Delivery phases

### Phase 0 — Repository and foundations

- Monorepo structure, Docker Compose, PostgreSQL + pgvector, migrations, linting, tests, CI.
- Authentication skeleton and health checks.
- Seed target-role configurations.

**Exit:** clean setup from README; API and database health tests pass.

### Phase 1 — PDF ingestion and structured NLP

- Secure upload, PyMuPDF extraction, section detection, entities, review UI.
- Versioned parsed output and extraction evaluation fixture.

**Exit:** 50-résumé evaluation report; idempotent retry; ownership tests.

### Phase 2 — Dataset and deep-learning classifier

- Source manifest, labeling guide, deduplication, grouped splits.
- TF-IDF baseline, DistilBERT training, evaluation, model card, promotion command.

**Exit:** acceptance gates met or an honest documented decision to retain the baseline.

### Phase 3 — Chunking and retrieval

- Section-aware chunks, embeddings, pgvector queries, curated knowledge ingestion.
- Retrieval evaluation dataset and report.

**Exit:** retrieval targets recorded; wrong-user retrieval tests pass.

### Phase 4 — Interview engine

- Topic planning, question selection/adaptation, classifier routing, answer rubric, progress aggregation.

**Exit:** deterministic end-to-end session works without an external LLM.

### Phase 5 — Full frontend

- Dashboard, interview flow, reports, evidence viewer, transparency and deletion pages.

**Exit:** primary journeys pass browser tests and accessibility checks.

### Phase 6 — Deployment and hardening

- Production Dockerfile, managed PostgreSQL/pgvector, object storage or protected volume, HTTPS, backups, monitoring, migration runbook.

**Exit:** deployed staging smoke test, restore test, and privacy/security checklist pass.

## 14. Deployment plan

Recommended learning-friendly path:

- frontend: static build served by Nginx or the selected cloud's static hosting;
- backend: one Dockerized FastAPI service on AWS App Runner/ECS Fargate or Azure Container Apps;
- database: AWS RDS PostgreSQL or Azure Database for PostgreSQL with pgvector support;
- files: private S3/Azure Blob container with encryption and lifecycle rules;
- CI/CD: GitHub Actions for tests, image build, and staging deployment;
- migrations: explicit Alembic command during release, never silently from each web worker.

Implement only one cloud path first. Keep cloud services behind documented environment variables and storage interfaces.

## 15. Risks and mitigations

| Risk | Mitigation |
| --- | --- |
| Public dataset licenses are unclear | Require source manifest and license approval; exclude unknown-license data |
| Synthetic paraphrases inflate metrics | Group parent/paraphrases in one split and report original-only metrics |
| Résumé parser fails on unusual layouts | Parsing review step, confidence flags, varied evaluation set |
| RAG retrieves another user's content | Mandatory ownership filter and adversarial isolation tests |
| “Weakness” claims are unfair | Require repeated answer evidence; distinguish absent evidence from poor performance |
| Fine-tuned model adds no value | Compare against TF-IDF; deploy simpler model if it wins |
| Generated questions invent facts | Template-first generation and stored chunk citations |
| Scope becomes an agent/LLM project | Preserve deterministic v1; optional provider only after core acceptance |
| CPU deployment is slow | DistilBERT/MiniLM, batching where useful, load once, benchmark before scaling |

## 16. Definition of done

V1 is done only when:

- a new user can upload a valid résumé, review extraction, select a role, complete an interview, and view an evidence-grounded report;
- an updated résumé creates a separate version without corrupting prior sessions;
- the classifier has a reproducible dataset, baseline, test report, and model card;
- retrieval has a labeled evaluation and zero cross-user results in security tests;
- no strength or weakness is shown without traceable evidence and confidence;
- local Docker setup, automated tests, migrations, and one staging deployment work from documentation;
- the user can delete their document and account data;
- the repository contains no private résumé, secrets, unlicensed dataset, or committed model cache.

## 17. Post-v1 backlog

- Optional job-description upload and gap analysis.
- Voice interview mode using speech-to-text, without emotion scoring.
- Better reranking if retrieval evaluation justifies it.
- Human mentor comments and shared reports.
- PDF report export.
- Multiple languages after a language-specific evaluation set exists.
- Carefully evaluated LLM-assisted feedback behind the existing provider interface.

