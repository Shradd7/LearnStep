import re
from pathlib import Path
from uuid import uuid4

SAFE_STORAGE_KEY = re.compile(r"^[0-9a-f]{32}\.pdf$")


def safe_display_name(filename: str) -> str:
    base = Path(filename.replace("\\", "/")).name
    cleaned = "".join(character for character in base if character.isalnum() or character in " ._-")
    return (cleaned.strip() or "demo-upload.pdf")[:160]


def store_pdf(*, root: Path, data: bytes) -> str:
    root.mkdir(parents=True, exist_ok=True)
    storage_key = f"{uuid4().hex}.pdf"
    (root / storage_key).write_bytes(data)
    return storage_key


def delete_pdf(*, root: Path, storage_key: str) -> None:
    if not SAFE_STORAGE_KEY.fullmatch(storage_key):
        raise ValueError("Unsafe storage key")
    path = root.resolve() / storage_key
    path.unlink(missing_ok=True)
