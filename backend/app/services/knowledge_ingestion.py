
import hashlib
import logging
import uuid

from datetime import datetime, timezone
from pathlib import Path

from qdrant_client import models

from app.config import settings
from app.database.qdrant import (
    get_qdrant_client,
    initialize_collection,
)
from app.services.embedding_service import generate_embeddings
from app.services.resume_parser import extract_pdf_text


logger = logging.getLogger(__name__)

KNOWLEDGE_DIR = Path("knowledge")

SUPPORTED_EXTENSIONS = {".pdf", ".md", ".txt"}

MAX_CHUNK_SIZE = 1200
CHUNK_OVERLAP = 200


def clean_text(text: str) -> str:
    """Normalize whitespace in extracted documents."""

    return " ".join(text.split())


def split_into_chunks(
    text: str,
    chunk_size: int = MAX_CHUNK_SIZE,
    overlap: int = CHUNK_OVERLAP,
) -> list[str]:
    """Split text into overlapping chunks without cutting words."""

    text = clean_text(text)

    if not text:
        return []

    if chunk_size <= 0:
        raise ValueError("Chunk size must be positive.")

    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("Overlap must be smaller than chunk size.")

    chunks = []
    start = 0

    while start < len(text):
        end = min(start + chunk_size, len(text))

        if end < len(text):
            boundary = text.rfind(
                " ",
                start + chunk_size // 2,
                end,
            )

            if boundary > start:
                end = boundary

        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end >= len(text):
            break

        start = max(end - overlap, start + 1)

    return chunks


def read_document(file_path: Path) -> str:
    """Read supported document formats."""

    extension = file_path.suffix.lower()

    if extension == ".pdf":
        return extract_pdf_text(file_path.read_bytes())

    if extension in {".md", ".txt"}:
        return file_path.read_text(encoding="utf-8-sig")

    raise ValueError(
        f"Unsupported document format: {extension}"
    )


def get_source_id(file_path: Path) -> str:
    """Generate a stable identifier for a document."""

    resolved_path = str(file_path.resolve())

    return hashlib.sha256(
        resolved_path.encode("utf-8")
    ).hexdigest()


def get_existing_source_point_ids(
    source_id: str,
) -> list[str]:
    """Retrieve existing point IDs belonging to one document."""

    client = get_qdrant_client()

    existing_ids = []
    offset = None

    while True:
        records, next_offset = client.scroll(
            collection_name=settings.QDRANT_COLLECTION,
            scroll_filter=models.Filter(
                must=[
                    models.FieldCondition(
                        key="source_id",
                        match=models.MatchValue(
                            value=source_id
                        ),
                    )
                ]
            ),
            limit=256,
            offset=offset,
            with_payload=False,
            with_vectors=False,
        )

        existing_ids.extend(
            str(record.id) for record in records
        )

        if next_offset is None:
            break

        offset = next_offset

    return existing_ids


def remove_stale_source_points(
    source_id: str,
    new_point_ids: set[str],
) -> int:
    """
    Delete outdated chunks only after successful upsert.

    Newly uploaded points are preserved.
    """

    client = get_qdrant_client()

    existing_ids = get_existing_source_point_ids(
        source_id
    )

    stale_ids = [
        point_id
        for point_id in existing_ids
        if point_id not in new_point_ids
    ]

    if not stale_ids:
        return 0

    client.delete(
        collection_name=settings.QDRANT_COLLECTION,
        points_selector=models.PointIdsList(
            points=stale_ids
        ),
        wait=True,
    )

    return len(stale_ids)


def ingest_document(
    file_path: str | Path,
) -> dict:
    """Extract, chunk, embed and safely index one document."""

    path = Path(file_path)

    if not path.is_file():
        raise FileNotFoundError(
            f"Document not found: {path}"
        )

    if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        raise ValueError(
            "Only PDF, Markdown and TXT files are supported."
        )

    logger.info(
        "Starting document ingestion: %s",
        path.name,
    )

    initialize_collection()

    extracted_text = read_document(path)
    chunks = split_into_chunks(extracted_text)

    if not chunks:
        raise ValueError(
            f"No readable text found in {path.name}"
        )

    embeddings = generate_embeddings(chunks)

    if len(chunks) != len(embeddings):
        raise ValueError(
            "Chunk and embedding counts do not match."
        )

    for index, embedding in enumerate(embeddings):
        if len(embedding) != settings.EMBEDDING_DIMENSION:
            raise ValueError(
                f"Invalid embedding dimension at index {index}: "
                f"expected {settings.EMBEDDING_DIMENSION}, "
                f"received {len(embedding)}."
            )

    source_id = get_source_id(path)

    content_hash = hashlib.sha256(
        extracted_text.encode("utf-8")
    ).hexdigest()

    timestamp = datetime.now(
        timezone.utc
    ).isoformat()

    points = []

    for index, (chunk, embedding) in enumerate(
        zip(chunks, embeddings)
    ):
        chunk_hash = hashlib.sha256(
            chunk.encode("utf-8")
        ).hexdigest()

        point_identity = (
            f"{source_id}:{index}:{chunk_hash}"
        )

        point_id = str(
            uuid.uuid5(
                uuid.NAMESPACE_URL,
                point_identity,
            )
        )

        points.append(
            models.PointStruct(
                id=point_id,
                vector=embedding,
                payload={
                    "text": chunk,
                    "source_id": source_id,
                    "source_name": path.name,
                    "source_type": path.suffix.lower().lstrip("."),
                    "chunk_index": index,
                    "content_hash": content_hash,
                    "indexed_at": timestamp,
                },
            )
        )

    client = get_qdrant_client()

    # Step 1: Upload new/current chunks first.
    # If this fails, existing document points remain untouched.
    client.upsert(
        collection_name=settings.QDRANT_COLLECTION,
        points=points,
        wait=True,
    )

    new_point_ids = {
        str(point.id) for point in points
    }

    # Step 2: Remove outdated chunks only after successful upload.
    removed_stale_vectors = remove_stale_source_points(
        source_id,
        new_point_ids,
    )

    result = {
        "success": True,
        "source": path.name,
        "source_id": source_id,
        "total_characters": len(extracted_text),
        "total_chunks": len(chunks),
        "total_vectors": len(embeddings),
        "removed_stale_vectors": removed_stale_vectors,
    }

    logger.info(
        "Document ingestion completed: %s",
        result,
    )

    return result


def ingest_knowledge_directory(
    directory: str | Path = KNOWLEDGE_DIR,
) -> list[dict]:
    """Index all supported documents inside the knowledge directory."""

    folder = Path(directory)

    if not folder.exists():
        raise FileNotFoundError(
            f"Knowledge directory does not exist: {folder}"
        )

    documents = sorted(
        path
        for path in folder.rglob("*")
        if path.is_file()
        and path.suffix.lower() in SUPPORTED_EXTENSIONS
    )

    if not documents:
        raise ValueError(
            "No supported knowledge documents were found."
        )

    results = []

    for document in documents:
        results.append(
            ingest_document(document)
        )

    return results
