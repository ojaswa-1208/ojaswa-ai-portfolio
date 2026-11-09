
from typing import Any

from qdrant_client import models

from app.config import settings
from app.database.qdrant import get_qdrant_client
from app.services.embedding_service import generate_embedding


DEFAULT_TOP_K = 5
DEFAULT_SCORE_THRESHOLD = 0.30


def retrieve_relevant_chunks(
    question: str,
    top_k: int = DEFAULT_TOP_K,
    score_threshold: float = DEFAULT_SCORE_THRESHOLD,
    source_name: str | None = None,
) -> list[dict[str, Any]]:
    """
    Retrieve relevant knowledge chunks from Qdrant.

    Args:
        question: Visitor's question.
        top_k: Maximum number of chunks to retrieve.
        score_threshold: Minimum cosine similarity score.
        source_name: Optional document name filter.

    Returns:
        Ranked knowledge chunks with their metadata and scores.
    """

    if not question or not question.strip():
        raise ValueError("Question cannot be empty.")

    if not 1 <= top_k <= 20:
        raise ValueError("top_k must be between 1 and 20.")

    if not 0.0 <= score_threshold <= 1.0:
        raise ValueError("score_threshold must be between 0 and 1.")

    client = get_qdrant_client()

    if not client.collection_exists(settings.QDRANT_COLLECTION):
        return []

    query_vector = generate_embedding(question)

    query_filter = None

    if source_name:
        query_filter = models.Filter(
            must=[
                models.FieldCondition(
                    key="source_name",
                    match=models.MatchValue(value=source_name),
                )
            ]
        )

    response = client.query_points(
        collection_name=settings.QDRANT_COLLECTION,
        query=query_vector,
        query_filter=query_filter,
        limit=top_k,
        with_payload=True,
        score_threshold=score_threshold,
    )

    results = []

    for point in response.points:
        payload = point.payload or {}

        results.append(
            {
                "text": payload.get("text", ""),
                "source_name": payload.get("source_name", "unknown"),
                "source_type": payload.get("source_type", "unknown"),
                "source_id": payload.get("source_id", ""),
                "chunk_index": payload.get("chunk_index", -1),
                "score": float(point.score),
            }
        )

    return results


def build_context(
    retrieved_chunks: list[dict[str, Any]],
) -> str:
    """
    Combine retrieved chunks into context for an LLM.

    Source labels are included so the LLM can identify
    where the information came from.
    """

    if not retrieved_chunks:
        return ""

    context_parts = []

    for index, chunk in enumerate(retrieved_chunks, start=1):
        source = chunk.get("source_name", "unknown")
        text = chunk.get("text", "")

        if not text:
            continue

        context_parts.append(
            f"[Source {index}: {source}]\n{text}"
        )

    return "\n\n".join(context_parts)
