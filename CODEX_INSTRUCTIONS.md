# Codex Build Instructions — ClassPath Learning Companion

## 1. Mission

Build the complete project described in `PRD.md` as a working, tested and deployable application for CBSE-aligned Classes 5–8 Mathematics and Science.

The portfolio story must remain technically accurate:

> NLP structures uploaded learning material and maps it to reviewed concepts. A trained classifier controls question cognitive level and difficulty. RAG retrieves class- and concept-filtered evidence. A deterministic teaching engine builds lessons, hints, practice and evidence-based progress.

Do not turn the product into a generic PDF chatbot, an unrestricted child-facing chatbot, or an overbuilt multi-agent system.

## 2. Required stack

- Python 3.12
- FastAPI and Pydantic v2
- SQLAlchemy 2 and Alembic
- PostgreSQL 16 with pgvector
- PyMuPDF
- spaCy plus deterministic extraction rules
- PyTorch, Hugging Face Transformers/Datasets and scikit-learn
- sentence-transformers with `all-MiniLM-L6-v2`
- React, TypeScript and Vite
- pytest, Vitest and React Testing Library
- Docker and Docker Compose
- Ruff for Python; ESLint and Prettier for frontend

Use one dependency only when it has a direct current purpose. Ask before making a major substitution or adding a service that changes cost/complexity.

## 3. Required repository structure

Create directories only as the corresponding vertical slice is implemented.

```text
classpath/
├── AGENTS.md
├── PRD.md
├── CODEX_INSTRUCTIONS.md
├── README.md
├── .env.example
├── .gitignore
├── docker-compose.yml
├── Makefile
├── configs/
│   ├── curriculum/
│   ├── extraction/
│   ├── lesson_templates/
│   ├── answer_rubrics/
│   └── safety/
├── backend/
│   ├── pyproject.toml
│   ├── alembic.ini
│   ├── alembic/
│   ├── src/classpath/
│   │   ├── main.py
│   │   ├── api/
│   │   ├── core/
│   │   ├── db/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── repositories/
│   │   ├── services/
│   │   │   ├── documents/
│   │   │   ├── curriculum/
│   │   │   ├── nlp/
│   │   │   ├── retrieval/
│   │   │   ├── teaching/
│   │   │   ├── assessment/
│   │   │   ├── progress/
│   │   │   └── storage/
│   │   └── observability/
│   └── tests/
├── frontend/
│   ├── package.json
│   ├── src/
│   │   ├── api/
│   │   ├── components/
│   │   ├── features/
│   │   ├── pages/
│   │   ├── routes/
│   │   ├── types/
│   │   └── test/
│   └── tests/
├── ml/
│   ├── pyproject.toml
│   ├── configs/
│   ├── src/classpath_ml/
│   │   ├── data/
│   │   ├── baselines/
│   │   ├── training/
│   │   ├── evaluation/
│   │   └── registry/
│   └── tests/
├── data/
│   ├── README.md
│   ├── DATASET_CARD.md
│   ├── LABELING_GUIDE.md
│   ├── source_manifest.csv
│   ├── raw/.gitkeep
│   ├── interim/.gitkeep
│   └── processed/.gitkeep
├── artifacts/
│   ├── README.md
│   └── models/.gitkeep
├── docs/
│   ├── architecture.md
│   ├── api.md
│   ├── child-safety-and-privacy.md
│   ├── content-review.md
│   ├── deployment.md
│   ├── evaluation.md
│   ├── threat-model.md
│   ├── adr/
│   └── reports/
└── scripts/
    ├── bootstrap.sh
    ├── seed_demo_curriculum.py
    ├── ingest_reviewed_content.py
    ├── evaluate_all.py
    └── smoke_test.py
```

Production code belongs in importable packages. Notebooks may explore data but must import shared package functions and must not become the only implementation.

## 4. Working method

For each milestone:

1. Read `AGENTS.md`, `PRD.md`, this file, existing tests and relevant code.
2. Inspect the worktree and preserve user changes.
3. Write a short plan tied to the milestone's observable acceptance criteria.
4. Implement the smallest complete vertical slice.
5. Add migrations, tests, fixtures, documentation and version fields in the same change.
6. Run focused checks during work and the required milestone checks before handoff.
7. Report only actual results, including failures and limitations.
8. Stop at the milestone boundary unless the user explicitly requests continuation.

