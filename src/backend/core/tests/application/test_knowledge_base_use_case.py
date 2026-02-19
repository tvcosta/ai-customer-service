"""Unit tests for KnowledgeBaseUseCase.

Tests cover CRUD operations delegated to DocumentStorePort.
All port methods are mocked with AsyncMock.
"""

from __future__ import annotations

from datetime import UTC, datetime
from unittest.mock import AsyncMock

import pytest

from app.domain.models.knowledge_base import KnowledgeBase
from app.domain.ports.document_store_port import DocumentStorePort
from app.application.use_cases.knowledge_base_use_case import KnowledgeBaseUseCase


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def kb_use_case(mock_document_store: AsyncMock) -> KnowledgeBaseUseCase:
    """KnowledgeBaseUseCase with a mocked document store."""
    return KnowledgeBaseUseCase(document_store=mock_document_store)


# ---------------------------------------------------------------------------
# Create
# ---------------------------------------------------------------------------

class TestKnowledgeBaseUseCaseCreate:
    """Tests for KB creation."""

    async def test_create_kb_returns_knowledge_base(
        self, kb_use_case: KnowledgeBaseUseCase, mock_document_store: AsyncMock
    ) -> None:
        """create() returns the KnowledgeBase entity that was passed to the store."""
        # The conftest side_effect returns the kb passed into create_kb,
        # so we assert on the returned KB's core fields rather than identity.
        result = await kb_use_case.create(name="My KB", description="A description")

        assert isinstance(result, KnowledgeBase)
        assert result.name == "My KB"
        assert result.description == "A description"

    async def test_create_kb_calls_store_create_kb(
        self, kb_use_case: KnowledgeBaseUseCase, mock_document_store: AsyncMock
    ) -> None:
        """create() delegates to document_store.create_kb with correct data."""
        mock_document_store.create_kb.side_effect = lambda kb: kb

        result = await kb_use_case.create(name="Test KB", description="desc")

        mock_document_store.create_kb.assert_called_once()
        passed_kb = mock_document_store.create_kb.call_args[0][0]
        assert passed_kb.name == "Test KB"
        assert passed_kb.description == "desc"

    async def test_create_kb_generates_uuid_for_id(
        self, kb_use_case: KnowledgeBaseUseCase, mock_document_store: AsyncMock
    ) -> None:
        """create() generates a UUID for the new KB's id."""
        import uuid

        mock_document_store.create_kb.side_effect = lambda kb: kb

        result = await kb_use_case.create(name="UUID KB")

        passed_kb = mock_document_store.create_kb.call_args[0][0]
        # Must be parseable as a UUID
        uuid.UUID(passed_kb.id)

    async def test_create_kb_without_description(
        self, kb_use_case: KnowledgeBaseUseCase, mock_document_store: AsyncMock
    ) -> None:
        """create() accepts no description (defaults to None)."""
        mock_document_store.create_kb.side_effect = lambda kb: kb

        await kb_use_case.create(name="No Description KB")

        passed_kb = mock_document_store.create_kb.call_args[0][0]
        assert passed_kb.description is None

    async def test_create_kb_sets_created_at(
        self, kb_use_case: KnowledgeBaseUseCase, mock_document_store: AsyncMock
    ) -> None:
        """create() sets created_at to the current UTC time."""
        mock_document_store.create_kb.side_effect = lambda kb: kb

        await kb_use_case.create(name="Timestamped KB")

        passed_kb = mock_document_store.create_kb.call_args[0][0]
        assert passed_kb.created_at is not None
        # created_at should be timezone-aware (UTC)
        assert passed_kb.created_at.tzinfo is not None


# ---------------------------------------------------------------------------
# List all
# ---------------------------------------------------------------------------

class TestKnowledgeBaseUseCaseListAll:
    """Tests for listing all KBs."""

    async def test_list_all_returns_empty_list_when_no_kbs(
        self, kb_use_case: KnowledgeBaseUseCase, mock_document_store: AsyncMock
    ) -> None:
        """list_all() returns an empty list when no KBs exist."""
        mock_document_store.list_kbs.return_value = []

        result = await kb_use_case.list_all()

        assert result == []

    async def test_list_all_returns_all_knowledge_bases(
        self, kb_use_case: KnowledgeBaseUseCase, mock_document_store: AsyncMock
    ) -> None:
        """list_all() returns the full list from the store."""
        kbs = [
            KnowledgeBase(id="kb-1", name="KB One"),
            KnowledgeBase(id="kb-2", name="KB Two"),
            KnowledgeBase(id="kb-3", name="KB Three"),
        ]
        mock_document_store.list_kbs.return_value = kbs

        result = await kb_use_case.list_all()

        assert len(result) == 3
        assert result == kbs

    async def test_list_all_calls_store_list_kbs(
        self, kb_use_case: KnowledgeBaseUseCase, mock_document_store: AsyncMock
    ) -> None:
        """list_all() delegates to document_store.list_kbs()."""
        mock_document_store.list_kbs.return_value = []

        await kb_use_case.list_all()

        mock_document_store.list_kbs.assert_called_once()


# ---------------------------------------------------------------------------
# Get by ID
# ---------------------------------------------------------------------------

class TestKnowledgeBaseUseCaseGet:
    """Tests for retrieving a KB by ID."""

    async def test_get_returns_knowledge_base_when_found(
        self, kb_use_case: KnowledgeBaseUseCase, mock_document_store: AsyncMock
    ) -> None:
        """get() returns the KB entity when found."""
        kb = KnowledgeBase(id="kb-1", name="Found KB")
        mock_document_store.get_kb.return_value = kb

        result = await kb_use_case.get(kb_id="kb-1")

        assert result is kb

    async def test_get_returns_none_when_not_found(
        self, kb_use_case: KnowledgeBaseUseCase, mock_document_store: AsyncMock
    ) -> None:
        """get() returns None when the KB does not exist."""
        mock_document_store.get_kb.return_value = None

        result = await kb_use_case.get(kb_id="nonexistent")

        assert result is None

    async def test_get_calls_store_with_correct_kb_id(
        self, kb_use_case: KnowledgeBaseUseCase, mock_document_store: AsyncMock
    ) -> None:
        """get() passes the kb_id to the document store."""
        mock_document_store.get_kb.return_value = None

        await kb_use_case.get(kb_id="kb-abc")

        mock_document_store.get_kb.assert_called_once_with("kb-abc")


# ---------------------------------------------------------------------------
# Delete
# ---------------------------------------------------------------------------

class TestKnowledgeBaseUseCaseDelete:
    """Tests for KB deletion."""

    async def test_delete_calls_store_delete_kb(
        self, kb_use_case: KnowledgeBaseUseCase, mock_document_store: AsyncMock
    ) -> None:
        """delete() delegates to document_store.delete_kb()."""
        await kb_use_case.delete(kb_id="kb-to-delete")

        mock_document_store.delete_kb.assert_called_once_with("kb-to-delete")

    async def test_delete_returns_none(
        self, kb_use_case: KnowledgeBaseUseCase, mock_document_store: AsyncMock
    ) -> None:
        """delete() returns None (no return value)."""
        mock_document_store.delete_kb.return_value = None

        result = await kb_use_case.delete(kb_id="kb-1")

        assert result is None
