from __future__ import annotations

import fitz
import pytest

from classpath.services.nlp.extraction import (
    ExtractedDocument,
    PdfValidationError,
    detect_content_blocks,
    validate_and_extract_pdf,
)


def make_pdf(*, text: str | None = None, pages: int = 1, encrypted: bool = False) -> bytes:
    document = fitz.open()
    for _ in range(pages):
        page = document.new_page()
        if text:
            page.insert_text((72, 72), text)
    if encrypted:
        data = bytes(
            document.tobytes(
                encryption=fitz.PDF_ENCRYPT_AES_256,
                owner_pw="owner-test-only",
                user_pw="reader-test-only",
            )
        )
    else:
        data = bytes(document.tobytes())
    document.close()
    return data


def extract(
    data: bytes, *, filename: str = "synthetic.pdf", mime: str = "application/pdf"
) -> ExtractedDocument:
    return validate_and_extract_pdf(
        data=data,
        filename=filename,
        content_type=mime,
        max_bytes=100_000,
        max_pages=2,
        min_text_chars=20,
    )


def test_extracts_original_text_content_type_and_concept() -> None:
    document = extract(make_pdf(text="CHAPTER: FRACTIONS\nDefinition: A fraction has equal parts."))
    blocks = detect_content_blocks(document)

    assert [block.content_type for block in blocks] == ["heading", "definition"]
    assert blocks[1].concept_key == "fractions"
    assert blocks[1].original_text == "Definition: A fraction has equal parts."


@pytest.mark.parametrize(
    ("data", "filename", "mime", "message"),
    [
        (b"not a pdf", "fake.pdf", "application/pdf", "not a PDF"),
        (
            make_pdf(text="Enough readable synthetic content."),
            "fake.txt",
            "application/pdf",
            ".pdf",
        ),
        (make_pdf(text="Enough readable synthetic content."), "fake.pdf", "text/plain", "MIME"),
    ],
)
def test_rejects_spoofed_uploads(data: bytes, filename: str, mime: str, message: str) -> None:
    with pytest.raises(PdfValidationError, match=message):
        extract(data, filename=filename, mime=mime)


def test_rejects_encrypted_image_only_and_too_many_pages() -> None:
    with pytest.raises(PdfValidationError, match="Encrypted"):
        extract(make_pdf(text="Secret synthetic text", encrypted=True))
    with pytest.raises(PdfValidationError, match="too little"):
        extract(make_pdf())
    with pytest.raises(PdfValidationError, match="page count"):
        extract(make_pdf(text="Readable synthetic text on each page", pages=3))
