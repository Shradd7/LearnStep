# Content and package review

Bundled lessons, questions, answers, hints, and evaluation corpora are original synthetic fixtures marked `synthetic_demo_not_educationally_reviewed` or `unreviewed_synthetic`. They are not verified curriculum and must not be relabeled without a documented reviewer decision.

## 100-package review queue

Regenerate `data/synthetic/human_review_queue.jsonl` with:

```powershell
.\backend\.venv\Scripts\python.exe scripts\generate_synthetic_evaluation_data.py
```

Each of the 100 rows starts with `pending_human_review`, null reviewer, null notes, and null decisions for:

- source support;
- class appropriateness;
- clarity and answerability;
- answer/rubric correctness;
- staged-hint quality;
- absence of invented claims.

A qualified human reviewer must record identity/role, date, decision, and notes. Codex output is not counted as human review. Current completed-review count: **0/100**.

Real content may be considered only after owner, URL, access date, license/terms, intended use, redistribution/training decision, and reviewer are recorded in `data/source_manifest.csv`.