Do not generate a large empty architecture before the first end-to-end flow works.

## 5. Ordered implementation milestones

### Milestone 0 — Foundation

Build:

- root README with exact prerequisites and commands;
- `.env.example` containing variable names and safe development defaults only;
- Docker Compose for PostgreSQL/pgvector, FastAPI and React;
- FastAPI app factory, configuration validation, database session and health routes;
- React shell with routing and backend health state;
- initial Alembic migration;
- minimal user and `student_profile` schema;
- lint, format, type-check, test and build commands;
- CI without network-dependent tests.

Seed only a tiny synthetic development taxonomy, clearly marked `synthetic_demo` and not presented as verified curriculum.

Required verification:

- clean database migration upgrade;
- API liveness/readiness;
- pgvector extension/dimension check;
- frontend production build;
- backend/frontend unit tests and type checks.

### Milestone 1 — Authentication, consent record and secure upload

Build:

- registration, login and current-user route;
- password hashing and documented token/cookie strategy;
- ownership dependencies and repository filters;
- student-profile CRUD for Classes 5–8 and Math/Science;
- policy/notice version record without overclaiming legal compliance;
- private storage interface and local implementation;
- PDF validation, generated storage keys and SHA-256;
- document/document-version schema and explicit processing states;
- extraction-status polling and safe deletion;
- retry-safe processing boundary.

Tests must include:

- non-PDF bytes and spoofed extension;
- encrypted, malformed, empty and image-only PDF;
- maximum size/page failures;
- path traversal and unsafe filenames;
- duplicate upload/version behaviour;
- user A reading, searching or deleting user B's file;
- document deletion removes derived test records and stored fixture file.

### Milestone 2 — Educational NLP pipeline

Implement pure typed functions before API integration:

```python
extract_pdf(path: Path) -> ExtractedDocument
normalize_document(document: ExtractedDocument) -> NormalizedDocument
detect_content_blocks(document: NormalizedDocument) -> list[ContentBlock]
segment_learning_items(blocks: list[ContentBlock]) -> list[LearningItem]
extract_terms_and_quantities(items: list[LearningItem]) -> list[ExtractedEntity]
map_concepts(items: list[LearningItem], taxonomy: CurriculumTaxonomy) -> list[ConceptMatch]
create_learning_units(...) -> list[LearningUnitDraft]
create_chunks(...) -> list[ChunkDraft]
```

Required content-block labels:

- heading;
- explanation;
- definition;
- fact;
- formula;
- worked example;
- activity;
- question;
- answer/solution;
- other.

Rules:

- preserve page and source spans where feasible;
- keep formulas/units with nearby explanation;
- do not infer an absent concept as a fact;
- keep original text separate from normalized labels;
- record rule/model/pipeline version and confidence;
- low-confidence mapping becomes `unmapped` or `needs_review`;
- provide API/UI correction without editing the original source.

Create at least 60 legally usable synthetic/consented fixtures across classes, subjects and layouts before claiming extraction metrics. Commit annotations, not private school files.

Required output:

- `scripts/evaluate_extraction.py`;
- machine-readable metrics JSON;
- Markdown failure analysis with representative synthetic examples;
- regression tests for every fixed parser failure.

### Milestone 3 — Curriculum taxonomy

Build a versioned, reviewable curriculum representation:

```text
class → subject → unit → topic → concept → prerequisite
```

Seed development records from original synthetic content first. Before importing real curriculum data:

1. add source to `data/source_manifest.csv`;
2. verify intended reuse and storage permission;
3. record reviewer and version;
4. retain provenance for each concept/content item.

Implement:

- stable concept IDs;
- aliases and descriptions;
- prerequisite edges;
- class/subject constraints;
- common-misconception records;
- review status;
- cycle detection in prerequisites;
- taxonomy version activation without rewriting historic sessions.

Do not silently claim official endorsement or alignment.

### Milestone 4 — Educational question dataset and classifier

Do not scrape or download data until its source entry and license decision exist.

#### Canonical dataset row

