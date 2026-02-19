"""Unit tests for QueryUseCase.

Tests cover the full RAG pipeline: embed → retrieve → generate → ground → save → return.
All ports are mocked via AsyncMock. GroundingService is used as a real instance
but its behaviour is controlled through the content of the mocked chunks and answer.
"""

from __future__ import annotations

import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.domain.models.chunk import Chunk
from app.domain.models.grounding import GroundingDecision
from app.domain.models.interaction import InteractionStatus
from app.application.use_cases.query_use_case import QueryUseCase, UNKNOWN_MESSAGE


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_chunk(chunk_id: str, content: str) -> Chunk:
    """Return a Chunk whose content clearly relates to refund/returns."""
    return Chunk(
        id=chunk_id,
        document_id="doc-001",
        content=content,
        metadata={"source_document": "policy.pdf", "page": 1},
        embedding=[0.1, 0.2, 0.3],
    )


# ---------------------------------------------------------------------------
# Successful query flow
# ---------------------------------------------------------------------------

class TestQueryUseCaseSuccess:
    """Tests for the happy path: query returns 'answered'."""

    async def test_successful_query_returns_answered_status(
        self, query_use_case: QueryUseCase, mock_vectorstore: AsyncMock, mock_llm: AsyncMock
    ) -> None:
        """Full RAG pipeline returns QueryResult with status='answered'."""
        chunks = [
            _make_chunk("c1", "Refunds are allowed within 30 days of purchase."),
            _make_chunk("c2", "Returns require original receipt and purchase proof."),
        ]
        mock_vectorstore.search.return_value = chunks
        mock_llm.generate.return_value = "Refunds allowed within 30 days purchase receipt."

        result = await query_use_case.execute(kb_id="kb-001", question="What is the refund policy?")

        assert result.status == "answered"

    async def test_successful_query_returns_non_empty_answer(
        self, query_use_case: QueryUseCase, mock_vectorstore: AsyncMock, mock_llm: AsyncMock
    ) -> None:
        """Answer text is populated and not the UNKNOWN_MESSAGE when grounded."""
        chunks = [_make_chunk("c1", "Refunds allowed within 30 days purchase.")]
        mock_vectorstore.search.return_value = chunks
        expected_answer = "Refunds allowed within 30 days purchase."
        mock_llm.generate.return_value = expected_answer

        result = await query_use_case.execute(kb_id="kb-001", question="Refund policy?")

        assert result.answer == expected_answer
        assert result.answer != UNKNOWN_MESSAGE

    async def test_successful_query_returns_interaction_id(
        self, query_use_case: QueryUseCase, mock_vectorstore: AsyncMock, mock_llm: AsyncMock
    ) -> None:
        """A UUID interaction_id is always included in the result."""
        chunks = [_make_chunk("c1", "Refunds allowed within 30 days purchase.")]
        mock_vectorstore.search.return_value = chunks
        mock_llm.generate.return_value = "Refunds allowed within 30 days purchase."

        result = await query_use_case.execute(kb_id="kb-001", question="Refund?")

        assert result.interaction_id is not None
        # Must be a valid UUID string
        parsed = uuid.UUID(result.interaction_id)
        assert str(parsed) == result.interaction_id

    async def test_successful_query_builds_citations_from_supporting_chunks(
        self, query_use_case: QueryUseCase, mock_vectorstore: AsyncMock, mock_llm: AsyncMock
    ) -> None:
        """Citations are built only from chunks that support the answer."""
        chunks = [
            _make_chunk("c1", "Refunds allowed within 30 days purchase receipt."),
            _make_chunk("c2", "Contact support for assistance with orders."),
        ]
        mock_vectorstore.search.return_value = chunks
        # Answer only overlaps with c1 content
        mock_llm.generate.return_value = "Refunds allowed within 30 days purchase receipt."

        result = await query_use_case.execute(kb_id="kb-001", question="Refund policy?")

        assert result.status == "answered"
        assert len(result.citations) > 0
        # All citations must reference chunk IDs from the provided chunks
        chunk_ids = {c.id for c in chunks}
        for citation in result.citations:
            assert citation.chunk_id in chunk_ids

    async def test_successful_query_saves_interaction_with_answered_status(
        self, query_use_case: QueryUseCase, mock_vectorstore: AsyncMock,
        mock_llm: AsyncMock, mock_interaction_store: AsyncMock
    ) -> None:
        """An ANSWERED interaction is persisted to the interaction store."""
        chunks = [_make_chunk("c1", "Refunds allowed within 30 days purchase.")]
        mock_vectorstore.search.return_value = chunks
        mock_llm.generate.return_value = "Refunds allowed within 30 days purchase."

        await query_use_case.execute(kb_id="kb-001", question="Refund?")

        mock_interaction_store.save.assert_called_once()
        saved_interaction = mock_interaction_store.save.call_args[0][0]
        assert saved_interaction.status == InteractionStatus.ANSWERED

    async def test_llm_embed_called_with_question(
        self, query_use_case: QueryUseCase, mock_vectorstore: AsyncMock,
        mock_llm: AsyncMock
    ) -> None:
        """LLM embed is called with the user's question to produce the query vector."""
        chunks = [_make_chunk("c1", "Refunds allowed within 30 days purchase.")]
        mock_vectorstore.search.return_value = chunks
        mock_llm.generate.return_value = "Refunds allowed within 30 days purchase."

        await query_use_case.execute(kb_id="kb-001", question="Refund policy?")

        mock_llm.embed.assert_called_once_with("Refund policy?")

    async def test_vectorstore_search_called_with_embedding_and_kb_id(
        self, query_use_case: QueryUseCase, mock_vectorstore: AsyncMock,
        mock_llm: AsyncMock
    ) -> None:
        """Vector store search receives the query embedding and correct kb_id."""
        query_vector = [0.9, 0.8, 0.7]
        mock_llm.embed.return_value = query_vector
        chunks = [_make_chunk("c1", "Refunds allowed within 30 days purchase.")]
        mock_vectorstore.search.return_value = chunks
        mock_llm.generate.return_value = "Refunds allowed within 30 days purchase."

        await query_use_case.execute(kb_id="kb-test", question="Refund?")

        mock_vectorstore.search.assert_called_once_with(query_vector, "kb-test")

    async def test_citations_have_source_document_from_metadata(
        self, query_use_case: QueryUseCase, mock_vectorstore: AsyncMock, mock_llm: AsyncMock
    ) -> None:
        """Citation source_document is populated from chunk metadata."""
        chunk = Chunk(
            id="c1",
            document_id="doc-1",
            content="Refunds allowed within 30 days purchase receipt policy.",
            metadata={"source_document": "policy-guide.pdf", "page": 5},
            embedding=[0.1, 0.2, 0.3],
        )
        mock_vectorstore.search.return_value = [chunk]
        mock_llm.generate.return_value = (
            "Refunds allowed within 30 days purchase receipt policy."
        )

        result = await query_use_case.execute(kb_id="kb-001", question="Policy?")

        assert result.status == "answered"
        assert len(result.citations) > 0
        assert result.citations[0].source_document == "policy-guide.pdf"


