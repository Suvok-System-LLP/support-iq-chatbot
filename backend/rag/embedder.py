"""Vertex AI text embedding wrapper using text-embedding-004."""

import logging
import os
import time

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT", "")
_REGION = os.getenv("GOOGLE_CLOUD_REGION", "australia-southeast1")
_MODEL_NAME = os.getenv("EMBEDDING_MODEL", "text-embedding-004")

_embedding_model = None  # lazy-initialised


def _get_model():
    """Lazily initialise the Vertex AI TextEmbeddingModel."""
    global _embedding_model  # noqa: PLW0603
    if _embedding_model is None:
        from vertexai.language_models import TextEmbeddingModel  # noqa: PLC0415
        import vertexai  # noqa: PLC0415

        vertexai.init(project=_PROJECT, location=_REGION)
        _embedding_model = TextEmbeddingModel.from_pretrained(_MODEL_NAME)
        logger.info("Loaded embedding model: %s", _MODEL_NAME)
    return _embedding_model


def embed_text(text: str) -> list[float]:
    """Embed a single string and return a vector of floats.

    Parameters
    ----------
    text:
        The input text to embed.

    Returns
    -------
    list[float]
        Embedding vector.
    """
    model = _get_model()
    for attempt in range(1, 4):
        try:
            embeddings = model.get_embeddings([text])
            return embeddings[0].values
        except Exception as exc:
            if attempt == 3:
                logger.error("Embedding failed after 3 attempts: %s", exc)
                raise
            logger.warning("Embedding attempt %d failed: %s — retrying in 2s", attempt, exc)
            time.sleep(2)
    # unreachable, but satisfies type checkers
    return []


def embed_batch(texts: list[str], batch_size: int = 5) -> list[list[float]]:
    """Embed a list of strings in batches to avoid rate limits.

    Parameters
    ----------
    texts:
        List of strings to embed.
    batch_size:
        Number of texts per API call.

    Returns
    -------
    list[list[float]]
        A list of embedding vectors in the same order as the input.
    """
    model = _get_model()
    all_embeddings: list[list[float]] = []

    try:
        from tqdm import tqdm  # noqa: PLC0415

        iterator = tqdm(
            range(0, len(texts), batch_size),
            desc="Embedding",
            unit="batch",
        )
    except ImportError:
        iterator = range(0, len(texts), batch_size)

    for start in iterator:
        batch = texts[start : start + batch_size]
        for attempt in range(1, 4):
            try:
                embeddings = model.get_embeddings(batch)
                all_embeddings.extend(e.values for e in embeddings)
                break
            except Exception as exc:
                if attempt == 3:
                    logger.error(
                        "Batch embedding failed after 3 attempts (batch starting at %d): %s",
                        start,
                        exc,
                    )
                    raise
                logger.warning(
                    "Batch embedding attempt %d failed (batch %d): %s — retrying in 2s",
                    attempt,
                    start,
                    exc,
                )
                time.sleep(2)

    logger.info("Embedded %d texts in batches of %d", len(texts), batch_size)
    return all_embeddings
