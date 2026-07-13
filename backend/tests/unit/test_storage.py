from pathlib import Path

import pytest

from classpath.services.storage import delete_pdf, safe_display_name, store_pdf


def test_storage_ignores_untrusted_filename_and_deletes_generated_key(tmp_path: Path) -> None:
    assert safe_display_name("../../private/student-name.pdf") == "student-name.pdf"
    key = store_pdf(root=tmp_path, data=b"%PDF synthetic")

    assert key.endswith(".pdf")
    assert (tmp_path / key).read_bytes() == b"%PDF synthetic"
    delete_pdf(root=tmp_path, storage_key=key)
    assert not (tmp_path / key).exists()


def test_delete_rejects_non_generated_storage_key(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="Unsafe"):
        delete_pdf(root=tmp_path, storage_key="../outside.pdf")