# ---------------------------------------------------------------------------
# No chunks found → unknown
# ---------------------------------------------------------------------------

class TestQueryUseCaseNoChunks:
    """Tests for the case where the vector store returns no results."""

    async def test_no_chunks_returns_unknown_status(
        self, query_use_case: QueryUseCase, mock_vectorstore: AsyncMock
    ) -> None:
        """Empty retrieval results always return status='unknown'."""
        mock_vectorstore.search.return_value = []

        result = await query_use_case.execute(kb_id="kb-001", question="What is X?")

        assert result.status == "unknown"

    async def test_no_chunks_returns_unknown_message(
        self, query_use_case: QueryUseCase, mock_vectorstore: AsyncMock
    ) -> None:
        """The standard UNKNOWN_MESSAGE is returned when no chunks are found."""
        mock_vectorstore.search.return_value = []

        result = await query_use_case.execute(kb_id="kb-001", question="What is X?")

        assert result.answer == UNKNOWN_MESSAGE

    async def test_no_chunks_returns_empty_citations(
        self, query_use_case: QueryUseCase, mock_vectorstore: AsyncMock
    ) -> None:
        """No citations are returned when retrieval yields no chunks."""
        mock_vectorstore.search.return_value = []

        result = await query_use_case.execute(kb_id="kb-001", question="What is X?")

        assert result.citations == []

    async def test_no_chunks_saves_unknown_interaction(
        self, query_use_case: QueryUseCase, mock_vectorstore: AsyncMock,
        mock_interaction_store: AsyncMock
    ) -> None:
        """An UNKNOWN interaction is saved when no chunks are retrieved."""
        mock_vectorstore.search.return_value = []

        await query_use_case.execute(kb_id="kb-001", question="What is X?")

        mock_interaction_store.save.assert_called_once()
        saved = mock_interaction_store.save.call_args[0][0]
        assert saved.status == InteractionStatus.UNKNOWN

    async def test_no_chunks_result_still_includes_interaction_id(
        self, query_use_case: QueryUseCase, mock_vectorstore: AsyncMock
    ) -> None:
        """interaction_id is always present even when retrieval fails."""
        mock_vectorstore.search.return_value = []

        result = await query_use_case.execute(kb_id="kb-001", question="Q?")

        assert result.interaction_id is not None
        uuid.UUID(result.interaction_id)  # Validates format


# ---------------------------------------------------------------------------
# Grounding fails → unknown
# ---------------------------------------------------------------------------

