"""Vector store port interface for semantic search operations."""

from __future__ import annotations

from abc import ABC, abstractmethod

from app.domain.models.chunk import Chunk


class VectorStorePort(ABC):
    """Abstract interface for vector storage and retrieval operations."""

    @abstractmethod
    async def store(self, chunks: list[Chunk]) -> None:
        """Store chunks with their embeddings in the vector store.

        Args:
            chunks: List of chunks to store.
        """
        ...

    @abstractmethod
    async def search(
        self, query_embedding: list[float], kb_id: str, top_k: int = 5
    ) -> list[Chunk]:
        """Search for similar chunks using vector similarity.

        Args:
            query_embedding: Query vector to search for.
            kb_id: Knowledge base ID to scope the search.
            top_k: Maximum number of results to return.

        Returns:
            List of most similar chunks.
        """
        ...

    @abstractmethod
    async def delete_by_document(self, document_id: str) -> None:
        """Delete all chunks associated with a document.

        Args:
            document_id: ID of the document whose chunks should be deleted.
        """
        ...

    @abstractmethod
    async def delete_by_kb(self, kb_id: str) -> None:
        """Delete all chunks associated with a knowledge base.

        Args:
            kb_id: ID of the knowledge base whose chunks should be deleted.
        """
        ...
