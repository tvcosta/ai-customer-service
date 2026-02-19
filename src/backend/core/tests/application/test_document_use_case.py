"""Unit tests for DocumentUseCase.

Tests cover upload, list, and delete operations.
DocumentStorePort and VectorStorePort are both mocked.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from unittest.mock import AsyncMock

import pytest

from app.domain.models.document import Document, DocumentStatus
from app.application.use_cases.document_use_case import DocumentUseCase


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def doc_use_case(
    mock_document_store: AsyncMock, mock_vectorstore: AsyncMock
) -> DocumentUseCase:
    """DocumentUseCase with mocked document store and vector store."""
    return DocumentUseCase(
        document_store=mock_document_store,
        vectorstore=mock_vectorstore,
    )


# ---------------------------------------------------------------------------
# Upload
# ---------------------------------------------------------------------------

class TestDocumentUseCaseUpload:
    """Tests for document upload."""

    async def test_upload_returns_document(
        self, doc_use_case: DocumentUseCase, mock_document_store: AsyncMock
    ) -> None:
        """upload() returns the Document entity that was passed to the store."""
        # The conftest side_effect returns the doc passed into save_document,
        # so we assert on the returned document's core fields rather than identity.
        result = await doc_use_case.upload(
            kb_id="kb-001",
            filename="report.pdf",
            content_hash="sha256abc",
        )

        assert isinstance(result, Document)
        assert result.kb_id == "kb-001"
        assert result.filename == "report.pdf"
        assert result.content_hash == "sha256abc"

    async def test_upload_calls_store_save_document(
        self, doc_use_case: DocumentUseCase, mock_document_store: AsyncMock
    ) -> None:
        """upload() delegates to document_store.save_document() with correct data."""
        mock_document_store.save_document.side_effect = lambda doc: doc

        await doc_use_case.upload(
            kb_id="kb-001",
            filename="invoice.pdf",
            content_hash="hash999",
        )

        mock_document_store.save_document.assert_called_once()
        saved_doc = mock_document_store.save_document.call_args[0][0]
        assert saved_doc.kb_id == "kb-001"
        assert saved_doc.filename == "invoice.pdf"
        assert saved_doc.content_hash == "hash999"

    async def test_upload_sets_status_to_pending(
        self, doc_use_case: DocumentUseCase, mock_document_store: AsyncMock
    ) -> None:
        """Newly uploaded documents always start with PENDING status."""
        mock_document_store.save_document.side_effect = lambda doc: doc

        await doc_use_case.upload(
            kb_id="kb-001",
            filename="file.pdf",
            content_hash="abc",
        )

        saved_doc = mock_document_store.save_document.call_args[0][0]
        assert saved_doc.status == DocumentStatus.PENDING

    async def test_upload_generates_uuid_for_id(
        self, doc_use_case: DocumentUseCase, mock_document_store: AsyncMock
    ) -> None:
        """upload() generates a UUID for the document id."""
        mock_document_store.save_document.side_effect = lambda doc: doc

        await doc_use_case.upload(
            kb_id="kb-001",
            filename="file.pdf",
            content_hash="abc",
        )

        saved_doc = mock_document_store.save_document.call_args[0][0]
        uuid.UUID(saved_doc.id)  # Raises ValueError if not valid UUID

    async def test_upload_sets_uploaded_at_timestamp(
        self, doc_use_case: DocumentUseCase, mock_document_store: AsyncMock
    ) -> None:
        """upload() sets uploaded_at to current UTC time."""
        mock_document_store.save_document.side_effect = lambda doc: doc

        await doc_use_case.upload(
            kb_id="kb-001",
            filename="file.pdf",
            content_hash="abc",
        )

        saved_doc = mock_document_store.save_document.call_args[0][0]
        assert saved_doc.uploaded_at is not None
        assert saved_doc.uploaded_at.tzinfo is not None

    async def test_upload_does_not_call_vectorstore(
        self, doc_use_case: DocumentUseCase, mock_vectorstore: AsyncMock,
        mock_document_store: AsyncMock
    ) -> None:
        """upload() only saves metadata; it does not write to the vector store."""
        mock_document_store.save_document.side_effect = lambda doc: doc

        await doc_use_case.upload(
            kb_id="kb-001",
            filename="file.pdf",
            content_hash="abc",
        )

        mock_vectorstore.store.assert_not_called()


# ---------------------------------------------------------------------------
# List documents
# ---------------------------------------------------------------------------

class TestDocumentUseCaseListDocuments:
    """Tests for listing documents."""

    async def test_list_documents_returns_empty_when_none(
        self, doc_use_case: DocumentUseCase, mock_document_store: AsyncMock
    ) -> None:
        """list_documents() returns an empty list when KB has no documents."""
        mock_document_store.list_documents.return_value = []

        result = await doc_use_case.list_documents(kb_id="kb-001")

        assert result == []

    async def test_list_documents_returns_all_documents_for_kb(
        self, doc_use_case: DocumentUseCase, mock_document_store: AsyncMock
    ) -> None:
        """list_documents() returns all documents associated with the KB."""
        docs = [
            Document(
                id="doc-1",
                kb_id="kb-001",
                filename="a.pdf",
                content_hash="hash1",
            ),
            Document(
                id="doc-2",
                kb_id="kb-001",
                filename="b.pdf",
                content_hash="hash2",
            ),
        ]
        mock_document_store.list_documents.return_value = docs

        result = await doc_use_case.list_documents(kb_id="kb-001")

        assert len(result) == 2
        assert result == docs

    async def test_list_documents_calls_store_with_kb_id(
        self, doc_use_case: DocumentUseCase, mock_document_store: AsyncMock
    ) -> None:
        """list_documents() passes kb_id to the document store."""
        mock_document_store.list_documents.return_value = []

        await doc_use_case.list_documents(kb_id="kb-xyz")

        mock_document_store.list_documents.assert_called_once_with("kb-xyz")


# ---------------------------------------------------------------------------
# Delete document
# ---------------------------------------------------------------------------

class TestDocumentUseCaseDelete:
    """Tests for document deletion."""

    async def test_delete_calls_vectorstore_delete_by_document(
        self, doc_use_case: DocumentUseCase, mock_vectorstore: AsyncMock,
        mock_document_store: AsyncMock
    ) -> None:
        """delete() removes vector chunks for the document first."""
        await doc_use_case.delete(kb_id="kb-001", document_id="doc-1")

        mock_vectorstore.delete_by_document.assert_called_once_with("doc-1")

    async def test_delete_calls_store_delete_document(
        self, doc_use_case: DocumentUseCase, mock_vectorstore: AsyncMock,
        mock_document_store: AsyncMock
    ) -> None:
        """delete() removes the document metadata from the store."""
        await doc_use_case.delete(kb_id="kb-001", document_id="doc-1")

        mock_document_store.delete_document.assert_called_once_with("doc-1")

    async def test_delete_removes_vectors_before_metadata(
        self, doc_use_case: DocumentUseCase, mock_vectorstore: AsyncMock,
        mock_document_store: AsyncMock
    ) -> None:
        """Vector store deletion is called before metadata deletion."""
        call_order: list[str] = []
        mock_vectorstore.delete_by_document.side_effect = (
            lambda _: call_order.append("vectorstore")
        )
        mock_document_store.delete_document.side_effect = (
            lambda _: call_order.append("document_store")
        )

        await doc_use_case.delete(kb_id="kb-001", document_id="doc-1")

        assert call_order == ["vectorstore", "document_store"]

    async def test_delete_returns_none(
        self, doc_use_case: DocumentUseCase, mock_document_store: AsyncMock
    ) -> None:
        """delete() returns None (no return value)."""
        result = await doc_use_case.delete(kb_id="kb-001", document_id="doc-1")

        assert result is None
