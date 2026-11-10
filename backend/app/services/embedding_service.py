
from functools import lru_cache
from pathlib import Path

import numpy as np
import onnxruntime as ort
from tokenizers import Tokenizer

from app.config import settings


MODEL_DIR = Path(__file__).resolve().parents[1] / "models" / "embedding"
MODEL_PATH = MODEL_DIR / "model.onnx"
TOKENIZER_PATH = MODEL_DIR / "tokenizer.json"

MAX_SEQUENCE_LENGTH = 256
BATCH_SIZE = 32


@lru_cache(maxsize=1)
def get_embedding_runtime():
    """Load the ONNX model and tokenizer once, on first use."""

    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"ONNX model not found: {MODEL_PATH}")

    if not TOKENIZER_PATH.exists():
        raise FileNotFoundError(f"Tokenizer not found: {TOKENIZER_PATH}")

    options = ort.SessionOptions()
    options.intra_op_num_threads = 1
    options.inter_op_num_threads = 1
    options.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL
    options.graph_optimization_level = (
        ort.GraphOptimizationLevel.ORT_ENABLE_ALL
    )

    session = ort.InferenceSession(
        str(MODEL_PATH),
        sess_options=options,
        providers=["CPUExecutionProvider"],
    )

    tokenizer = Tokenizer.from_file(str(TOKENIZER_PATH))
    tokenizer.enable_truncation(max_length=MAX_SEQUENCE_LENGTH)
    tokenizer.enable_padding(
        pad_id=0,
        pad_token="[PAD]",
    )

    return session, tokenizer


def _encode_batch(texts: list[str]) -> list[list[float]]:
    """Generate normalized embeddings using ONNX Runtime."""

    session, tokenizer = get_embedding_runtime()

    encodings = tokenizer.encode_batch(texts)

    input_ids = np.asarray(
        [encoding.ids for encoding in encodings],
        dtype=np.int64,
    )

    attention_mask = np.asarray(
        [encoding.attention_mask for encoding in encodings],
        dtype=np.int64,
    )

    token_type_ids = np.asarray(
        [encoding.type_ids for encoding in encodings],
        dtype=np.int64,
    )

    available_inputs = {
        "input_ids": input_ids,
        "attention_mask": attention_mask,
        "token_type_ids": token_type_ids,
    }

    model_inputs = {}

    for model_input in session.get_inputs():
        name = model_input.name

        if name not in available_inputs:
            raise ValueError(
                f"Unsupported ONNX model input: {name}"
            )

        model_inputs[name] = available_inputs[name]

    outputs = session.run(None, model_inputs)

    if not outputs:
        raise RuntimeError("ONNX model returned no outputs.")

    token_embeddings = np.asarray(outputs[0], dtype=np.float32)

    if token_embeddings.ndim != 3:
        raise ValueError(
            f"Expected 3D token embeddings, got shape "
            f"{token_embeddings.shape}"
        )

    # Attention-mask-aware mean pooling.
    mask = attention_mask.astype(np.float32)[..., np.newaxis]

    summed_embeddings = np.sum(
        token_embeddings * mask,
        axis=1,
    )

    token_counts = np.maximum(
        np.sum(mask, axis=1),
        1e-9,
    )

    pooled_embeddings = summed_embeddings / token_counts

    # L2 normalization, matching the original MiniLM embeddings.
    norms = np.linalg.norm(
        pooled_embeddings,
        axis=1,
        keepdims=True,
    )

    normalized_embeddings = (
        pooled_embeddings / np.maximum(norms, 1e-12)
    )

    embeddings = normalized_embeddings.tolist()

    if any(
        len(vector) != settings.EMBEDDING_DIMENSION
        for vector in embeddings
    ):
        raise ValueError("Embedding dimension mismatch.")

    return embeddings


def generate_embedding(text: str) -> list[float]:
    """Generate one normalized 384-dimensional embedding."""

    if not text or not text.strip():
        raise ValueError("Cannot generate an embedding from empty text.")

    return _encode_batch([text.strip()])[0]


def generate_embeddings(texts: list[str]) -> list[list[float]]:
    """Generate embeddings for multiple documents in small batches."""

    if not texts:
        return []

    if any(not text or not text.strip() for text in texts):
        raise ValueError(
            "All documents must contain non-empty text."
        )

    all_embeddings = []

    for start in range(0, len(texts), BATCH_SIZE):
        batch = [
            text.strip()
            for text in texts[start:start + BATCH_SIZE]
        ]

        all_embeddings.extend(_encode_batch(batch))

    return all_embeddings
