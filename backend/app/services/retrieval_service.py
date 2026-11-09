import time
from typing import Any

from qdrant_client import models

from app.config import settings
from app.core.logging import logger
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

    started_at = time.perf_counter()
    logger.info("retrieval_started")

    if not question or not question.strip():
        raise ValueError("Question cannot be empty.")

    if not 1 <= top_k <= 20:
        raise ValueError("top_k must be between 1 and 20.")

    if not 0.0 <= score_threshold <= 1.0:
        raise ValueError("score_threshold must be between 0 and 1.")

    try:
        logger.info("qdrant_client_initializing")
        client = get_qdrant_client()
        logger.info("qdrant_client_ready")

        logger.info("qdrant_collection_check_started")
        collection_exists = client.collection_exists(
            settings.QDRANT_COLLECTION
        )
        logger.info(
            "qdrant_collection_check_completed",
            exists=collection_exists,
        )

        if not collection_exists:
            logger.warning("qdrant_collection_not_found")
            return []

        logger.info("embedding_generation_started")
        embedding_started_at = time.perf_counter()

        query_vector = generate_embedding(question)

        embedding_duration = round(
            time.perf_counter() - embedding_started_at,
            3,
        )

        logger.info(
            "embedding_generation_completed",
            dimensions=len(query_vector),
            duration_seconds=embedding_duration,
        )

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

        logger.info("qdrant_vector_search_started")

        response = client.query_points(
            collection_name=settings.QDRANT_COLLECTION,
            query=query_vector,
            query_filter=query_filter,
            limit=top_k,
            with_payload=True,
            score_threshold=score_threshold,
        )

        logger.info(
            "qdrant_vector_search_completed",
            result_count=len(response.points),
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

        logger.info(
            "retrieval_completed",
            result_count=len(results),
            duration_seconds=round(
                time.perf_counter() - started_at,
                3,
            ),
        )

        return results

    except Exception as exc:
        logger.exception(
            "retrieval_failed",
            error_type=type(exc).__name__,
        )
        raise


def build_context(
    retrieved_chunks: list[dict[str, Any]],
) -> str:

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