```json
{
  "question_id": "stable-id",
  "text": "Why does a shadow change length during the day?",
  "class_level": 6,
  "subject": "science",
  "topic_id": "light-and-shadows",
  "cognitive_level": "understand",
  "difficulty": "intermediate",
  "answer_type": "explanation",
  "source_id": "manifest-source-id",
  "license": "verified-license",
  "is_synthetic": false,
  "parent_question_id": null,
  "passage_group_id": null,
  "template_group_id": null,
  "review_status": "human_reviewed"
}
```

#### Labeling rules

- `remember`: recall a term, fact, formula or direct procedure;
- `understand`: explain, compare, classify or interpret;
- `apply`: use learned knowledge in a familiar/new concrete problem;
- `analyse`: connect evidence, break down reasoning or justify across steps;
- `foundational`: direct single-concept check;
- `intermediate`: one or more linked steps with normal class prerequisites;
- `challenge`: unfamiliar application or deeper combination, still within the selected class.

Create `LABELING_GUIDE.md` with positive/negative examples and adjudication rules. Measure inter-annotator agreement on a reviewed sample; disagreement is resolved before the test set is frozen.

#### Reproducible data stages

1. collect approved source records;
2. normalize and validate;
3. remove malformed/unsafe items;
4. exact and near-duplicate clustering;
5. label validation and review-status checks;
6. grouped stratified splitting;
7. dataset fingerprint and report.

Questions from the same passage, exercise, template, parent/paraphrase family or near-duplicate cluster stay in one split. Processed splits are generated, never manually edited.

#### Models

Train in this order:

1. majority baseline;
2. TF-IDF word/character n-grams + Logistic Regression;
3. DistilBERT cognitive-level classifier;
4. DistilBERT difficulty classifier only after the first task is evaluated.

Separate models are preferred over premature multi-task complexity. Class/subject/topic should remain curriculum metadata unless a separately labeled experiment demonstrates value.

Use configuration files, fixed seeds, early stopping and a small controlled search—not an expensive hyperparameter sweep.

#### Required evaluation artifacts

- dataset/source/label distributions;
- duplicate and exclusion report;
- macro/weighted/per-class precision, recall and F1;
- confusion matrices;
- original-only versus synthetic-inclusive metrics;
- grade- and subject-sliced results;
- calibration/reliability report if probabilities drive decisions;
- CPU latency benchmark;
- at least 100 human-reviewed errors;
- promotion decision against PRD gates;
- model card and artifact checksum.

If DistilBERT does not justify itself, deploy the baseline and document the failed hypothesis.

### Milestone 5 — Chunking, embeddings and RAG

Build learning-purpose-aware chunks and store pgvector embeddings with full metadata/versioning.

Generic document or blind token-window chunking is prohibited. Unit tests must cover:

- concept and chapter boundaries;
- formula/explanation preservation;
- question/options/solution preservation;
- overlap only when necessary;
- deterministic text hashes and chunk indexes;
- document-version immutability.

The student retrieval interface must require ownership and learning context:

```python
search_student_chunks(
    *,
    user_id: UUID,
    document_version_ids: list[UUID],
    class_level: int,
    subject: Subject,
    concept_ids: list[UUID],
    content_types: list[ContentType] | None,
    query_vector: list[float],
    limit: int,
) -> list[RetrievedChunk]
```

No unscoped user-document vector search may exist in production code.

Reviewed knowledge ingestion requires source, license, class, subject, topic, content type, review status and citation fields. Do not fetch arbitrary web content during a student request.

Create a labeled retrieval evaluation with at least 120 queries and report:

- Recall@1/5;
- MRR@10;
- no-result and duplicate rates;
- wrong-class and wrong-concept rates;
- latency;
- cross-user isolation count.

Add reranking/hybrid search only after documenting which baseline errors it should solve.

### Milestone 6 — Teaching engine

Implement deterministic learning-unit construction before considering generation.

Required lesson structure:

```text
learning goal
prerequisite reminder
simple explanation
worked/everyday example
foundational check
application question
recap
source references
```

Build versioned lesson templates by subject and content type. Template slots may use only retrieved evidence or reviewed template content. Store every selected chunk/template/version with the resulting immutable session item.

