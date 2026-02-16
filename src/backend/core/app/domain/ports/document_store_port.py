"""Document store port interface."""

from __future__ import annotations

from abc import ABC, abstractmethod

from app.domain.models.document import Document, DocumentStatus
from app.domain.models.knowledge_base import KnowledgeBase


class DocumentStorePort(ABC):
    """Abstract interface for document and knowledge base persistence."""

    @abstractmethod
    async def create_kb(self, kb: KnowledgeBase) -> KnowledgeBase:
        """Create a new knowledge base.

        Args:
            kb: Knowledge base entity to create.

        Returns:
            Created knowledge base entity.
        """
        ...

    @abstractmethod
    async def get_kb(self, kb_id: str) -> KnowledgeBase | None:
        """Retrieve a knowledge base by ID.

        Args:
            kb_id: Knowledge base ID.

        Returns:
            Knowledge base entity if found, None otherwise.
        """
        ...

    @abstractmethod
    async def list_kbs(self) -> list[KnowledgeBase]:
        """List all knowledge bases.

        Returns:
            List of all knowledge bases.
        """
        ...

    @abstractmethod
    async def delete_kb(self, kb_id: str) -> None:
        """Delete a knowledge base.

        Args:
            kb_id: Knowledge base ID to delete.
        """
        ...

    @abstractmethod
    async def save_document(self, document: Document) -> Document:
        """Save a document entity.

        Args:
            document: Document entity to save.

        Returns:
            Saved document entity.
        """
        ...

    @abstractmethod
    async def get_document(self, document_id: str) -> Document | None:
        """Retrieve a document by ID.

        Args:
            document_id: Document ID.

        Returns:
            Document entity if found, None otherwise.
        """
        ...

    @abstractmethod
    async def list_documents(self, kb_id: str) -> list[Document]:
        """List all documents in a knowledge base.

        Args:
            kb_id: Knowledge base ID.

        Returns:
            List of documents in the knowledge base.
        """
        ...

    @abstractmethod
    async def delete_document(self, document_id: str) -> None:
        """Delete a document.

        Args:
            document_id: Document ID to delete.
        """
        ...

    @abstractmethod
    async def update_document_status(
        self, document_id: str, status: DocumentStatus, chunks_count: int = 0
    ) -> None:
        """Update document processing status.

        Args:
            document_id: Document ID to update.
            status: New status.
            chunks_count: Number of chunks created from the document.
        """
        ...
