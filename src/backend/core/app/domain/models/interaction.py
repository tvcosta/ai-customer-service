"""Interaction domain model.

This module defines the Interaction entity and associated types for tracking
question-answer interactions with the system.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from app.domain.models.citation import Citation


class InteractionStatus(str, Enum):
    """Status of a question-answering interaction."""

    ANSWERED = "answered"
    UNKNOWN = "unknown"
    ERROR = "error"


@dataclass
class Interaction:
    """Entity representing a question-answer interaction.

    Each interaction tracks a user question, the system's response,
    and the grounding evidence (citations).

    Attributes:
        id: Unique identifier (UUID string).
        kb_id: ID of the knowledge base queried.
        question: The user's question.
        answer: The system's generated answer (if available).
        status: Outcome status of the interaction.
        citations: List of source citations supporting the answer.
        created_at: Timestamp when the interaction occurred.
    """

    id: str
    kb_id: str
    question: str
    answer: str | None = None
    status: InteractionStatus = InteractionStatus.UNKNOWN
    citations: list[Citation] = field(default_factory=list)
    created_at: datetime | None = None
