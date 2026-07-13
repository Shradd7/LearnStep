from decimal import Decimal

import pytest

from classpath.services.assessment.evaluator import QuestionSnapshot, evaluate_attempt


@pytest.mark.parametrize(
    ("response", "expected"),
    [("3/4", "correct"), (" 3/4 ", "correct"), ("4/3", "incorrect")],
)
def test_multiple_choice_uses_normalized_exact_match(response: str, expected: str) -> None:
    question = QuestionSnapshot("mcq", "multiple_choice", "3/4")
    assert evaluate_attempt(question=question, response=response).outcome == expected


@pytest.mark.parametrize(
    ("response", "expected"),
    [
        ("16 cm", "correct"),
        ("16.005 CM", "correct"),
        ("16 m", "incorrect"),
        ("15 cm", "incorrect"),
        ("sixteen cm", "needs_review"),
    ],
)
def test_numeric_evaluation_requires_value_unit_and_tolerance(response: str, expected: str) -> None:
    question = QuestionSnapshot(
        "numeric", "numeric", "16", accepted_unit="cm", tolerance=Decimal("0.01")
    )
    assert evaluate_attempt(question=question, response=response).outcome == expected
