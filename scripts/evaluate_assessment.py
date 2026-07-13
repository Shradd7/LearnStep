"""Evaluate MCQ and numerical rules on labeled synthetic adversarial cases."""

from __future__ import annotations

import json
from decimal import Decimal
from pathlib import Path

from classpath.services.assessment.evaluator import QuestionSnapshot, evaluate_attempt

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    mcq = QuestionSnapshot(
        question_key="synthetic-mcq", answer_type="multiple_choice", accepted_answer="3/4"
    )
    numeric = QuestionSnapshot(
        question_key="synthetic-numeric",
        answer_type="numeric",
        accepted_answer="16",
        accepted_unit="cm",
        tolerance=Decimal("0.01"),
    )
    cases: list[tuple[str, QuestionSnapshot, str, str]] = []
    for index in range(50):
        response = ("3/4", " 3/4 ", "3/4  ")[index % 3]
        cases.append(("multiple_choice", mcq, response, "correct"))
    for index in range(50):
        response = ("1/4", "4/3", "three quarters", "3 / 4")[index % 4]
        cases.append(("multiple_choice", mcq, response, "incorrect"))
    for index in range(50):
        response = ("16 cm", "16.0 CM", "16.00cm", "15.999 cm")[index % 4]
        cases.append(("numeric", numeric, response, "correct"))
    for index in range(50):
        response, expected = (
            ("16 m", "incorrect"),
            ("15 cm", "incorrect"),
            ("sixteen cm", "needs_review"),
            ("16", "incorrect"),
        )[index % 4]
        cases.append(("numeric", numeric, response, expected))
    correct = {"multiple_choice": 0, "numeric": 0}
    total = {"multiple_choice": 0, "numeric": 0}
    failures: list[dict[str, str]] = []
    for answer_type, question, response, expected in cases:
        actual = evaluate_attempt(question=question, response=response).outcome
        total[answer_type] += 1
        if actual == expected:
            correct[answer_type] += 1
        else:
            failures.append(
                {"type": answer_type, "response": response, "expected": expected, "actual": actual}
            )
    metrics = {
        "scope": "200 programmatically labeled synthetic evaluator cases",
        "overall_accuracy": sum(correct.values()) / sum(total.values()),
        "multiple_choice_accuracy": correct["multiple_choice"] / total["multiple_choice"],
        "numeric_accuracy": correct["numeric"] / total["numeric"],
        "cases": total,
        "failure_count": len(failures),
        "failures": failures,
        "limitations": [
            "These cases test deterministic parsing rules, not educational validity.",
            "Short-text and explanation rubric evaluation are not implemented in this demo slice.",
        ],
    }
    output_root = ROOT / "artifacts" / "evaluation"
    output_root.mkdir(parents=True, exist_ok=True)
    (output_root / "assessment_metrics.json").write_text(
        json.dumps(metrics, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
