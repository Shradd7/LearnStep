# Data boundary

The repository contains no downloaded, scraped, real-curriculum, or student data. Bundled educational-looking records are original fictional/synthetic fixtures marked `synthetic_demo` or `unreviewed_synthetic`.

- `backend/src/classpath/fixtures/demo_curriculum.json`: four tiny metadata records.
- `data/synthetic/evaluation`: 60 generated PDFs plus extraction annotations.
- `data/synthetic/questions.jsonl`: 384 generated classifier-baseline questions.
- `data/synthetic/human_review_queue.jsonl`: 100 pending, not completed, review records.
- `data/synthetic/samples`: three sample PDFs safe for the controlled demo.

Regenerate the synthetic bundle with `scripts/generate_synthetic_evaluation_data.py`. Do not place real student work, private school files, or unknown-license curriculum in this repository.
