"""Unit tests for InteractionUseCase.

Tests cover listing interactions with filtering/pagination and retrieval by ID.
InteractionStorePort is mocked with AsyncMock.
"""

from __future__ import annotations

from datetime import UTC, datetime
from unittest.mock import AsyncMock

import pytest

from app.domain.models.citation import Citation
from app.domain.models.interaction import Interaction, InteractionStatus
from app.application.use_cases.interaction_use_case import InteractionUseCase


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def interaction_use_case(mock_interaction_store: AsyncMock) -> InteractionUseCase:
    """InteractionUseCase with a mocked interaction store."""
    return InteractionUseCase(interaction_store=mock_interaction_store)


def _make_interaction(
    interaction_id: str,
    kb_id: str = "kb-001",
    question: str = "What is the policy?",
    status: InteractionStatus = InteractionStatus.ANSWERED,
) -> Interaction:
    """Build a sample Interaction for testing."""
    return Interaction(
        id=interaction_id,
        kb_id=kb_id,
        question=question,
        answer="The policy is 30 days.",
        status=status,
        citations=[
            Citation(
                source_document="policy.pdf",
                page=1,
                chunk_id=f"chunk-{interaction_id}",
                relevance_score=0.9,
            )
        ],
        created_at=datetime(2026, 1, 1, tzinfo=UTC),
    )


# ---------------------------------------------------------------------------
# List all
# ---------------------------------------------------------------------------

class TestInteractionUseCaseListAll:
    """Tests for listing all interactions."""

    async def test_list_all_returns_empty_when_no_interactions(
        self,
        interaction_use_case: InteractionUseCase,
        mock_interaction_store: AsyncMock,
    ) -> None:
        """list_all() returns an empty list when the store has no interactions."""
        mock_interaction_store.list_all.return_value = []

        result = await interaction_use_case.list_all()

        assert result == []

    async def test_list_all_returns_all_interactions(
        self,
        interaction_use_case: InteractionUseCase,
        mock_interaction_store: AsyncMock,
    ) -> None:
        """list_all() returns all interactions from the store."""
        interactions = [
            _make_interaction("int-1"),
            _make_interaction("int-2"),
            _make_interaction("int-3"),
        ]
        mock_interaction_store.list_all.return_value = interactions

        result = await interaction_use_case.list_all()

        assert len(result) == 3
        assert result == interactions

    async def test_list_all_passes_kb_id_filter_to_store(
        self,
        interaction_use_case: InteractionUseCase,
        mock_interaction_store: AsyncMock,
    ) -> None:
        """list_all() forwards the kb_id filter to the interaction store."""
        mock_interaction_store.list_all.return_value = []

        await interaction_use_case.list_all(kb_id="kb-specific")

        mock_interaction_store.list_all.assert_called_once_with(
            kb_id="kb-specific", limit=50, offset=0
        )

    async def test_list_all_passes_limit_to_store(
        self,
        interaction_use_case: InteractionUseCase,
        mock_interaction_store: AsyncMock,
    ) -> None:
        """list_all() forwards the limit parameter to the interaction store."""
        mock_interaction_store.list_all.return_value = []

        await interaction_use_case.list_all(limit=10)

        mock_interaction_store.list_all.assert_called_once_with(
            kb_id=None, limit=10, offset=0
        )

    async def test_list_all_passes_offset_to_store(
        self,
        interaction_use_case: InteractionUseCase,
        mock_interaction_store: AsyncMock,
    ) -> None:
        """list_all() forwards the offset parameter to the interaction store."""
        mock_interaction_store.list_all.return_value = []

        await interaction_use_case.list_all(offset=20)

        mock_interaction_store.list_all.assert_called_once_with(
            kb_id=None, limit=50, offset=20
        )

    async def test_list_all_default_parameters(
        self,
        interaction_use_case: InteractionUseCase,
        mock_interaction_store: AsyncMock,
    ) -> None:
        """list_all() uses default limit=50 and offset=0 when not specified."""
        mock_interaction_store.list_all.return_value = []

        await interaction_use_case.list_all()

        mock_interaction_store.list_all.assert_called_once_with(
            kb_id=None, limit=50, offset=0
        )

    async def test_list_all_without_kb_filter_returns_all(
        self,
        interaction_use_case: InteractionUseCase,
        mock_interaction_store: AsyncMock,
    ) -> None:
        """list_all() without kb_id filter calls store with kb_id=None."""
        mock_interaction_store.list_all.return_value = []

        await interaction_use_case.list_all(kb_id=None)

        call_kwargs = mock_interaction_store.list_all.call_args[1]
        assert call_kwargs["kb_id"] is None

    async def test_list_all_returns_interactions_of_mixed_statuses(
        self,
        interaction_use_case: InteractionUseCase,
        mock_interaction_store: AsyncMock,
    ) -> None:
        """list_all() returns interactions regardless of their status."""
        interactions = [
            _make_interaction("int-a", status=InteractionStatus.ANSWERED),
            _make_interaction("int-b", status=InteractionStatus.UNKNOWN),
        ]
        mock_interaction_store.list_all.return_value = interactions

        result = await interaction_use_case.list_all()

        statuses = {i.status for i in result}
        assert InteractionStatus.ANSWERED in statuses
        assert InteractionStatus.UNKNOWN in statuses


# ---------------------------------------------------------------------------
# Get by ID
# ---------------------------------------------------------------------------

class TestInteractionUseCaseGet:
    """Tests for retrieving an interaction by ID."""

    async def test_get_returns_interaction_when_found(
        self,
        interaction_use_case: InteractionUseCase,
        mock_interaction_store: AsyncMock,
    ) -> None:
        """get() returns the Interaction entity when found."""
        interaction = _make_interaction("int-found")
        mock_interaction_store.get.return_value = interaction

        result = await interaction_use_case.get(interaction_id="int-found")

        assert result is interaction

    async def test_get_returns_none_when_not_found(
        self,
        interaction_use_case: InteractionUseCase,
        mock_interaction_store: AsyncMock,
    ) -> None:
        """get() returns None when the interaction ID does not exist."""
        mock_interaction_store.get.return_value = None

        result = await interaction_use_case.get(interaction_id="nonexistent")

        assert result is None

    async def test_get_calls_store_with_correct_interaction_id(
        self,
        interaction_use_case: InteractionUseCase,
        mock_interaction_store: AsyncMock,
    ) -> None:
        """get() passes the correct interaction_id to the store."""
        mock_interaction_store.get.return_value = None

        await interaction_use_case.get(interaction_id="int-abc-123")

        mock_interaction_store.get.assert_called_once_with("int-abc-123")

    async def test_get_returns_interaction_with_correct_id(
        self,
        interaction_use_case: InteractionUseCase,
        mock_interaction_store: AsyncMock,
    ) -> None:
        """get() returns an interaction whose id matches the requested id."""
        interaction = _make_interaction("int-verify-id")
        mock_interaction_store.get.return_value = interaction

        result = await interaction_use_case.get(interaction_id="int-verify-id")

        assert result is not None
        assert result.id == "int-verify-id"

    async def test_get_returns_interaction_with_citations(
        self,
        interaction_use_case: InteractionUseCase,
        mock_interaction_store: AsyncMock,
    ) -> None:
        """get() preserves citations on the returned interaction."""
        interaction = _make_interaction("int-with-citations")
        mock_interaction_store.get.return_value = interaction

        result = await interaction_use_case.get(interaction_id="int-with-citations")

        assert result is not None
        assert len(result.citations) > 0
        assert result.citations[0].source_document == "policy.pdf"
