"""Run grouped majority and TF-IDF baselines on unreviewed synthetic questions."""

from __future__ import annotations

import hashlib
import json
import statistics
import time
from pathlib import Path
from typing import Any

from sklearn.dummy import DummyClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import GroupShuffleSplit
from sklearn.pipeline import FeatureUnion, Pipeline

ROOT = Path(__file__).resolve().parents[1]


def evaluate_model(
    model: Any, train_x: list[str], train_y: list[str], test_x: list[str], test_y: list[str]
) -> dict[str, Any]:
    model.fit(train_x, train_y)
    predictions = model.predict(test_x)
    durations: list[float] = []
    for text in test_x:
        started = time.perf_counter()
        model.predict([text])
        durations.append((time.perf_counter() - started) * 1000)
    labels = sorted(set(test_y) | set(predictions))
    return {
        "classification_report": classification_report(
            test_y, predictions, labels=labels, output_dict=True, zero_division=0
        ),
        "labels": labels,
        "confusion_matrix": confusion_matrix(test_y, predictions, labels=labels).tolist(),
        "cpu_single_item_latency_ms": {
            "median": statistics.median(durations),
            "p95": sorted(durations)[max(0, int(len(durations) * 0.95) - 1)],
        },
    }


def main() -> None:
    path = ROOT / "data" / "synthetic" / "questions.jsonl"
    raw = path.read_bytes()
    rows = [json.loads(line) for line in raw.decode("utf-8").splitlines() if line]
    texts = [row["text"] for row in rows]
    groups = [row["template_group_id"] for row in rows]
    first = GroupShuffleSplit(n_splits=1, test_size=0.30, random_state=20260713)
    train_indices, remainder_indices = next(first.split(texts, groups=groups))
    remainder_groups = [groups[index] for index in remainder_indices]
    second = GroupShuffleSplit(n_splits=1, test_size=0.50, random_state=20260713)
    validation_relative, test_relative = next(
        second.split(remainder_indices, groups=remainder_groups)
    )
    validation_indices = [remainder_indices[index] for index in validation_relative]
    test_indices = [remainder_indices[index] for index in test_relative]
    split_groups = {
        "train": {groups[index] for index in train_indices},
        "validation": {groups[index] for index in validation_indices},
        "test": {groups[index] for index in test_indices},
    }
    if (
        (split_groups["train"] & split_groups["validation"])
        or (split_groups["train"] & split_groups["test"])
        or (split_groups["validation"] & split_groups["test"])
    ):
        raise RuntimeError("Template groups leaked across classifier splits")
    train_x = [texts[index] for index in train_indices]
    test_x = [texts[index] for index in test_indices]
    result: dict[str, Any] = {
        "scope": f"{len(rows)} original unreviewed synthetic questions",
        "dataset_sha256": hashlib.sha256(raw).hexdigest(),
        "seed": 20260713,
        "split_counts": {
            "train": len(train_indices),
            "validation": len(validation_indices),
            "test": len(test_indices),
        },
        "group_leakage_count": 0,
        "targets": {},
        "distilbert": {
            "status": "not_run",
            "reason": (
                "The required human-reviewed labels, frozen grouped test set, and error review "
                "do not exist. Downloading/fine-tuning DistilBERT now would produce misleading "
                "portfolio evidence."
            ),
        },
        "promotion_decision": "none; synthetic-only baselines are not eligible for promotion",
        "limitations": [
            "All questions and labels are generator-controlled and unreviewed.",
            "Metrics measure template generalization only, not real educational question quality.",
            (
                "Original-only versus synthetic-inclusive comparison is unavailable because "
                "no approved original external dataset is present."
            ),
        ],
    }
    for target in ("cognitive_level", "difficulty"):
        train_y = [rows[index][target] for index in train_indices]
        test_y = [rows[index][target] for index in test_indices]
        majority = DummyClassifier(strategy="most_frequent")
        tfidf = Pipeline(
            [
                (
                    "features",
                    FeatureUnion(
                        [
                            ("word", TfidfVectorizer(ngram_range=(1, 2), min_df=2)),
                            (
                                "char",
                                TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), min_df=2),
                            ),
                        ]
                    ),
                ),
                (
                    "classifier",
                    LogisticRegression(
                        max_iter=1000, random_state=20260713, class_weight="balanced"
                    ),
                ),
            ]
        )
        result["targets"][target] = {
            "majority": evaluate_model(majority, train_x, train_y, test_x, test_y),
            "tfidf_logistic_regression": evaluate_model(tfidf, train_x, train_y, test_x, test_y),
        }
    output_root = ROOT / "artifacts" / "evaluation"
    output_root.mkdir(parents=True, exist_ok=True)
    (output_root / "classifier_metrics.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
