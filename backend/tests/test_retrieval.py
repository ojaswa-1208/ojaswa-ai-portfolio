
import pytest

from app.services.retrieval_service import (
    retrieve_relevant_chunks,
    build_context,
)


def test_reject_empty_question():
    with pytest.raises(ValueError):
        retrieve_relevant_chunks("")


def test_reject_invalid_top_k():
    with pytest.raises(ValueError):
        retrieve_relevant_chunks(
            "What projects has Ojaswa built?",
            top_k=0,
        )


def test_reject_invalid_score_threshold():
    with pytest.raises(ValueError):
        retrieve_relevant_chunks(
            "Tell me about Ojaswa",
            score_threshold=1.5,
        )


def test_build_context_with_results():
    chunks = [
        {
            "text": "Ojaswa built an AI Retention Diagnosis project.",
            "source_name": "projects.md",
        },
        {
            "text": "The project uses Python and Random Forest.",
            "source_name": "resume.pdf",
        },
    ]

    context = build_context(chunks)

    assert "AI Retention Diagnosis" in context
    assert "Python" in context
    assert "projects.md" in context
    assert "resume.pdf" in context


def test_build_context_without_results():
    assert build_context([]) == ""
