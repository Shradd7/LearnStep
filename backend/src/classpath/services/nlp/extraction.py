from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from pathlib import Path

import fitz

PIPELINE_VERSION = "synthetic-rules-v1"
CONTENT_TYPES = {
    "heading",
    "explanation",
    "definition",
    "fact",
    "formula",
    "worked_example",
    "activity",
    "question",
    "answer_solution",
    "other",
}

CONCEPT_ALIASES: dict[str, tuple[str, ...]] = {
    "fractions": ("fraction", "numerator", "denominator"),
    "perimeter": ("perimeter", "boundary length"),
    "decimals": ("decimal", "place value"),
    "integers": ("integer", "negative number"),
    "plant_parts": ("plant part", "root", "stem", "leaf"),
    "force_motion": ("force", "motion", "push", "pull"),
    "light_shadows": ("light", "shadow", "opaque"),
    "heat_transfer": ("heat", "conduction", "temperature"),
}


class PdfValidationError(ValueError):
    """A safe, user-facing PDF validation failure."""


@dataclass(frozen=True)
class ExtractedPage:
    page_number: int
    original_text: str


@dataclass(frozen=True)
class ExtractedDocument:
    pages: tuple[ExtractedPage, ...]
    sha256: str
    pipeline_version: str = PIPELINE_VERSION


@dataclass(frozen=True)
class ContentBlock:
    page_number: int
    block_index: int
    original_text: str
    content_type: str
    concept_key: str | None
    confidence: float
    pipeline_version: str = PIPELINE_VERSION


def validate_and_extract_pdf(
    *,
    data: bytes,
    filename: str,
    content_type: str,
    max_bytes: int,
    max_pages: int,
    min_text_chars: int,
) -> ExtractedDocument:
    """Validate untrusted PDF bytes and preserve page-level original text."""

    if Path(filename).suffix.lower() != ".pdf":
        raise PdfValidationError("The upload must use a .pdf extension.")
    if content_type.lower() != "application/pdf":
        raise PdfValidationError("The upload MIME type must be application/pdf.")
    if len(data) > max_bytes:
        raise PdfValidationError("The PDF exceeds the configured demo size limit.")
    if not data.startswith(b"%PDF"):
        raise PdfValidationError("The uploaded bytes are not a PDF.")
    try:
        document = fitz.open(stream=data, filetype="pdf")
    except (fitz.FileDataError, RuntimeError) as error:
        raise PdfValidationError("The PDF is malformed or unsupported.") from error
    try:
        if document.needs_pass:
            raise PdfValidationError("Encrypted PDFs are not supported in the demo.")
        if document.page_count == 0 or document.page_count > max_pages:
            raise PdfValidationError("The PDF page count is outside the configured demo limit.")
        pages = tuple(
            ExtractedPage(page_number=index + 1, original_text=page.get_text("text"))
            for index, page in enumerate(document)
        )
    finally:
        document.close()
    if sum(len(page.original_text.strip()) for page in pages) < min_text_chars:
        raise PdfValidationError("The PDF has too little extractable text; scanned PDFs need OCR.")
    return ExtractedDocument(pages=pages, sha256=hashlib.sha256(data).hexdigest())


def extract_pdf(path: Path) -> ExtractedDocument:
    """Extract a trusted local evaluation fixture using production validation rules."""

    data = path.read_bytes()
    return validate_and_extract_pdf(
        data=data,
        filename=path.name,
        content_type="application/pdf",
        max_bytes=10_000_000,
        max_pages=20,
        min_text_chars=1,
    )


def detect_content_blocks(document: ExtractedDocument) -> list[ContentBlock]:
    """Detect line-oriented synthetic educational content without inventing facts."""

    blocks: list[ContentBlock] = []
    for page in document.pages:
        for raw_line in page.original_text.splitlines():
            line = " ".join(raw_line.split()).strip()
            if not line:
                continue
            content_type, confidence = _classify_line(line)
            concept_key = map_concept(line)
            blocks.append(
                ContentBlock(
                    page_number=page.page_number,
                    block_index=len(blocks),
                    original_text=line,
                    content_type=content_type,
                    concept_key=concept_key,
                    confidence=confidence,
                )
            )
    return blocks


def map_concept(text: str) -> str | None:
    normalized = text.casefold()
    matches = [
        key
        for key, aliases in CONCEPT_ALIASES.items()
        if any(alias in normalized for alias in aliases)
    ]
    return matches[0] if len(matches) == 1 else None


def _classify_line(line: str) -> tuple[str, float]:
    normalized = line.casefold()
    prefixes = {
        "definition:": "definition",
        "fact:": "fact",
        "formula:": "formula",
        "example:": "worked_example",
        "worked example:": "worked_example",
        "activity:": "activity",
        "question:": "question",
        "answer:": "answer_solution",
        "solution:": "answer_solution",
        "explanation:": "explanation",
    }
    for prefix, label in prefixes.items():
        if normalized.startswith(prefix):
            return label, 0.99
    if normalized.startswith(("chapter:", "topic:")) or (line.isupper() and len(line) <= 100):
        return "heading", 0.95
    if re.search(r"\b(is defined as|means)\b", normalized):
        return "definition", 0.8
    return "other", 0.45
