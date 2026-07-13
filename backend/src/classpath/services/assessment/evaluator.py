from __future__ import annotations

import re
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Literal


@dataclass(frozen=True)
class QuestionSnapshot:
    question_key: str
    answer_type: Literal["multiple_choice", "numeric"]
    accepted_answer: str
    accepted_unit: str | None = None
    tolerance: Decimal = Decimal("0")
    rubric_version: str = "demo-rubric-v1"


@dataclass(frozen=True)
class EvaluationResult:
    outcome: Literal["correct", "incorrect", "needs_review"]
    confidence: Literal["high", "low"]
    feedback: str
    features: dict[str, object]


def evaluate_attempt(*, question: QuestionSnapshot, response: str) -> EvaluationResult:
    cleaned = " ".join(response.split()).casefold()
    if not cleaned or len(cleaned) > 500:
        return EvaluationResult(
            outcome="needs_review",
            confidence="low",
            feedback="Enter one short answer using the requested format.",
            features={"valid_input": False},
        )
    if question.answer_type == "multiple_choice":
        expected = " ".join(question.accepted_answer.split()).casefold()
        is_correct = cleaned == expected
        return EvaluationResult(
            outcome="correct" if is_correct else "incorrect",
            confidence="high",
            feedback="That matches the reviewed demo answer."
            if is_correct
            else "Try the concept cue, then compare each option.",
            features={"valid_input": True, "normalized_exact_match": is_correct},
        )
    return _evaluate_numeric(question=question, response=cleaned)


def _evaluate_numeric(*, question: QuestionSnapshot, response: str) -> EvaluationResult:
    match = re.fullmatch(r"([-+]?\d+(?:\.\d+)?)\s*([a-zA-Z²^0-9/]*)", response)
    if match is None:
        return EvaluationResult(
            outcome="needs_review",
            confidence="low",
            feedback="Use a number followed by its unit, for example 12 cm.",
            features={"valid_input": False, "numeric_parse": False},
        )
    try:
        actual = Decimal(match.group(1))
        expected = Decimal(question.accepted_answer)
    except InvalidOperation:
        return EvaluationResult(
            "needs_review", "low", "The number could not be parsed.", {"numeric_parse": False}
        )
    actual_unit = match.group(2).casefold().replace("^2", "²") or None
    expected_unit = (
        question.accepted_unit.casefold().replace("^2", "²") if question.accepted_unit else None
    )
    within_tolerance = abs(actual - expected) <= question.tolerance
    unit_matches = actual_unit == expected_unit
    is_correct = within_tolerance and unit_matches
    return EvaluationResult(
        outcome="correct" if is_correct else "incorrect",
        confidence="high",
        feedback=(
            "The value and unit match the reviewed demo answer."
            if is_correct
            else "Check both the calculation and the required unit."
        ),
        features={
            "valid_input": True,
            "numeric_parse": True,
            "within_tolerance": within_tolerance,
            "unit_matches": unit_matches,
        },
    )
