"""Unit tests for all domain models.

Covers entity creation, value object semantics, status enums,
and immutability constraints for frozen dataclasses.
"""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from app.domain.models.chunk import Chunk
from app.domain.models.citation import Citation
from app.domain.models.document import Document, DocumentStatus
from app.domain.models.grounding import GroundingDecision, QueryResult
from app.domain.models.interaction import Interaction, InteractionStatus
from app.domain.models.knowledge_base import KnowledgeBase


# ---------------------------------------------------------------------------
# KnowledgeBase
# ---------------------------------------------------------------------------

class TestKnowledgeBaseModel:
    """Tests for KnowledgeBase entity."""

    def test_create_with_required_fields(self) -> None:
        """KnowledgeBase can be created with id and name only."""
        kb = KnowledgeBase(id="kb-1", name="My KB")

        assert kb.id == "kb-1"
        assert kb.name == "My KB"

    def test_description_defaults_to_none(self) -> None:
        """Description is optional and defaults to None."""
        kb = KnowledgeBase(id="kb-1", name="My KB")

        assert kb.description is None

    def test_timestamps_default_to_none(self) -> None:
        """created_at and updated_at default to None when not provided."""
        kb = KnowledgeBase(id="kb-1", name="My KB")

        assert kb.created_at is None
        assert kb.updated_at is None

    def test_create_with_all_fields(self) -> None:
        """KnowledgeBase stores all provided fields correctly."""
        now = datetime(2026, 1, 1, tzinfo=UTC)
        kb = KnowledgeBase(
            id="kb-full",
            name="Full KB",
            description="A complete knowledge base",
            created_at=now,
            updated_at=now,
        )

        assert kb.id == "kb-full"
        assert kb.name == "Full KB"
        assert kb.description == "A complete knowledge base"
        assert kb.created_at == now
        assert kb.updated_at == now

    def test_is_mutable_dataclass(self) -> None:
        """KnowledgeBase fields can be updated (not frozen)."""
        kb = KnowledgeBase(id="kb-1", name="Old Name")
        kb.name = "New Name"

        assert kb.name == "New Name"


# ---------------------------------------------------------------------------
# Document
# ---------------------------------------------------------------------------

class TestDocumentModel:
    """Tests for Document entity and DocumentStatus enum."""

    def test_create_with_required_fields(self) -> None:
        """Document requires id, kb_id, filename, and content_hash."""
        doc = Document(
            id="doc-1",
            kb_id="kb-1",
            filename="report.pdf",
            content_hash="sha256abc",
        )

        assert doc.id == "doc-1"
        assert doc.kb_id == "kb-1"
        assert doc.filename == "report.pdf"
        assert doc.content_hash == "sha256abc"

    def test_status_defaults_to_pending(self) -> None:
        """New documents default to PENDING status."""
        doc = Document(
            id="doc-1",
            kb_id="kb-1",
            filename="file.pdf",
            content_hash="hash123",
        )

        assert doc.status == DocumentStatus.PENDING

    def test_chunks_count_defaults_to_zero(self) -> None:
        """chunks_count defaults to 0 for new documents."""
        doc = Document(
            id="doc-1",
            kb_id="kb-1",
            filename="file.pdf",
            content_hash="hash123",
        )

        assert doc.chunks_count == 0

    def test_status_transition_pending_to_processing(self) -> None:
        """Document status can be transitioned from PENDING to PROCESSING."""
        doc = Document(
            id="doc-1",
            kb_id="kb-1",
            filename="file.pdf",
            content_hash="hash123",
            status=DocumentStatus.PENDING,
        )
        doc.status = DocumentStatus.PROCESSING

        assert doc.status == DocumentStatus.PROCESSING

    def test_status_transition_processing_to_indexed(self) -> None:
        """Document status can transition from PROCESSING to INDEXED."""
        doc = Document(
            id="doc-1",
            kb_id="kb-1",
            filename="file.pdf",
            content_hash="hash123",
            status=DocumentStatus.PROCESSING,
        )
        doc.status = DocumentStatus.INDEXED

        assert doc.status == DocumentStatus.INDEXED

    def test_status_transition_to_error(self) -> None:
        """Document status can be set to ERROR from any state."""
        doc = Document(
            id="doc-1",
            kb_id="kb-1",
            filename="file.pdf",
            content_hash="hash123",
            status=DocumentStatus.PROCESSING,
        )
        doc.status = DocumentStatus.ERROR

        assert doc.status == DocumentStatus.ERROR

    def test_document_status_enum_values(self) -> None:
        """DocumentStatus enum has expected string values."""
        assert DocumentStatus.PENDING == "pending"
        assert DocumentStatus.PROCESSING == "processing"
        assert DocumentStatus.INDEXED == "indexed"
        assert DocumentStatus.ERROR == "error"


