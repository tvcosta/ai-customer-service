"""Document management use case."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from app.domain.models.document import Document, DocumentStatus
from app.domain.ports.document_store_port import DocumentStorePort
from app.domain.ports.vectorstore_port import VectorStorePort


class DocumentUseCase:
    """Use case for document management."""

    def __init__(
        self, document_store: DocumentStorePort, vectorstore: VectorStorePort
    ) -> None:
        """Initialize the document use case.

        Args:
            document_store: Document store port.
            vectorstore: Vector store port.
        """
        self._store = document_store
        self._vectorstore = vectorstore

    async def upload(
        self, kb_id: str, filename: str, content_hash: str
    ) -> Document:
        """Upload a document to a knowledge base.

        Args:
            kb_id: Knowledge base ID.
            filename: Document filename.
            content_hash: SHA-256 hash of document content.

        Returns:
            Created document entity.
        """
        doc = Document(
            id=str(uuid.uuid4()),
            kb_id=kb_id,
            filename=filename,
            content_hash=content_hash,
            status=DocumentStatus.PENDING,
            uploaded_at=datetime.now(UTC),
        )
        return await self._store.save_document(doc)

    async def list_documents(self, kb_id: str) -> list[Document]:
        """List all documents in a knowledge base.

        Args:
            kb_id: Knowledge base ID.

        Returns:
            List of documents.
        """
        return await self._store.list_documents(kb_id)

    async def delete(self, kb_id: str, document_id: str) -> None:
        """Delete a document and its chunks.

        Args:
            kb_id: Knowledge base ID (for validation).
            document_id: Document ID to delete.
        """
        await self._vectorstore.delete_by_document(document_id)
        await self._store.delete_document(document_id)
