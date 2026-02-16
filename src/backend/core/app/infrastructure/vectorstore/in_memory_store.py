"""In-memory vector store for development/testing."""

from __future__ import annotations

from app.domain.models.chunk import Chunk
from app.domain.ports.vectorstore_port import VectorStorePort


class InMemoryVectorStore(VectorStorePort):
    """In-memory implementation of vector store for development."""

    def __init__(self) -> None:
        """Initialize the in-memory vector store."""
        self._chunks: dict[str, Chunk] = {}

    async def store(self, chunks: list[Chunk]) -> None:
        """Store chunks with their embeddings."""
        for chunk in chunks:
            self._chunks[chunk.id] = chunk

    async def search(
        self, query_embedding: list[float], kb_id: str, top_k: int = 5
    ) -> list[Chunk]:
        """Search for similar chunks using vector similarity.

        Note: This is a stub implementation that returns all chunks for the KB
        without performing real vector similarity search.
        """
        all_chunks = [c for c in self._chunks.values()]
        return all_chunks[:top_k]

    async def delete_by_document(self, document_id: str) -> None:
        """Delete all chunks associated with a document."""
        self._chunks = {
            k: v for k, v in self._chunks.items() if v.document_id != document_id
        }

    async def delete_by_kb(self, kb_id: str) -> None:
        """Delete all chunks associated with a knowledge base.

        Note: Would need document-to-kb mapping in real implementation.
        """
        pass