# ---------------------------------------------------------------------------
# Interaction
# ---------------------------------------------------------------------------

class TestInteractionModel:
    """Tests for Interaction entity and InteractionStatus enum."""

    def test_create_with_required_fields(self) -> None:
        """Interaction requires id, kb_id, and question."""
        interaction = Interaction(
            id="int-1",
            kb_id="kb-1",
            question="What is the return policy?",
        )

        assert interaction.id == "int-1"
        assert interaction.kb_id == "kb-1"
        assert interaction.question == "What is the return policy?"

    def test_answer_defaults_to_none(self) -> None:
        """Answer is optional and defaults to None."""
        interaction = Interaction(id="int-1", kb_id="kb-1", question="Q?")

        assert interaction.answer is None

    def test_status_defaults_to_unknown(self) -> None:
        """Default interaction status is UNKNOWN."""
        interaction = Interaction(id="int-1", kb_id="kb-1", question="Q?")

        assert interaction.status == InteractionStatus.UNKNOWN

    def test_citations_default_to_empty_list(self) -> None:
        """Citations default to an empty list."""
        interaction = Interaction(id="int-1", kb_id="kb-1", question="Q?")

        assert interaction.citations == []

    def test_create_answered_interaction(self) -> None:
        """Interaction can be created in ANSWERED status with citations."""
        citation = Citation(
            source_document="doc.pdf",
            page=1,
            chunk_id="chunk-1",
            relevance_score=0.9,
        )
        interaction = Interaction(
            id="int-1",
            kb_id="kb-1",
            question="What is the policy?",
            answer="Policy allows 30-day returns.",
            status=InteractionStatus.ANSWERED,
            citations=[citation],
        )

        assert interaction.status == InteractionStatus.ANSWERED
        assert interaction.answer == "Policy allows 30-day returns."
        assert len(interaction.citations) == 1

    def test_interaction_status_enum_values(self) -> None:
        """InteractionStatus enum has expected string values."""
        assert InteractionStatus.ANSWERED == "answered"
        assert InteractionStatus.UNKNOWN == "unknown"
        assert InteractionStatus.ERROR == "error"

    def test_citations_list_is_independent_between_instances(self) -> None:
        """Each Interaction instance has its own citations list (no shared state)."""
        int_a = Interaction(id="int-a", kb_id="kb-1", question="Q1?")
        int_b = Interaction(id="int-b", kb_id="kb-1", question="Q2?")

        int_a.citations.append(
            Citation(source_document="x.pdf", page=1, chunk_id="c1", relevance_score=0.5)
        )

        assert len(int_b.citations) == 0


# ---------------------------------------------------------------------------
# Citation
# ---------------------------------------------------------------------------

