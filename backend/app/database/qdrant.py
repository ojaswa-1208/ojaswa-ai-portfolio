
import atexit

from qdrant_client import QdrantClient, models

from app.config import settings


_client: QdrantClient | None = None


def get_qdrant_client() -> QdrantClient:
    """Return one persistent authenticated Qdrant Cloud client."""

    global _client

    if _client is None:
        _client = QdrantClient(
            url=settings.QDRANT_URL,
            api_key=settings.QDRANT_API_KEY,
            timeout=settings.QDRANT_TIMEOUT_SECONDS,
        )

    return _client


def close_qdrant_client() -> None:
    """Close the Qdrant client cleanly."""

    global _client

    if _client is not None:
        _client.close()
        _client = None


atexit.register(close_qdrant_client)


def verify_qdrant_connection() -> dict:
    """Verify authentication and connectivity to Qdrant Cloud."""

    client = get_qdrant_client()

    try:
        response = client.get_collections()

        return {
            "success": True,
            "message": "Successfully connected to Qdrant Cloud.",
            "collection_count": len(response.collections),
        }

    except Exception as exc:
        raise ConnectionError(
            "Unable to connect to Qdrant Cloud. "
            "Check your QDRANT_URL, QDRANT_API_KEY, "
            "network connection and cluster status."
        ) from exc


def _get_vector_params(vectors_config):
    """Return vector parameters for a single dense vector."""

    if isinstance(vectors_config, models.VectorParams):
        return vectors_config

    if isinstance(vectors_config, dict):
        if len(vectors_config) != 1:
            raise ValueError(
                "Expected exactly one dense vector in Qdrant collection. "
                f"Found: {list(vectors_config.keys())}"
            )

        return next(iter(vectors_config.values()))

    raise ValueError(
        "Unsupported Qdrant vector configuration: "
        f"{type(vectors_config).__name__}"
    )


def ensure_payload_index(field_name: str) -> None:
    """Ensure a payload field has a KEYWORD index."""

    client = get_qdrant_client()
    collection_name = settings.QDRANT_COLLECTION

    info = client.get_collection(collection_name)
    payload_schema = info.payload_schema or {}

    if field_name not in payload_schema:
        client.create_payload_index(
            collection_name=collection_name,
            field_name=field_name,
            field_schema=models.PayloadSchemaType.KEYWORD,
            wait=True,
        )


def ensure_source_id_index() -> None:
    """Ensure source_id has a KEYWORD payload index."""

    ensure_payload_index("source_id")


def ensure_source_name_index() -> None:
    """Ensure source_name has a KEYWORD payload index."""

    ensure_payload_index("source_name")


def initialize_collection() -> None:
    """Create or validate the collection and its payload indexes."""

    client = get_qdrant_client()
    collection_name = settings.QDRANT_COLLECTION

    if not client.collection_exists(collection_name):
        client.create_collection(
            collection_name=collection_name,
            vectors_config=models.VectorParams(
                size=settings.EMBEDDING_DIMENSION,
                distance=models.Distance.COSINE,
            ),
        )

    info = client.get_collection(collection_name)

    vector_params = _get_vector_params(
        info.config.params.vectors
    )

    if vector_params.size != settings.EMBEDDING_DIMENSION:
        raise ValueError(
            f"Collection '{collection_name}' has an incompatible "
            f"vector dimension. Expected {settings.EMBEDDING_DIMENSION}, "
            f"found {vector_params.size}."
        )

    if vector_params.distance != models.Distance.COSINE:
        raise ValueError(
            f"Collection '{collection_name}' must use COSINE distance."
        )

    ensure_source_id_index()
    ensure_source_name_index()


def get_collection_info() -> dict:
    """Return information about the portfolio collection."""

    client = get_qdrant_client()
    collection_name = settings.QDRANT_COLLECTION

    if not client.collection_exists(collection_name):
        return {
            "exists": False,
            "collection": collection_name,
            "points_count": 0,
        }

    info = client.get_collection(collection_name)

    vector_params = _get_vector_params(
        info.config.params.vectors
    )

    payload_schema = info.payload_schema or {}

    return {
        "exists": True,
        "collection": collection_name,
        "points_count": info.points_count or 0,
        "status": str(info.status),
        "vector_dimension": vector_params.size,
        "distance": str(vector_params.distance),
        "source_id_indexed": "source_id" in payload_schema,
        "source_name_indexed": "source_name" in payload_schema,
    }
