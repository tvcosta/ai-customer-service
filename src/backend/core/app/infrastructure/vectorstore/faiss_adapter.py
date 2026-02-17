"""FAISS vector store adapter."""

from __future__ import annotations

import faiss
import numpy as np

from app.domain.models.chunk import Chunk
from app.domain.ports.vectorstore_port import VectorStorePort


class FaissVectorStore(VectorStorePort):
    """FAISS-based vector store implementation.

    This adapter uses FAISS (Facebook AI Similarity Search) for efficient
    similarity search over chunk embeddings. It maintains an in-memory index
    with L2 distance metric.

    Attributes:
        _dimension: Dimension of the embedding vectors.
        _index: FAISS index for similarity search.
        _chunks: List of chunks ordered by their position in the index.
        _chunk_map: Mapping from chunk ID to position in _chunks list.
    """

    def __init__(self, dimension: int = 768) -> None:
        """Initialize FAISS vector store.

        Args:
            dimension: Dimension of the embedding vectors (default: 768 for Ollama).
        """
        self._dimension = dimension
        self._index = faiss.IndexFlatL2(dimension)
        self._chunks: list[Chunk] = []  # ordered list matching index positions
        self._chunk_map: dict[str, int] = {}  # chunk_id -> position in _chunks

    async def store(self, chunks: list[Chunk]) -> None:
        """Store chunks with their embeddings in the vector store.

        Args:
            chunks: List of chunks to store. Chunks without embeddings are skipped.
        """
        vectors = []
        for chunk in chunks:
            if chunk.embedding is None:
                continue
            pos = len(self._chunks)
            self._chunks.append(chunk)
            self._chunk_map[chunk.id] = pos
            vectors.append(chunk.embedding)

        if vectors:
            arr = np.array(vectors, dtype=np.float32)
            self._index.add(arr)

    async def search(
        self, query_embedding: list[float], kb_id: str, top_k: int = 5
    ) -> list[Chunk]:
        """Search for similar chunks using vector similarity.

        Args:
            query_embedding: Query vector to search for.
            kb_id: Knowledge base ID to scope the search (currently unused in basic impl).
            top_k: Maximum number of results to return.

        Returns:
            List of most similar chunks ordered by relevance.
        """
        if self._index.ntotal == 0:
            return []

        query = np.array([query_embedding], dtype=np.float32)
        # Search extra to allow filtering by kb_id
        k = min(top_k * 3, self._index.ntotal)
        distances, indices = self._index.search(query, k)

        results = []
        for idx in indices[0]:
            if idx < 0 or idx >= len(self._chunks):
                continue
            chunk = self._chunks[idx]
            # TODO: Filter by kb_id via document->kb mapping from document store
            # For now we return all matches since kb filtering needs cross-reference
            results.append(chunk)
            if len(results) >= top_k:
                break

        return results

    async def delete_by_document(self, document_id: str) -> None:
        """Delete all chunks associated with a document.

        Args:
            document_id: ID of the document whose chunks should be deleted.

        Note:
            FAISS doesn't support deletion, so we rebuild the entire index.
        """
        remaining = [c for c in self._chunks if c.document_id != document_id]
        self._rebuild(remaining)

    async def delete_by_kb(self, kb_id: str) -> None:
        """Delete all chunks associated with a knowledge base.

        Args:
            kb_id: ID of the knowledge base whose chunks should be deleted.

        Note:
            This operation requires document->kb mapping from the document store.
            Current implementation is a no-op; real implementation needs cross-reference.
        """
        # Would need document_store to resolve doc->kb mapping
        # For now this is a no-op; real implementation needs cross-reference
        pass

    def _rebuild(self, chunks: list[Chunk]) -> None:
        """Rebuild the FAISS index with the given chunks.

        Args:
            chunks: List of chunks to rebuild the index with.
        """
        self._index = faiss.IndexFlatL2(self._dimension)
        self._chunks = []
        self._chunk_map = {}
        vectors = []

        for chunk in chunks:
            if chunk.embedding is None:
                continue
            pos = len(self._chunks)
            self._chunks.append(chunk)
            self._chunk_map[chunk.id] = pos
            vectors.append(chunk.embedding)

        if vectors:
            arr = np.array(vectors, dtype=np.float32)
            self._index.add(arr)
