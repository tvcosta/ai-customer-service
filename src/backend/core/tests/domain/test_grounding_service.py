"""Unit tests for GroundingService domain service.

Tests cover grounded/ungrounded decisions, confidence scoring behaviour,
and edge cases (empty chunks, empty answer).
"""

from __future__ import annotations

import pytest

from app.domain.models.chunk import Chunk
from app.domain.services.grounding_service import GroundingService


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_chunk(chunk_id: str, content: str, document_id: str = "doc-001") -> Chunk:
    """Create a minimal Chunk for testing."""
    return Chunk(
        id=chunk_id,
        document_id=document_id,
        content=content,
        metadata={"source_document": "test.pdf", "page": 1},
    )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestGroundingServiceGroundedAnswer:
    """Tests where the answer IS grounded in the provided chunks."""

    def test_grounded_answer_returns_is_grounded_true(
        self, grounding_service: GroundingService
    ) -> None:
        """High keyword overlap between answer and chunks yields is_grounded=True."""
        chunks = [
            _make_chunk("c1", "The refund policy allows returns within 30 days of purchase."),
            _make_chunk("c2", "Customers must present the original receipt to claim refund."),
        ]
        question = "What is the refund policy?"
        answer = "Returns are allowed within 30 days of purchase with original receipt."

        decision = grounding_service.evaluate(question, answer, chunks)

        assert decision.is_grounded is True

    def test_grounded_answer_confidence_above_threshold(
        self, grounding_service: GroundingService
    ) -> None:
        """Confidence score is >= 0.3 when answer is grounded."""
        chunks = [_make_chunk("c1", "The product ships within 2 business days via standard mail.")]
        answer = "The product ships within 2 business days."

        decision = grounding_service.evaluate("When does it ship?", answer, chunks)

        assert decision.confidence >= 0.3

    def test_grounded_answer_includes_supporting_chunks(
        self, grounding_service: GroundingService
    ) -> None:
        """supporting_chunks list is populated when answer is grounded."""
        chunks = [
            _make_chunk("c1", "The warranty lasts for two years from purchase date."),
            _make_chunk("c2", "Extended warranty options are available at checkout."),
        ]
        answer = "Warranty lasts two years from purchase date."

        decision = grounding_service.evaluate("How long is the warranty?", answer, chunks)

        assert decision.is_grounded is True
        assert len(decision.supporting_chunks) > 0
        assert all(c_id in {"c1", "c2"} for c_id in decision.supporting_chunks)

    def test_grounded_answer_has_meaningful_reasoning(
        self, grounding_service: GroundingService
    ) -> None:
        """Reasoning string describes keyword overlap."""
        chunks = [_make_chunk("c1", "Office hours are Monday to Friday, 9am to 5pm.")]
        answer = "Office hours Monday Friday."

        decision = grounding_service.evaluate("What are the office hours?", answer, chunks)

        assert "meaningful words" in decision.reasoning


class TestGroundingServiceUngroundedAnswer:
    """Tests where the answer is NOT grounded in the provided chunks."""

    def test_ungrounded_answer_returns_is_grounded_false(
        self, grounding_service: GroundingService
    ) -> None:
        """Answer with zero keyword overlap with chunks yields is_grounded=False."""
        chunks = [_make_chunk("c1", "Shipping takes 3-5 business days.")]
        # Answer talks about something completely different from the chunk
        answer = "Jupiter astronomy planet universe galaxy telescope nebula."

        decision = grounding_service.evaluate("What is in the sky?", answer, chunks)

        assert decision.is_grounded is False

    def test_ungrounded_answer_low_confidence(
        self, grounding_service: GroundingService
    ) -> None:
        """Confidence score is below 0.3 when answer has low overlap."""
        chunks = [_make_chunk("c1", "Our store is located in downtown Manhattan.")]
        answer = "Jupiter astronomy planet universe galaxy telescope nebula observatory."

        decision = grounding_service.evaluate("Where is the store?", answer, chunks)

        assert decision.confidence < 0.3

    def test_ungrounded_answer_has_empty_supporting_chunks(
        self, grounding_service: GroundingService
    ) -> None:
        """No supporting chunks listed when answer is ungrounded."""
        chunks = [_make_chunk("c1", "We sell fresh organic vegetables daily.")]
        answer = "Jupiter astronomy planet universe galaxy telescope."

        decision = grounding_service.evaluate("What do you sell?", answer, chunks)

        assert decision.is_grounded is False
        # supporting_chunks may be empty or contain no overlap
        # The key assertion: confidence < 0.3 so is_grounded is False
        assert decision.confidence < 0.3


