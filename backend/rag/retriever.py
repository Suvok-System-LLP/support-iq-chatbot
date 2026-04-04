"""Vertex AI Vector Search retriever with local chunk store fallback."""

import json
import logging
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT", "")
_REGION = os.getenv("GOOGLE_CLOUD_REGION", "australia-southeast1")
_INDEX_ENDPOINT_ID = os.getenv("VERTEX_INDEX_ENDPOINT_ID", "")
_DEPLOYED_INDEX_ID = os.getenv("VERTEX_DEPLOYED_INDEX_ID", "")

# Path to the local chunk metadata store written by ingest_docs.py.
# Search multiple locations: Docker image first, then local dev paths.
_CHUNK_STORE_CANDIDATES = [
    Path("/app/chunk_store.json"),                                  # Cloud Run Docker
    Path(__file__).parent.parent.parent / "knowledge" / "chunk_store.json",  # local dev
    Path("knowledge") / "chunk_store.json",                         # fallback
]
_CHUNK_STORE_PATH = next((p for p in _CHUNK_STORE_CANDIDATES if p.exists()), _CHUNK_STORE_CANDIDATES[0])

# In-memory chunk store: id -> chunk dict
CHUNK_STORE: dict[str, dict] = {}

_store_loaded = False


def _load_chunk_store() -> None:
    """Load chunk_store.json into memory (called once at first search)."""
    global _store_loaded  # noqa: PLW0603
    if _store_loaded:
        return
    _store_loaded = True

    if not _CHUNK_STORE_PATH.exists():
        logger.warning(
            "chunk_store.json not found at %s — retriever will return empty results. "
            "Run scripts/ingest_docs.py to build the index.",
            _CHUNK_STORE_PATH,
        )
        return

    try:
        data = json.loads(_CHUNK_STORE_PATH.read_text(encoding="utf-8"))
        CHUNK_STORE.update(data)
        logger.info("Loaded %d chunks from chunk_store.json", len(CHUNK_STORE))
    except Exception as exc:
        logger.error("Failed to load chunk_store.json: %s", exc)


_endpoint = None  # lazy-initialised


def _get_endpoint():
    """Lazily initialise the Vertex AI MatchingEngineIndexEndpoint."""
    global _endpoint  # noqa: PLW0603
    if _endpoint is None:
        from google.cloud import aiplatform  # noqa: PLC0415

        aiplatform.init(project=_PROJECT, location=_REGION)
        _endpoint = aiplatform.MatchingEngineIndexEndpoint(
            index_endpoint_name=_INDEX_ENDPOINT_ID
        )
        logger.info("Connected to Vertex AI index endpoint: %s", _INDEX_ENDPOINT_ID)
    return _endpoint


def search(query: str, domain: str = "all", top_k: int = 5) -> list[dict]:
    """Search the vector store for chunks relevant to query.

    Parameters
    ----------
    query:
        The natural-language query to embed and search.
    domain:
        Filter results to this domain. Use "all" for no filtering.
    top_k:
        Maximum number of results to return.

    Returns
    -------
    list[dict]
        Each element has keys: text, source, domain, score.
        Returns an empty list on any error.
    """
    _load_chunk_store()

    if not CHUNK_STORE:
        logger.warning("Chunk store is empty — returning no results for query: %s", query)
        return []

    try:
        from rag.embedder import embed_text  # noqa: PLC0415

        query_vector = embed_text(query)
    except Exception as exc:
        logger.error("Failed to embed query: %s", exc)
        return []

    try:
        endpoint = _get_endpoint()

        # Build namespace restricts for domain filtering
        restricts = []
        if domain != "all":
            from google.cloud.aiplatform.matching_engine.matching_engine_index_endpoint import (  # noqa: PLC0415
                Namespace,
            )

            restricts = [Namespace(name="domain", allow_tokens=[domain])]

        response = endpoint.find_neighbors(
            deployed_index_id=_DEPLOYED_INDEX_ID,
            queries=[query_vector],
            num_neighbors=top_k,
            filter=restricts if restricts else None,
        )

        neighbors = response[0] if response else []

    except Exception as exc:
        logger.error("Vertex AI Vector Search query failed: %s", exc)
        return []

    results: list[dict] = []
    for neighbor in neighbors:
        chunk_id = neighbor.id
        chunk = CHUNK_STORE.get(chunk_id)
        if chunk is None:
            logger.warning("Chunk ID %s not found in chunk store", chunk_id)
            continue
        results.append(
            {
                "text": chunk.get("text", ""),
                "source": chunk.get("source", "unknown"),
                "domain": chunk.get("domain", domain),
                "score": neighbor.distance,
            }
        )

    logger.info(
        "Vector search | query_len=%d | domain=%s | results=%d",
        len(query),
        domain,
        len(results),
    )
    return results


def format_context(results: list[dict]) -> str:
    """Format a list of retrieved chunks as a numbered context string.

    Parameters
    ----------
    results:
        Output of :func:`search`.

    Returns
    -------
    str
        Formatted context block, or empty string if results is empty.
    """
    if not results:
        return ""

    lines: list[str] = ["--- Retrieved Knowledge ---"]
    for i, chunk in enumerate(results, start=1):
        source = chunk.get("source", "unknown")
        text = chunk.get("text", "").strip()
        lines.append(f"\n[{i}] Source: {source}\n{text}")

    lines.append("\n--- End of Retrieved Knowledge ---")
    return "\n".join(lines)
