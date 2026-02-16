"""Knowledge Base domain model.

This module defines the KnowledgeBase entity representing a collection
of documents for question answering.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass
class KnowledgeBase:
    """Entity representing a knowledge base.

    A knowledge base is a collection of documents that can be queried
    to answer questions.

    Attributes:
        id: Unique identifier (UUID string).
        name: Human-readable name for the knowledge base.
        description: Optional description of the knowledge base content.
        created_at: Timestamp when the KB was created.
        updated_at: Timestamp when the KB was last modified.
    """

    id: str
    name: str
    description: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
