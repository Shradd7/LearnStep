# Dataset card — LearnStep synthetic evaluation bundle

## Purpose and provenance

All rows and PDFs are original generator-controlled synthetic fixtures created by `scripts/generate_synthetic_evaluation_data.py`. No website, textbook, school PDF, student work, account, answer, or private record was imported. Source ID: `learnstep-original-synthetic-v1` in `data/source_manifest.csv`.

## Contents

- 60 text-based PDF chapters across eight synthetic concept keys and three simple generated layout families;
- page/content/concept annotations for extraction evaluation;
- 384 synthetic question rows with cognitive-level, difficulty, class, subject, topic, template-group, source, and review metadata;
- 100 pending human package-review records;
- three sample PDFs for the controlled demo.

## Labels and split

Cognitive levels: remember, understand, apply, analyse. Difficulty: foundational, intermediate, challenge. Labels are assigned by generation templates and are **not human-reviewed**. The classifier script uses fixed seed `20260713` and grouped splitting by `template_group_id`; the recorded run had 264 train, 56 validation, and 64 test rows with zero group overlap.

Dataset SHA-256 for the recorded `questions.jsonl`: `8a857298e82209d32c2415c57b4364247f4822ae890e9ada1c5e44c58da48814`.

## Intended use

Deterministic parser regression, data-contract testing, pipeline demonstrations, security/isolation tests, and baseline-script verification.

## Prohibited claims and limitations

Do not use these fixtures to claim CBSE/NCERT alignment, curriculum correctness, real-document extraction quality, classifier robustness, model production readiness, or educational improvement. Template artifacts make the classification task unrealistically easy. There is no approved external/original comparison set, inter-annotator agreement, demographic representation, OCR, handwriting, complex layout, or real classroom language.
