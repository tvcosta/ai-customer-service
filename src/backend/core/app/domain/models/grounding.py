"""Grounding domain model.

This module defines value objects for grounding evaluation and query results.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from app.domain.models.citation import Citation


@dataclass(frozen=True)
class GroundingDecision:
    """Value object representing the result of grounding evaluation.

    Grounding checks whether a generated answer is supported by the
    retrieved source chunks.

    Attributes:
        is_grounded: Whether the answer is adequately supported.
        confidence: Confidence score for the grounding decision (0.0-1.0).
        reasoning: Explanation of how the decision was made.
        supporting_chunks: List of chunk IDs that support the answer.
    """

    is_grounded: bool
    confidence: float
    reasoning: str
    supporting_chunks: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class QueryResult:
    """Value object representing the result of a knowledge base query.

    This is the final output returned to the user after the RAG pipeline
    completes.

    Attributes:
        status: Result status ("answered", "unknown", or "error").
        answer: The generated answer text (if available).
        citations: List of source citations supporting the answer.
        interaction_id: Unique identifier for this interaction.
    """

    status: str
    answer: str | None
    citations: list[Citation]
    interaction_id: str
