"""Evaluate deterministic extraction on the generated synthetic PDF corpus."""

from __future__ import annotations

import json
import statistics
import time
from collections import Counter
from pathlib import Path

from classpath.services.nlp.extraction import detect_content_blocks, extract_pdf

ROOT = Path(__file__).resolve().parents[1]


def prf(*, true_positive: int, false_positive: int, false_negative: int) -> dict[str, float]:
    precision = (
        true_positive / (true_positive + false_positive) if true_positive + false_positive else 0.0
    )
    recall = (
        true_positive / (true_positive + false_negative) if true_positive + false_negative else 0.0
    )
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {"precision": precision, "recall": recall, "f1": f1}


def main() -> None:
    data_root = ROOT / "data" / "synthetic" / "evaluation"
    annotations = json.loads((data_root / "annotations.json").read_text(encoding="utf-8"))
    content_tp = content_fp = content_fn = 0
    concept_tp = concept_fp = concept_fn = 0
    failures: list[dict[str, object]] = []
    durations: list[float] = []
    for annotation in annotations:
        started = time.perf_counter()
        try:
            blocks = detect_content_blocks(extract_pdf(data_root / "pdfs" / annotation["filename"]))
        except Exception as error:
            failures.append(
                {"document_id": annotation["document_id"], "error": type(error).__name__}
            )
            continue
        durations.append((time.perf_counter() - started) * 1000)
        expected_types = Counter(annotation["content_types"])
        predicted_types = Counter(block.content_type for block in blocks)
        for label in expected_types.keys() | predicted_types.keys():
            overlap = min(expected_types[label], predicted_types[label])
            content_tp += overlap
            content_fp += predicted_types[label] - overlap
            content_fn += expected_types[label] - overlap
        expected_concepts = set(annotation["concept_keys"])
        predicted_concepts = {block.concept_key for block in blocks if block.concept_key}
        concept_tp += len(expected_concepts & predicted_concepts)
        concept_fp += len(predicted_concepts - expected_concepts)
        concept_fn += len(expected_concepts - predicted_concepts)
        if expected_types != predicted_types or expected_concepts != predicted_concepts:
            failures.append(
                {
                    "document_id": annotation["document_id"],
                    "expected_types": expected_types,
                    "predicted_types": predicted_types,
                    "expected_concepts": sorted(expected_concepts),
                    "predicted_concepts": sorted(predicted_concepts),
                }
            )
    metrics = {
        "scope": "60 original synthetic PDFs across 8 concepts and 3 generated layout families",
        "review_status": "unreviewed_synthetic",
        "documents_total": len(annotations),
        "documents_extracted": len(durations),
        "document_failure_rate": (len(annotations) - len(durations)) / len(annotations),
        "content_type_micro": prf(
            true_positive=content_tp, false_positive=content_fp, false_negative=content_fn
        ),
        "concept_micro": prf(
            true_positive=concept_tp, false_positive=concept_fp, false_negative=concept_fn
        ),
        "latency_ms": {
            "median": statistics.median(durations),
            "p95": sorted(durations)[max(0, int(len(durations) * 0.95) - 1)],
        },
        "failure_count": len(failures),
        "limitations": [
            "The corpus is generator-controlled synthetic data, not real school material.",
            (
                "No OCR, handwriting, tables, complex equations, or adversarial layouts are "
                "represented."
            ),
            (
                "These results do not establish curriculum correctness or real-document "
                "generalization."
            ),
        ],
    }
    output_root = ROOT / "artifacts" / "evaluation"
    report_root = ROOT / "docs" / "reports"
    output_root.mkdir(parents=True, exist_ok=True)
    report_root.mkdir(parents=True, exist_ok=True)
    (output_root / "extraction_metrics.json").write_text(
        json.dumps(metrics, indent=2) + "\n", encoding="utf-8"
    )
    failure_lines = [
        "# Synthetic extraction failure analysis",
        "",
        f"Evaluated documents: {len(annotations)}; flagged differences: {len(failures)}.",
        "",
        (
            "This is generator-controlled synthetic evidence, not performance on real school "
            "documents."
        ),
        "",
        "## Flagged cases",
        "",
        "```json",
        json.dumps(failures[:20], indent=2),
        "```",
        "",
    ]
    (report_root / "extraction_failure_analysis.md").write_text(
        "\n".join(failure_lines), encoding="utf-8"
    )
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