class TestCitationModel:
    """Tests for Citation frozen value object."""

    def test_create_citation(self) -> None:
        """Citation stores all fields correctly."""
        citation = Citation(
            source_document="report.pdf",
            page=3,
            chunk_id="chunk-abc",
            relevance_score=0.87,
        )

        assert citation.source_document == "report.pdf"
        assert citation.page == 3
        assert citation.chunk_id == "chunk-abc"
        assert citation.relevance_score == 0.87

    def test_page_can_be_none(self) -> None:
        """Page number is optional and can be None."""
        citation = Citation(
            source_document="doc.pdf",
            page=None,
            chunk_id="chunk-1",
            relevance_score=0.5,
        )

        assert citation.page is None

    def test_citation_is_frozen(self) -> None:
        """Citation is a frozen dataclass — mutation raises an error."""
        citation = Citation(
            source_document="doc.pdf",
            page=1,
            chunk_id="chunk-1",
            relevance_score=0.9,
        )

        with pytest.raises((AttributeError, TypeError)):
            citation.relevance_score = 0.5  # type: ignore[misc]

    def test_citation_equality_by_value(self) -> None:
        """Two Citations with identical field values are equal."""
        c1 = Citation(source_document="a.pdf", page=1, chunk_id="c1", relevance_score=0.9)
        c2 = Citation(source_document="a.pdf", page=1, chunk_id="c1", relevance_score=0.9)

        assert c1 == c2

    def test_citation_inequality_different_chunk_id(self) -> None:
        """Citations with different chunk_ids are not equal."""
        c1 = Citation(source_document="a.pdf", page=1, chunk_id="c1", relevance_score=0.9)
        c2 = Citation(source_document="a.pdf", page=1, chunk_id="c2", relevance_score=0.9)

        assert c1 != c2


# ---------------------------------------------------------------------------
# GroundingDecision
# ---------------------------------------------------------------------------

class TestGroundingDecisionModel:
    """Tests for GroundingDecision frozen value object."""

    def test_create_grounded_decision(self) -> None:
        """GroundingDecision stores all fields including supporting_chunks."""
        decision = GroundingDecision(
            is_grounded=True,
            confidence=0.85,
            reasoning="High keyword overlap",
            supporting_chunks=["chunk-1", "chunk-2"],
        )

        assert decision.is_grounded is True
        assert decision.confidence == 0.85
        assert decision.reasoning == "High keyword overlap"
        assert decision.supporting_chunks == ["chunk-1", "chunk-2"]

    def test_supporting_chunks_defaults_to_empty(self) -> None:
        """supporting_chunks defaults to empty list when not provided."""
        decision = GroundingDecision(
            is_grounded=False,
            confidence=0.0,
            reasoning="No chunks",
        )

        assert decision.supporting_chunks == []

    def test_grounding_decision_is_frozen(self) -> None:
        """GroundingDecision is a frozen dataclass — mutation raises an error."""
        decision = GroundingDecision(
            is_grounded=True,
            confidence=0.9,
            reasoning="Good overlap",
        )

        with pytest.raises((AttributeError, TypeError)):
            decision.is_grounded = False  # type: ignore[misc]

    def test_create_not_grounded_decision(self) -> None:
        """GroundingDecision correctly represents ungrounded state."""
        decision = GroundingDecision(
            is_grounded=False,
            confidence=0.1,
            reasoning="Insufficient keyword overlap",
        )

        assert decision.is_grounded is False
        assert decision.confidence == 0.1


# ---------------------------------------------------------------------------
# Chunk
# ---------------------------------------------------------------------------

class TestChunkModel:
    """Tests for Chunk value object."""

    def test_create_chunk_with_embedding(self) -> None:
        """Chunk stores content, metadata, and optional embedding."""
        chunk = Chunk(
            id="chunk-1",
            document_id="doc-1",
            content="Some text content.",
            metadata={"page": 1, "source_document": "file.pdf"},
            embedding=[0.1, 0.2, 0.3],
        )

        assert chunk.id == "chunk-1"
        assert chunk.document_id == "doc-1"
        assert chunk.content == "Some text content."
        assert chunk.metadata["page"] == 1
        assert chunk.embedding == [0.1, 0.2, 0.3]

    def test_embedding_defaults_to_none(self) -> None:
        """Embedding is optional and defaults to None."""
        chunk = Chunk(
            id="chunk-1",
            document_id="doc-1",
            content="Text.",
            metadata={},
        )

        assert chunk.embedding is None

    def test_chunk_metadata_is_arbitrary_dict(self) -> None:
        """Chunk metadata can hold arbitrary key-value pairs."""
        chunk = Chunk(
            id="chunk-1",
            document_id="doc-1",
            content="Text.",
            metadata={"custom_key": "custom_value", "nested": {"a": 1}},
        )

        assert chunk.metadata["custom_key"] == "custom_value"
        assert chunk.metadata["nested"]["a"] == 1
