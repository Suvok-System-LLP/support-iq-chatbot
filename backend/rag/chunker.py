"""Markdown document chunker using tiktoken for token-aware splitting."""

import json
import uuid
from pathlib import Path

import tiktoken

CHUNK_SIZE = 500  # tokens per chunk
CHUNK_OVERLAP = 50  # overlap tokens between adjacent chunks
ENCODING_NAME = "cl100k_base"
MIN_CHUNK_TOKENS = 50  # skip chunks smaller than this

_enc = tiktoken.get_encoding(ENCODING_NAME)


def _tokenize(text: str) -> list[int]:
    """Return the token IDs for a string."""
    return _enc.encode(text)


def _detokenize(tokens: list[int]) -> str:
    """Decode token IDs back to a string."""
    return _enc.decode(tokens)


def chunk_single_file(filepath: str, domain: str) -> list[dict]:
    """Chunk a single Markdown file into token-bounded segments.

    Parameters
    ----------
    filepath:
        Absolute or relative path to the .md file.
    domain:
        Domain label (e.g. "schads", "ndis") derived from parent folder.

    Returns
    -------
    list[dict]
        Each element has keys: id, text, source, domain, char_count.
    """
    path = Path(filepath)
    try:
        content = path.read_text(encoding="utf-8").strip()
    except OSError:
        return []

    tokens = _tokenize(content)
    if len(tokens) < MIN_CHUNK_TOKENS:
        return []

    chunks: list[dict] = []
    start = 0

    while start < len(tokens):
        end = min(start + CHUNK_SIZE, len(tokens))
        chunk_tokens = tokens[start:end]
        chunk_text = _detokenize(chunk_tokens).strip()

        if len(chunk_tokens) >= MIN_CHUNK_TOKENS and chunk_text:
            chunks.append(
                {
                    "id": str(uuid.uuid4()),
                    "text": chunk_text,
                    "source": path.name,
                    "domain": domain,
                    "char_count": len(chunk_text),
                }
            )

        if end >= len(tokens):
            break
        start = end - CHUNK_OVERLAP  # slide back by overlap

    return chunks


def chunk_documents(docs_dir: str) -> list[dict]:
    """Walk all .md files under docs_dir and return a flat list of chunks.

    The domain is derived from the immediate parent folder name of each file.

    Parameters
    ----------
    docs_dir:
        Root directory containing domain sub-folders with .md files.

    Returns
    -------
    list[dict]
        Flat list of chunk dicts from all files.
    """
    root = Path(docs_dir)
    all_chunks: list[dict] = []

    for md_file in sorted(root.rglob("*.md")):
        # Domain = immediate parent folder name (e.g. schads, ndis, dex, product)
        domain = md_file.parent.name
        file_chunks = chunk_single_file(str(md_file), domain)
        all_chunks.extend(file_chunks)

    return all_chunks
