"""Generate original synthetic evaluation data; no curriculum source is imported."""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import TypedDict

import fitz

ROOT = Path(__file__).resolve().parents[1]
SYNTHETIC_ROOT = ROOT / "data" / "synthetic"


class ConceptSpec(TypedDict):
    key: str
    title: str
    class_level: int
    subject: str
    lines: list[tuple[str, str]]


CONCEPTS: list[ConceptSpec] = [
    {
        "key": "fractions",
        "title": "Fractions as Equal Parts",
        "class_level": 5,
        "subject": "mathematics",
        "lines": [
            ("definition", "Definition: A fraction describes selected equal parts of a whole."),
            ("explanation", "Explanation: In a fraction, the denominator counts all equal parts."),
            ("formula", "Formula: fraction = selected equal parts / all equal parts."),
            ("worked_example", "Example: Three selected parts out of four equal parts form 3/4."),
            ("activity", "Activity: Fold a strip into equal parts and label one fraction."),
            ("question", "Question: Which fraction names one selected part out of four?"),
            ("answer_solution", "Solution: One selected part out of four is the fraction 1/4."),
        ],
    },
    {
        "key": "perimeter",
        "title": "Perimeter and Boundary Length",
        "class_level": 5,
        "subject": "mathematics",
        "lines": [
            ("definition", "Definition: Perimeter is the total boundary length of a shape."),
            ("explanation", "Explanation: Add every side length using the same unit."),
            ("formula", "Formula: rectangle perimeter = 2 x (length + width)."),
            ("worked_example", "Example: Sides 5 cm and 3 cm give a perimeter of 16 cm."),
            ("activity", "Activity: Measure a book cover and estimate its perimeter."),
            ("question", "Question: Find the perimeter of a 4 cm by 2 cm rectangle."),
            ("answer_solution", "Solution: The perimeter is 4 + 2 + 4 + 2 = 12 cm."),
        ],
    },
    {
        "key": "decimals",
        "title": "Decimal Place Value",
        "class_level": 6,
        "subject": "mathematics",
        "lines": [
            ("definition", "Definition: A decimal uses place value to show parts of one whole."),
            ("explanation", "Explanation: The first decimal place represents tenths."),
            ("formula", "Formula: 0.1 = one tenth."),
            ("worked_example", "Example: In 2.5, the digit 5 has a place value of five tenths."),
            ("activity", "Activity: Mark the decimal 0.4 on a line from zero to one."),
            ("question", "Question: What place value does 7 have in the decimal 3.7?"),
            ("answer_solution", "Solution: The digit 7 represents seven tenths."),
        ],
    },
    {
        "key": "integers",
        "title": "Positive and Negative Integers",
        "class_level": 7,
        "subject": "mathematics",
        "lines": [
            ("definition", "Definition: An integer is a whole number, its negative, or zero."),
            ("explanation", "Explanation: A negative number lies left of zero on a number line."),
            ("formula", "Formula: adding an opposite integer gives zero, such as 4 + (-4) = 0."),
            ("worked_example", "Example: Moving three steps left from zero reaches integer -3."),
            ("activity", "Activity: Place five positive and negative numbers on a line."),
            ("question", "Question: Which integer is two steps left of zero?"),
            ("answer_solution", "Solution: The integer two steps left of zero is -2."),
        ],
    },
    {
        "key": "plant_parts",
        "title": "Plant Parts and Functions",
        "class_level": 6,
        "subject": "science",
        "lines": [
            (
                "definition",
                "Definition: A plant part is a structure such as a root, stem, or leaf.",
            ),
            ("fact", "Fact: In this example, a root anchors a plant and takes in water."),
            ("explanation", "Explanation: A stem supports leaves and connects plant parts."),
            ("worked_example", "Example: Water entering a root can move through the stem."),
            ("activity", "Activity: Label the root, stem, and leaf on a drawing."),
            ("question", "Question: Which plant part is described as taking in water?"),
            ("answer_solution", "Solution: The described plant part is the root."),
        ],
    },
    {
        "key": "force_motion",
        "title": "Force and Motion",
        "class_level": 7,
        "subject": "science",
        "lines": [
            ("definition", "Definition: A force is a push or pull acting on an object."),
            ("fact", "Fact: A force can change an object's motion."),
            ("explanation", "Explanation: The effect depends on the direction of a push or pull."),
            ("worked_example", "Example: A push can start a stationary toy car moving."),
            ("activity", "Activity: Observe how different pushes change a ball's motion."),
            ("question", "Question: What kind of action can change an object's motion?"),
            (
                "answer_solution",
                "Solution: A force, described as a push or pull, can change motion.",
            ),
        ],
    },
    {
        "key": "light_shadows",
        "title": "Light and Shadows",
        "class_level": 6,
        "subject": "science",
        "lines": [
            ("definition", "Definition: A shadow is a dark region where light is blocked."),
            ("fact", "Fact: An opaque object blocks most light in this example."),
            ("explanation", "Explanation: A shadow forms on the side away from the light source."),
            ("worked_example", "Example: A card between a lamp and wall produces a shadow."),
            ("activity", "Activity: Move an opaque card and observe the shadow position."),
            ("question", "Question: What must be blocked for a shadow to form?"),
            ("answer_solution", "Solution: The object blocks light, creating a shadow."),
        ],
    },
    {
        "key": "heat_transfer",
        "title": "Heat Transfer",
        "class_level": 8,
        "subject": "science",
        "lines": [
            (
                "definition",
                "Definition: Heat transfer is energy moving because of a temperature difference.",
            ),
            ("fact", "Fact: Conduction transfers heat through direct contact in this example."),
            (
                "explanation",
                "Explanation: Energy moves from a warmer region toward a cooler region.",
            ),
            ("worked_example", "Example: A metal spoon warms by conduction in hot water."),
            ("activity", "Activity: Compare heat transfer through two safe material samples."),
            ("question", "Question: Which heat process occurs through direct contact?"),
            ("answer_solution", "Solution: The described heat process is conduction."),
        ],
    },
]


