"""Grounding service for determining if LLM responses are grounded in KB content."""

from __future__ import annotations

from app.domain.models.chunk import Chunk
from app.domain.models.grounding import GroundingDecision

_STOPWORDS = frozenset({
    "the", "a", "an", "is", "are", "was", "were", "in", "on", "at", "to", "for",
    "of", "and", "or", "but", "it", "this", "that", "with", "from", "by", "as",
    "be", "has", "have", "had", "not", "no", "do", "does", "did", "will", "would",
    "can", "could", "should", "may", "might", "i", "you", "we", "they", "he", "she",
})


class GroundingService:
    """Service to evaluate if LLM-generated answers are grounded in retrieved chunks."""

    def evaluate(
        self, question: str, answer: str, chunks: list[Chunk]
    ) -> GroundingDecision:
        """Evaluate if the answer is grounded in the provided chunks.

        Args:
            question: The original question.
            answer: The LLM-generated answer.
            chunks: Retrieved chunks from the knowledge base.

        Returns:
            Grounding decision with confidence score and reasoning.
        """
        if not chunks:
            return GroundingDecision(
                is_grounded=False,
                confidence=0.0,
                reasoning="No chunks retrieved",
            )

        chunk_text = " ".join(c.content.lower() for c in chunks)
        meaningful_words = set(answer.lower().split()) - _STOPWORDS

        if not meaningful_words:
            return GroundingDecision(
                is_grounded=False,
                confidence=0.0,
                reasoning="No meaningful content in answer",
            )

        overlap = sum(1 for w in meaningful_words if w in chunk_text)
        confidence = overlap / len(meaningful_words)
        supporting = [
            c.id for c in chunks if any(w in c.content.lower() for w in meaningful_words)
        ]

        return GroundingDecision(
            is_grounded=confidence >= 0.3,
            confidence=confidence,
            reasoning=f"Keyword overlap: {overlap}/{len(meaningful_words)} meaningful words found in chunks",
            supporting_chunks=supporting,
        )
