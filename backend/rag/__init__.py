"""RAG package — retrieval, embedding, and chunking utilities."""

from .retriever import format_context, search
from .embedder import embed_batch, embed_text
from .chunker import chunk_documents

__all__ = [
    "search",
    "format_context",
    "embed_text",
    "embed_batch",
    "chunk_documents",
]
