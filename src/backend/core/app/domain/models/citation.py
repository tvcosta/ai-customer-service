"""Citation domain model.

This module defines the Citation value object representing source references
for grounded answers.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Citation:
    """Value object representing a citation to a source document chunk.

    Attributes:
        source_document: Name or identifier of the source document.
        page: Page number within the document (if applicable).
        chunk_id: Unique identifier of the chunk.
        relevance_score: Similarity score between query and chunk (0.0-1.0).
    """

    source_document: str
    page: int | None
    chunk_id: str
    relevance_score: float