class TestQueryUseCaseGroundingFails:
    """Tests for the case where chunks exist but the answer is not grounded."""

    async def test_ungrounded_answer_returns_unknown_status(
        self, query_use_case: QueryUseCase, mock_vectorstore: AsyncMock,
        mock_llm: AsyncMock
    ) -> None:
        """When grounding fails the result status is 'unknown'."""
        # Chunks about one topic, LLM generates completely unrelated answer
        chunks = [_make_chunk("c1", "The store is located in downtown Manhattan area.")]
        mock_vectorstore.search.return_value = chunks
        # Unrelated answer — no keyword overlap with chunks
        mock_llm.generate.return_value = (
            "Jupiter astronomy planet universe galaxy telescope nebula observatory cosmos."
        )

        result = await query_use_case.execute(kb_id="kb-001", question="Where is the store?")

        assert result.status == "unknown"

    async def test_ungrounded_answer_returns_unknown_message(
        self, query_use_case: QueryUseCase, mock_vectorstore: AsyncMock,
        mock_llm: AsyncMock
    ) -> None:
        """The UNKNOWN_MESSAGE is returned when grounding fails."""
        chunks = [_make_chunk("c1", "The store is located in downtown Manhattan area.")]
        mock_vectorstore.search.return_value = chunks
        mock_llm.generate.return_value = (
            "Jupiter astronomy planet universe galaxy telescope nebula observatory cosmos."
        )

        result = await query_use_case.execute(kb_id="kb-001", question="Where is the store?")

        assert result.answer == UNKNOWN_MESSAGE

    async def test_ungrounded_answer_returns_empty_citations(
        self, query_use_case: QueryUseCase, mock_vectorstore: AsyncMock,
        mock_llm: AsyncMock
    ) -> None:
        """No citations are returned when grounding fails."""
        chunks = [_make_chunk("c1", "The store is located in downtown Manhattan area.")]
        mock_vectorstore.search.return_value = chunks
        mock_llm.generate.return_value = (
            "Jupiter astronomy planet universe galaxy telescope nebula observatory cosmos."
        )

        result = await query_use_case.execute(kb_id="kb-001", question="Where is the store?")

        assert result.citations == []

    async def test_ungrounded_answer_saves_unknown_interaction(
        self, query_use_case: QueryUseCase, mock_vectorstore: AsyncMock,
        mock_llm: AsyncMock, mock_interaction_store: AsyncMock
    ) -> None:
        """An UNKNOWN interaction is persisted when grounding fails."""
        chunks = [_make_chunk("c1", "The store is located in downtown Manhattan area.")]
        mock_vectorstore.search.return_value = chunks
        mock_llm.generate.return_value = (
            "Jupiter astronomy planet universe galaxy telescope nebula observatory cosmos."
        )

        await query_use_case.execute(kb_id="kb-001", question="Where is the store?")

        mock_interaction_store.save.assert_called_once()
        saved = mock_interaction_store.save.call_args[0][0]
        assert saved.status == InteractionStatus.UNKNOWN

    async def test_ungrounded_answer_still_includes_interaction_id(
        self, query_use_case: QueryUseCase, mock_vectorstore: AsyncMock,
        mock_llm: AsyncMock
    ) -> None:
        """interaction_id is always present even when grounding fails."""
        chunks = [_make_chunk("c1", "Store located downtown Manhattan.")]
        mock_vectorstore.search.return_value = chunks
        mock_llm.generate.return_value = (
            "Jupiter astronomy planet universe galaxy telescope nebula observatory cosmos."
        )

        result = await query_use_case.execute(kb_id="kb-001", question="Q?")

        assert result.interaction_id is not None
        uuid.UUID(result.interaction_id)


# ---------------------------------------------------------------------------
# Interaction ID uniqueness
# ---------------------------------------------------------------------------

class TestQueryUseCaseInteractionId:
    """Tests that verify interaction_id generation semantics."""

    async def test_each_call_generates_unique_interaction_id(
        self, query_use_case: QueryUseCase, mock_vectorstore: AsyncMock
    ) -> None:
        """Consecutive calls produce different interaction IDs."""
        mock_vectorstore.search.return_value = []

        result_a = await query_use_case.execute(kb_id="kb-001", question="Q?")
        result_b = await query_use_case.execute(kb_id="kb-001", question="Q?")

        assert result_a.interaction_id != result_b.interaction_id

    async def test_saved_interaction_id_matches_result_interaction_id(
        self, query_use_case: QueryUseCase, mock_vectorstore: AsyncMock,
        mock_interaction_store: AsyncMock
    ) -> None:
        """The interaction_id in the result matches the one persisted to the store."""
        mock_vectorstore.search.return_value = []

        result = await query_use_case.execute(kb_id="kb-001", question="Q?")

        saved = mock_interaction_store.save.call_args[0][0]
        assert saved.id == result.interaction_id