Before displaying a unit, validate:

- profile class and subject;
- concept/prerequisite state;
- source/review status;
- classifier cognitive level/difficulty;
- required answer/rubric presence;
- unsafe/off-topic patterns;
- duplicate exposure.

If evidence is insufficient, return a specific abstention state or a reviewed generic learning unit. Do not fabricate content.

### Milestone 7 — Question, hint and assessment engine

Implement reviewed question selection and controlled template adaptation. Each question package requires:

- question and answer type;
- accepted answer or explicit rubric;
- two staged hints;
- explanation/approach;
- concept/prerequisite/class metadata;
- cognitive/difficulty label and classifier version;
- source/evidence IDs.

Implement evaluators behind a typed interface:

```python
evaluate_attempt(
    *, question: QuestionSnapshot, response: StudentResponse
) -> EvaluationResult
```

Evaluator types:

- multiple-choice/boolean exact match;
- numeric parsing with units and configured tolerance;
- short-text accepted variants and concept coverage;
- explanation rubric feedback with confidence/abstention;
- structured worked-step checks where supported.

Never use semantic similarity as the sole correctness signal for mathematics, numeric questions or contradictory text.

Hint behaviour:

- hint 1 identifies relevant concept/first move;
- hint 2 gives stronger procedural scaffolding;
- answer reveal requires an attempt or explicit action;
- hint use is evidence about needed support, not punishment.

Create adversarial evaluation cases for unit mistakes, alternative correct phrasing, contradictions, partial explanations, irrelevant keyword stuffing and malformed input.

### Milestone 8 — Progress and revision

Persist immutable attempts and atomic concept evidence. Calculate aggregates through a versioned progress policy.

Maintain separate fields/services for:

- curriculum coverage;
- observed learning evidence;
- revision priority.

Required rules:

- one answer cannot establish independent demonstration;
- repeated evidence must span at least two items and preferably more than one form;
- hints reduce independence of that observation but never imply a fixed limitation;
- later evidence does not erase old attempts;
- a low-confidence automated evaluation does not update strong progress states;
- changing curriculum/rubric version does not silently rewrite history;
- aggregate progress must be rebuildable from immutable evidence.

Use clear states from the PRD, not labels such as `weak`, `smart`, `slow` or `poor`.

### Milestone 9 — Frontend completion

Build accessible, responsive flows for:

- account/privacy entry;
- class/subject profile;
- upload and processing;
- detected-topic review;
- home dashboard;
- chapter/concept explorer;
- learn session;
- practice setup and one-question-at-a-time session;
- staged hints and feedback;
- revision queue;
- progress evidence;
- source/model transparency;
- reporting a content problem;
- document/account deletion.

Frontend rules:

- use generated or centrally maintained typed API contracts;
- show loading, empty, error, retry, expired and low-confidence states;
- keep one primary action per learning screen;
- open evidence at the correct page/content block;
- distinguish uploaded from reviewed content;
- never display fake charts, mastery percentages or competitive rankings;
- do not use colour alone for correctness/progress;
- solution reveal is deliberate, not automatic.

### Milestone 10 — Safety review, deployment and documentation

Build:

- content-report workflow;
- age/off-topic response boundaries;
- production multi-stage containers;
- CORS allowlist, secure headers, rate/size limits and environment validation;
- managed PostgreSQL/pgvector deployment;
- private object-storage adapter with encryption/deletion/lifecycle;
- model artifact checksum verification and startup readiness;
- structured privacy-safe logs and monitoring;
- backup, restore, rollback and migration runbooks;
- one cloud path only.

Before a real child-facing release, document that qualified legal/privacy and educational-content review is still required. Do not claim compliance merely because technical controls exist.

Creating paid cloud resources or configuring a real domain requires user approval.

## 6. Database implementation requirements

- UUID primary keys and timezone-aware UTC timestamps.
- Explicit ownership paths, foreign keys and delete behaviour.
- Indexes beginning with ownership/curriculum filters used in queries.
- Immutable document versions, question/session snapshots and attempts.
- Rebuildable progress aggregates from atomic evidence.
- Version fields for curriculum, extraction pipeline, lesson template, embedding, classifier, answer rubric and progress policy.
- Vector dimension validated against configured embedding model at startup.
- JSONB only for truly versioned/flexible payloads, not fields requiring normal filtering/constraints.
- Do not store uploaded PDF bytes in relational rows.