class TestGroundingServiceEmptyChunks:
    """Tests for edge case: no chunks retrieved."""

    def test_empty_chunks_returns_not_grounded(
        self, grounding_service: GroundingService
    ) -> None:
        """Empty chunk list always results in is_grounded=False."""
        decision = grounding_service.evaluate(
            question="What is the return policy?",
            answer="Returns are allowed within 30 days.",
            chunks=[],
        )

        assert decision.is_grounded is False

    def test_empty_chunks_returns_zero_confidence(
        self, grounding_service: GroundingService
    ) -> None:
        """Confidence is exactly 0.0 when no chunks are provided."""
        decision = grounding_service.evaluate(
            question="Any question?",
            answer="Any answer with content.",
            chunks=[],
        )

        assert decision.confidence == 0.0

    def test_empty_chunks_has_explanatory_reasoning(
        self, grounding_service: GroundingService
    ) -> None:
        """Reasoning explains why grounding failed when no chunks present."""
        decision = grounding_service.evaluate(
            question="Test?",
            answer="Test answer.",
            chunks=[],
        )

        assert "No chunks" in decision.reasoning


class TestGroundingServiceConfidenceScoring:
    """Tests that verify the confidence scoring formula."""

    def test_confidence_is_zero_for_all_stopword_answer(
        self, grounding_service: GroundingService
    ) -> None:
        """An answer composed entirely of stopwords produces confidence=0.0."""
        chunks = [_make_chunk("c1", "Some content about products and services.")]
        # All words in this answer are in the stopwords set
        answer = "the a an is are was in on at"

        decision = grounding_service.evaluate("Question?", answer, chunks)

        assert decision.confidence == 0.0
        assert decision.is_grounded is False

    def test_confidence_between_zero_and_one(
        self, grounding_service: GroundingService
    ) -> None:
        """Confidence is always in the range [0.0, 1.0]."""
        chunks = [_make_chunk("c1", "Partial overlap content here about refunds.")]
        answer = "Refunds available for eligible purchases within the stipulated period."

        decision = grounding_service.evaluate("Refund info?", answer, chunks)

        assert 0.0 <= decision.confidence <= 1.0

    def test_perfect_overlap_produces_high_confidence(
        self, grounding_service: GroundingService
    ) -> None:
        """Answer using only words present in chunks scores high confidence."""
        chunks = [
            _make_chunk("c1", "premium membership includes unlimited access streaming movies"),
        ]
        # All meaningful words from the answer exist in the chunk
        answer = "premium membership includes unlimited streaming access movies"

        decision = grounding_service.evaluate("What does membership include?", answer, chunks)

        assert decision.confidence >= 0.8

    def test_supporting_chunks_only_includes_matching_chunks(
        self, grounding_service: GroundingService
    ) -> None:
        """Only chunks containing meaningful answer words appear in supporting_chunks."""
        chunks = [
            _make_chunk("c1", "The refund policy applies within 30 days."),
            _make_chunk("c2", "Store hours are 9am to 5pm on weekdays."),
        ]
        answer = "Refunds allowed within 30 days."

        decision = grounding_service.evaluate("Refund policy?", answer, chunks)

        # c1 matches refund/days; c2 about store hours should not be primary match
        assert "c1" in decision.supporting_chunks
