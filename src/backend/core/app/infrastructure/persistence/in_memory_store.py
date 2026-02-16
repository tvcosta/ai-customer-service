"""In-memory implementations of persistence ports for development/testing."""

from __future__ import annotations

from app.domain.models.document import Document, DocumentStatus
from app.domain.models.interaction import Interaction
from app.domain.models.knowledge_base import KnowledgeBase
from app.domain.ports.document_store_port import DocumentStorePort
from app.domain.ports.interaction_store_port import InteractionStorePort


class InMemoryDocumentStore(DocumentStorePort):
    """In-memory implementation of document store for development."""

    def __init__(self) -> None:
        """Initialize the in-memory document store."""
        self._kbs: dict[str, KnowledgeBase] = {}
        self._documents: dict[str, Document] = {}

    async def create_kb(self, kb: KnowledgeBase) -> KnowledgeBase:
        """Create a new knowledge base."""
        self._kbs[kb.id] = kb
        return kb

    async def get_kb(self, kb_id: str) -> KnowledgeBase | None:
        """Retrieve a knowledge base by ID."""
        return self._kbs.get(kb_id)

    async def list_kbs(self) -> list[KnowledgeBase]:
        """List all knowledge bases."""
        return list(self._kbs.values())

    async def delete_kb(self, kb_id: str) -> None:
        """Delete a knowledge base."""
        self._kbs.pop(kb_id, None)
        self._documents = {k: v for k, v in self._documents.items() if v.kb_id != kb_id}

    async def save_document(self, document: Document) -> Document:
        """Save a document entity."""
        self._documents[document.id] = document
        return document

    async def get_document(self, document_id: str) -> Document | None:
        """Retrieve a document by ID."""
        return self._documents.get(document_id)

    async def list_documents(self, kb_id: str) -> list[Document]:
        """List all documents in a knowledge base."""
        return [d for d in self._documents.values() if d.kb_id == kb_id]

    async def delete_document(self, document_id: str) -> None:
        """Delete a document."""
        self._documents.pop(document_id, None)

    async def update_document_status(
        self, document_id: str, status: DocumentStatus, chunks_count: int = 0
    ) -> None:
        """Update document processing status."""
        doc = self._documents.get(document_id)
        if doc:
            doc.status = status
            doc.chunks_count = chunks_count


class InMemoryInteractionStore(InteractionStorePort):
    """In-memory implementation of interaction store for development."""

    def __init__(self) -> None:
        """Initialize the in-memory interaction store."""
        self._interactions: dict[str, Interaction] = {}

    async def save(self, interaction: Interaction) -> Interaction:
        """Save an interaction."""
        self._interactions[interaction.id] = interaction
        return interaction

    async def get(self, interaction_id: str) -> Interaction | None:
        """Retrieve an interaction by ID."""
        return self._interactions.get(interaction_id)

    async def list_all(
        self, kb_id: str | None = None, limit: int = 50, offset: int = 0
    ) -> list[Interaction]:
        """List interactions with optional filtering and pagination."""
        items = list(self._interactions.values())
        if kb_id:
            items = [i for i in items if i.kb_id == kb_id]
        items.sort(key=lambda i: i.created_at or "", reverse=True)
        return items[offset : offset + limit]
