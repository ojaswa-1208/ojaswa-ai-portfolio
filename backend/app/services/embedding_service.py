
from functools import lru_cache

from sentence_transformers import SentenceTransformer

from app.config import settings


@lru_cache(maxsize=1)
def get_embedding_model() -> SentenceTransformer:
    """Load the embedding model once and reuse it."""

    return SentenceTransformer(settings.EMBEDDING_MODEL)


def generate_embedding(text: str) -> list[float]:
    """Convert one text string into a normalized embedding vector."""

    if not text or not text.strip():
        raise ValueError("Cannot generate an embedding from empty text.")

    model = get_embedding_model()

    vector = model.encode(
        text.strip(),
        normalize_embeddings=True,
        convert_to_numpy=True,
        show_progress_bar=False,
    )

    embedding = vector.tolist()

    if len(embedding) != settings.EMBEDDING_DIMENSION:
        raise ValueError(
            f"Expected {settings.EMBEDDING_DIMENSION} dimensions, "
            f"received {len(embedding)}."
        )

    return embedding


def generate_embeddings(texts: list[str]) -> list[list[float]]:
    """Generate embeddings for multiple text documents."""

    if not texts:
        return []

    if any(not text.strip() for text in texts):
        raise ValueError("All documents must contain non-empty text.")

    model = get_embedding_model()

    vectors = model.encode(
        texts,
        normalize_embeddings=True,
        convert_to_numpy=True,
        show_progress_bar=False,
        batch_size=32,
    )

    embeddings = vectors.tolist()

    if any(
        len(vector) != settings.EMBEDDING_DIMENSION
        for vector in embeddings
    ):
        raise ValueError("Embedding dimension mismatch.")

    return embeddings
