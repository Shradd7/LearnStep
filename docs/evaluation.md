# Evaluation record

All current evidence is synthetic and was generated locally on 2026-07-13. These measurements verify deterministic software behavior; they do not establish curriculum quality, learning effectiveness, or generalization to real school documents.

## Extraction

- Corpus: 60 original synthetic PDFs, eight concepts, Classes 5–8 represented, Mathematics and Science represented, three simple generated layout families.
- Result: 60/60 extracted; document failure rate 0; content-type micro precision/recall/F1 1.00; concept micro precision/recall/F1 1.00.
- Local latency: median 2.12 ms, p95 3.72 ms on the final recorded run.
- Artifact: `artifacts/evaluation/extraction_metrics.json`.
- Failure analysis: `docs/reports/extraction_failure_analysis.md`.

The corpus does not include OCR, handwriting, dense tables, complex equations, damaged scans, or adversarial layouts. The perfect score reflects rules evaluated against the generator that produced the labeled prefixes.

## Question classifiers

- Dataset: 384 generator-controlled, unreviewed synthetic questions.
- Grouped split: train 264, validation 56, untouched test 64; template-group leakage count 0.
- Cognitive level: majority macro F1 0.0556; TF-IDF Logistic Regression macro F1 1.00.
- Difficulty: majority macro F1 0.1818; TF-IDF Logistic Regression macro F1 1.00.
- Artifact: `artifacts/evaluation/classifier_metrics.json`, including per-class metrics, confusion matrices, dataset SHA-256, seed, and CPU latency.

DistilBERT status: **not run**. The required human-reviewed labels, frozen grouped test set, inter-annotator process, and 100-error human review do not exist. Training against these template labels would create impressive but misleading portfolio evidence. No model is promoted.

## Retrieval and isolation

- Runtime: real PostgreSQL 16 with pgvector 0.8.0.
- Scope: 120 synthetic queries, two isolated users, deterministic 384-dimensional hash-vector baseline, strict ownership/class/subject/concept filters.
- Recall@1: 1.00; Recall@5: 1.00; MRR@10: 1.00; no-result rate 0.
- Wrong-class results: 0; wrong-concept results: 0; cross-user results: 0.
- Local latency: median 2.39 ms, p95 3.85 ms on the final recorded run.
- Artifact: `artifacts/evaluation/retrieval_metrics.json`.

This is primarily a metadata-filter and isolation baseline. It does not establish semantic retrieval quality for varied school language and it does not use MiniLM.

## Assessment

- 100 MCQ exact/normalized cases and 100 numeric value/unit/tolerance/malformed-input cases.
- Outcome accuracy: MCQ 1.00; numeric 1.00; failures 0.
- Artifact: `artifacts/evaluation/assessment_metrics.json`.

Short-text, explanation-rubric, and worked-step evaluators are not implemented. Rule accuracy does not establish educational validity.

## User journey

The PostgreSQL integration suite executes: synthetic login → temporary PDF upload → extraction → detected concept → owner-scoped pgvector retrieval → lesson → hint 1 → answer → feedback → progress observation → file/database deletion. It also attempts cross-user retrieval and receives zero results.

## Human review and student studies

`data/synthetic/human_review_queue.jsonl` contains 100 review records with null decisions and `pending_human_review` status. No human review is claimed. No student study has been conducted, so LearnStep makes no claim of educational improvement.
