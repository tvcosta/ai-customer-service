"""Document domain model.

This module defines the Document entity and associated types for tracking
uploaded documents within a knowledge base.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class DocumentStatus(str, Enum):
    """Status of a document in the processing pipeline."""

    PENDING = "pending"
    PROCESSING = "processing"
    INDEXED = "indexed"
    ERROR = "error"


@dataclass
class Document:
    """Entity representing a document within a knowledge base.

    Documents are uploaded files that get chunked and indexed for retrieval.

    Attributes:
        id: Unique identifier (UUID string).
        kb_id: ID of the knowledge base this document belongs to.
        filename: Original filename of the uploaded document.
        content_hash: Hash of the document content for deduplication.
        status: Current processing status.
        chunks_count: Number of chunks extracted from this document.
        uploaded_at: Timestamp when the document was uploaded.
    """

    id: str
    kb_id: str
    filename: str
    content_hash: str
    status: DocumentStatus = DocumentStatus.PENDING
    chunks_count: int = 0
    uploaded_at: datetime | None = None