def generate_pdf(path: Path, *, spec: ConceptSpec, layout: int, serial: int) -> None:
    document = fitz.open()
    page = document.new_page()
    y = 60.0
    heading = f"CHAPTER: {spec['title']} - SYNTHETIC DEMO {serial:02d}"
    page.insert_text((50 + layout * 8, y), heading, fontsize=13 + layout)
    y += 34
    for index, (_, line) in enumerate(spec["lines"]):
        if layout == 2 and index == 4:
            page = document.new_page()
            y = 70
        page.insert_text((50 + layout * 8, y), line, fontsize=10 + (layout % 2))
        y += 28 + layout * 3
    document.set_metadata(
        {
            "title": heading,
            "author": "LearnStep synthetic evaluation generator",
            "subject": "Original synthetic content; not reviewed curriculum",
        }
    )
    document.save(path)
    document.close()


def generate_questions() -> list[dict[str, object]]:
    cognitive_templates = {
        "remember": ["State the meaning of {title}.", "Recall one stated fact about {title}."],
        "understand": ["Explain {title} in your own words.", "Compare two ideas within {title}."],
        "apply": [
            "Use the stated rule for {title} in a familiar example.",
            "Apply {title} to solve a concrete case.",
        ],
        "analyse": [
            "Analyse a claim about {title} and justify each step.",
            "Find and explain an error in reasoning about {title}.",
        ],
    }
    difficulty_additions = {
        "foundational": " Use one direct idea.",
        "intermediate": " Connect two stated steps.",
        "challenge": " Consider an unfamiliar but in-scope case.",
    }
    rows: list[dict[str, object]] = []
    for concept in CONCEPTS:
        for cognitive, templates in cognitive_templates.items():
            for template_index, template in enumerate(templates):
                for difficulty, addition in difficulty_additions.items():
                    for variant in range(2):
                        family = f"{cognitive}-{template_index}-{difficulty}-{variant}"
                        rows.append(
                            {
                                "question_id": f"syn-{concept['key']}-{family}",
                                "text": template.format(title=concept["title"]) + addition,
                                "class_level": concept["class_level"],
                                "subject": concept["subject"],
                                "topic_id": concept["key"],
                                "cognitive_level": cognitive,
                                "difficulty": difficulty,
                                "answer_type": "explanation",
                                "source_id": "learnstep-original-synthetic-v1",
                                "license": "project-original-synthetic",
                                "is_synthetic": True,
                                "template_group_id": family,
                                "review_status": "unreviewed_synthetic",
                            }
                        )
    return rows


def main() -> None:
    pdf_root = SYNTHETIC_ROOT / "evaluation" / "pdfs"
    sample_root = SYNTHETIC_ROOT / "samples"
    pdf_root.mkdir(parents=True, exist_ok=True)
    sample_root.mkdir(parents=True, exist_ok=True)
    annotations: list[dict[str, object]] = []
    for serial in range(60):
        spec = CONCEPTS[serial % len(CONCEPTS)]
        filename = f"synthetic_chapter_{serial + 1:02d}_{spec['key']}.pdf"
        path = pdf_root / filename
        generate_pdf(path, spec=spec, layout=serial % 3, serial=serial + 1)
        annotations.append(
            {
                "document_id": f"synthetic-{serial + 1:02d}",
                "filename": filename,
                "class_level": spec["class_level"],
                "subject": spec["subject"],
                "concept_keys": [spec["key"]],
                "content_types": ["heading", *[label for label, _ in spec["lines"]]],
                "layout_family": f"synthetic-layout-{serial % 3 + 1}",
                "source_id": "learnstep-original-synthetic-v1",
                "review_status": "unreviewed_synthetic",
            }
        )
        if serial < 3:
            shutil.copyfile(path, sample_root / filename)
    annotation_path = SYNTHETIC_ROOT / "evaluation" / "annotations.json"
    annotation_path.write_text(json.dumps(annotations, indent=2) + "\n", encoding="utf-8")
    questions = generate_questions()
    question_path = SYNTHETIC_ROOT / "questions.jsonl"
    question_path.write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in questions), encoding="utf-8"
    )
    review_path = SYNTHETIC_ROOT / "human_review_queue.jsonl"
    review_rows = [
        {
            "review_item_id": f"package-review-{index + 1:03d}",
            "source_question_id": questions[index]["question_id"],
            "checks": {
                "source_supported": None,
                "class_appropriate": None,
                "clear_and_answerable": None,
                "answer_and_rubric_correct": None,
                "hints_do_not_reveal_answer": None,
                "no_invented_claim": None,
            },
            "review_status": "pending_human_review",
            "reviewer": None,
            "notes": None,
        }
        for index in range(100)
    ]
    review_path.write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in review_rows),
        encoding="utf-8",
    )
    print(f"Generated {len(annotations)} PDFs, {len(questions)} questions, and 100 review items")


if __name__ == "__main__":
    main()
