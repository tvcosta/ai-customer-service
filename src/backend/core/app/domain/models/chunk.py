"""Chunk domain model.

This module defines the Chunk value object representing a segment of
document text with its embedding.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class Chunk:
    """Value object representing a chunk of document text.

    Documents are split into chunks for efficient retrieval and processing.
    Each chunk has an embedding vector for semantic search.

    Attributes:
        id: Unique identifier for the chunk.
        document_id: ID of the parent document.
        content: The actual text content of the chunk.
        metadata: Additional metadata (e.g., page number, section).
        embedding: Vector embedding of the chunk content (if computed).
    """

    id: str
    document_id: str
    content: str
    metadata: dict[str, Any]
    embedding: list[float] | None = None
