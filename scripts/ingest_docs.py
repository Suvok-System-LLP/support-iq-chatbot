#!/usr/bin/env python3
"""Ingest knowledge base documents into Vertex AI Vector Search.

Usage
-----
# Full ingest
python scripts/ingest_docs.py

# Dry run — print chunks without uploading
python scripts/ingest_docs.py --dry-run

# Re-ingest a single domain
python scripts/ingest_docs.py --domain schads
"""

import argparse
import json
import logging
import os
import sys
from collections import defaultdict
from pathlib import Path

# Ensure backend is on the path when running from the repo root
_REPO_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(_REPO_ROOT / "backend"))

from dotenv import load_dotenv

load_dotenv(_REPO_ROOT / "backend" / ".env")

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
logger = logging.getLogger(__name__)

_KNOWLEDGE_DIR = _REPO_ROOT / "knowledge"
_CHUNK_STORE_PATH = _KNOWLEDGE_DIR / "chunk_store.json"


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Ingest knowledge base into Vertex AI.")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print chunks without uploading to Vertex AI.",
    )
    parser.add_argument(
        "--domain",
        type=str,
        default=None,
        help="Only ingest chunks from this domain (e.g. schads, ndis, dex, product).",
    )
    return parser.parse_args()


def _print_dry_run(chunks: list[dict]) -> None:
    """Print the first 3 chunks per domain for review."""
    by_domain: dict[str, list[dict]] = defaultdict(list)
    for chunk in chunks:
        by_domain[chunk["domain"]].append(chunk)

    for domain, domain_chunks in sorted(by_domain.items()):
        print(f"\n{'='*60}")
        print(f"DOMAIN: {domain}  ({len(domain_chunks)} chunks total)")
        print("='*60")
        for chunk in domain_chunks[:3]:
            print(f"\n  ID:     {chunk['id']}")
            print(f"  Source: {chunk['source']}")
            print(f"  Chars:  {chunk['char_count']}")
            print(f"  Text:   {chunk['text'][:200]}...")


def _upsert_to_vertex(chunks: list[dict], embeddings: list[list[float]]) -> None:
    """Upsert chunk vectors to Vertex AI Vector Search."""
    import vertexai  # noqa: PLC0415
    from google.cloud import aiplatform  # noqa: PLC0415

    project = os.getenv("GOOGLE_CLOUD_PROJECT", "")
    region = os.getenv("GOOGLE_CLOUD_REGION", "australia-southeast1")
    index_endpoint_id = os.getenv("VERTEX_INDEX_ENDPOINT_ID", "")
    deployed_index_id = os.getenv("VERTEX_DEPLOYED_INDEX_ID", "")

    if not all([project, index_endpoint_id, deployed_index_id]):
        logger.error(
            "Missing required env vars: GOOGLE_CLOUD_PROJECT, "
            "VERTEX_INDEX_ENDPOINT_ID, VERTEX_DEPLOYED_INDEX_ID"
        )
        sys.exit(1)

    vertexai.init(project=project, location=region)
    aiplatform.init(project=project, location=region)

    # Vertex AI Vector Search upsert uses the index (not the endpoint)
    # We need the index resource name from the endpoint
    endpoint = aiplatform.MatchingEngineIndexEndpoint(
        index_endpoint_name=index_endpoint_id
    )

    # Find the deployed index to get the underlying index name
    deployed = None
    for di in endpoint.deployed_indexes:
        if di.id == deployed_index_id:
            deployed = di
            break

    if deployed is None:
        logger.error("Deployed index '%s' not found on endpoint.", deployed_index_id)
        sys.exit(1)

    index = aiplatform.MatchingEngineIndex(index_name=deployed.index)

    # Build datapoints for upsert
    from google.cloud.aiplatform.matching_engine.matching_engine_index_endpoint import (  # noqa: PLC0415
        Namespace,
    )
    from google.cloud.aiplatform_v1.types import IndexDatapoint  # noqa: PLC0415

    datapoints = []
    for chunk, vector in zip(chunks, embeddings):
        dp = IndexDatapoint(
            datapoint_id=chunk["id"],
            feature_vector=vector,
            restricts=[
                IndexDatapoint.Restriction(
                    namespace="domain",
                    allow_list=[chunk["domain"]],
                ),
            ],
        )
        datapoints.append(dp)

    logger.info("Upserting %d vectors to Vertex AI index…", len(datapoints))

    # Upsert in batches of 100 (Vertex AI limit per call)
    batch_size = 100
    for i in range(0, len(datapoints), batch_size):
        batch = datapoints[i : i + batch_size]
        index.upsert_datapoints(datapoints=batch)
        logger.info("  Upserted batch %d/%d", i // batch_size + 1, -(-len(datapoints) // batch_size))

    logger.info("Vertex AI upsert complete.")


def main() -> None:
    args = _parse_args()

    from rag.chunker import chunk_documents  # noqa: PLC0415

    logger.info("Loading chunks from %s …", _KNOWLEDGE_DIR)
    chunks = chunk_documents(str(_KNOWLEDGE_DIR))

    if args.domain:
        chunks = [c for c in chunks if c["domain"] == args.domain]
        logger.info("Filtered to domain '%s': %d chunks", args.domain, len(chunks))

    if not chunks:
        logger.warning("No chunks found — check that knowledge/*.md files have content.")
        sys.exit(0)

    # Count per domain
    by_domain: dict[str, int] = defaultdict(int)
    for c in chunks:
        by_domain[c["domain"]] += 1
    for domain, count in sorted(by_domain.items()):
        logger.info("  %s: %d chunks", domain, count)

    if args.dry_run:
        _print_dry_run(chunks)
        print(f"\n✅ Dry run complete — {len(chunks)} chunks across {len(by_domain)} domains (nothing uploaded)")
        return

    # Embed all chunks
    logger.info("Embedding %d chunks…", len(chunks))
    from rag.embedder import embed_batch  # noqa: PLC0415

    texts = [c["text"] for c in chunks]
    embeddings = embed_batch(texts, batch_size=5)

    # Upload to Vertex AI
    _upsert_to_vertex(chunks, embeddings)

    # Load existing chunk store (to preserve chunks from other domains if --domain used)
    existing_store: dict[str, dict] = {}
    if _CHUNK_STORE_PATH.exists():
        try:
            existing_store = json.loads(_CHUNK_STORE_PATH.read_text(encoding="utf-8"))
        except Exception as exc:
            logger.warning("Could not read existing chunk_store.json: %s", exc)

    # Update store with new chunks
    for chunk in chunks:
        existing_store[chunk["id"]] = {
            "text": chunk["text"],
            "source": chunk["source"],
            "domain": chunk["domain"],
            "char_count": chunk["char_count"],
        }

    _CHUNK_STORE_PATH.write_text(
        json.dumps(existing_store, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    logger.info("Saved chunk_store.json (%d total chunks)", len(existing_store))

    print(
        f"\n✅ Ingested {len(chunks)} chunks across {len(by_domain)} domains"
        f" | chunk_store.json updated"
    )


if __name__ == "__main__":
    main()
