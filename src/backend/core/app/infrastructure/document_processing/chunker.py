"""Text chunking with overlap for RAG retrieval."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class TextChunk:
    """A chunk of text with associated metadata."""

    content: str
    metadata: dict[str, object]


def chunk_text(
    text: str,
    chunk_size: int = 512,
    chunk_overlap: int = 50,
    source_document: str = "",
    page_number: int = 1,
) -> list[TextChunk]:
    """Split text into overlapping chunks by word count.

    Args:
        text: The input text to chunk.
        chunk_size: Maximum number of words per chunk.
        chunk_overlap: Number of overlapping words between consecutive chunks.
        source_document: Name of the source document for metadata.
        page_number: Page number within the document.

    Returns:
        List of text chunks with metadata.
    """
    if not text.strip():
        return []

    words = text.split()
    chunks: list[TextChunk] = []
    start = 0

    while start < len(words):
        end = start + chunk_size
        chunk_words = words[start:end]
        content = " ".join(chunk_words)
        chunks.append(
            TextChunk(
                content=content,
                metadata={
                    "source_document": source_document,
                    "page": page_number,
                    "start_word": start,
                },
            )
        )
        if end >= len(words):
            break
        start = end - chunk_overlap

    return chunks