## 7. API rules

- Version routes under `/api/v1`.
- Use Pydantic request/response models; do not return ORM entities.
- Error shape: `code`, `message`, `request_id` and optional safe `details`.
- Use appropriate status codes: `201`, `202`, `400/422`, `401`, `403`, `404`, `409`.
- Cursor pagination for growing lists.
- Idempotency keys for attempts, processing retry and other duplicate-sensitive commands.
- Server enforces class/subject/ownership; never trust frontend metadata alone.
- OpenAPI examples are synthetic and contain no child/student identifiers.
- Long processing uses status polling; WebSockets are unnecessary for v1.

## 8. Testing requirements

Required layers:

- unit tests for extraction, content blocks, concept mapping, prerequisite checks, chunking, lesson construction, evaluators and progress policy;
- repository integration tests using real PostgreSQL/pgvector;
- API tests for authentication, profile, upload, analysis correction, session lifecycle, deletion and ownership;
- ML-data tests with tiny local fixtures;
- model contract tests with a tiny local artifact;
- frontend component tests for critical states;
- browser smoke test: profile → upload → review → learn → attempt → feedback → progress;
- migration test from empty database;
- retrieval security test proving no cross-user result;
- content-safety tests for document instructions and unsafe/off-topic inputs.

Unit tests must not use network access. Full model downloads/training are not normal CI tasks. Do not mock PostgreSQL vector behaviour in the only integration test.

Every reproducible bug fix receives a regression test.

## 9. Documentation requirements

Maintain in the same change as behaviour:

- `README.md`: exact local setup and command reference;
- `docs/architecture.md`: data and request flows;
- `docs/api.md`: authentication and main endpoints;
- `docs/child-safety-and-privacy.md`: data minimization, oversight, deletion and limitations;
- `docs/content-review.md`: source approval and human-review workflow;
- `docs/threat-model.md`: upload, cross-user retrieval, prompt injection and content risks;
- `docs/evaluation.md`: extraction, classifier, retrieval, lesson, question and evaluator results;
- `docs/deployment.md`: one fully documented cloud route;
- `data/DATASET_CARD.md`: provenance, licenses, labels, splits, biases and intended use;
- model card for each promoted classifier;
- ADR for any consequential architectural/product decision.

Do not paste fabricated metrics into documentation.

## 10. Commands to expose

Provide Makefile or equivalent targets:

```text
make setup
make dev
make lint
make typecheck
make test
make test-integration
make migrate
make seed-demo
make data-validate
make train-baseline
make train-cognitive-classifier
make train-difficulty-classifier
make evaluate-models
make evaluate-extraction
make evaluate-retrieval
make evaluate-assessment
make smoke
```

Commands fail non-zero on failure and print enough context to diagnose the issue without leaking student content.

## 11. Implementation decisions Codex may make without asking

Codex may make reversible choices such as:

- module and function names consistent with the architecture;
- accessible visual layout and neutral colour palette;
- exact database index names;
- local storage directory beneath the configured private data root;
- small synthetic fixtures;
- threshold defaults that are documented as development values;
- whether CSS modules or Tailwind is used, selecting only one.

Codex must pause before:

- importing a real dataset/content source whose license is not already approved;
- creating paid cloud resources;
- adding a generative model or external LLM;
- expanding classes, subjects, boards or languages;
- changing child/consent data collection;
- adding surveillance, ranking or diagnostic functionality;
- using real student data;
- materially altering the product architecture.

## 12. Milestone completion report

Use this structure:

1. **Outcome:** what a student can now do.
2. **Files changed:** concise grouped list.
3. **Data/schema/API changes:** migrations and contracts.
4. **Verification:** exact commands and pass/fail counts.
5. **Measured results:** actual metrics only, with dataset/fixture scope.
6. **Safety/privacy impact:** controls added or unresolved review.
7. **Known limitations and failed attempts.**
8. **Next milestone:** one narrow recommendation.

Do not call scaffolding a product, demo data verified curriculum, or a configuration-only deployment completed.