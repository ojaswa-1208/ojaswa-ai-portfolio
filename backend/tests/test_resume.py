
import fitz
import pytest

from app.services.resume_parser import (
    extract_pdf_text,
    ResumeProcessingError,
)


def create_test_pdf():
    document = fitz.open()

    page = document.new_page()

    page.insert_text(
        (72, 72),
        "Ojaswa Mahobiya - AI Engineer"
    )

    pdf_bytes = document.tobytes()

    document.close()

    return pdf_bytes


def test_extract_valid_pdf():

    pdf_bytes = create_test_pdf()

    result = extract_pdf_text(pdf_bytes)

    assert "Ojaswa Mahobiya" in result
    assert "AI Engineer" in result


def test_reject_empty_pdf():

    with pytest.raises(ResumeProcessingError):
        extract_pdf_text(b"")


def test_reject_invalid_pdf():

    with pytest.raises(ResumeProcessingError):
        extract_pdf_text(b"This is not a PDF")


def test_reject_oversized_pdf():

    pdf_bytes = b"%PDF-" + b"A" * (5 * 1024 * 1024)

    with pytest.raises(ResumeProcessingError):
        extract_pdf_text(pdf_bytes)


def test_reject_pdf_without_readable_text():

    document = fitz.open()
    document.new_page()

    pdf_bytes = document.tobytes()

    document.close()

    with pytest.raises(ResumeProcessingError):
        extract_pdf_text(pdf_bytes)
