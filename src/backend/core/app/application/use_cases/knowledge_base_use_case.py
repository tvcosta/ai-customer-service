"""Knowledge base CRUD use case."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from app.domain.models.knowledge_base import KnowledgeBase
from app.domain.ports.document_store_port import DocumentStorePort


class KnowledgeBaseUseCase:
    """Use case for knowledge base management."""

    def __init__(self, document_store: DocumentStorePort) -> None:
        """Initialize the knowledge base use case.

        Args:
            document_store: Document store port.
        """
        self._store = document_store

    async def create(
        self, name: str, description: str | None = None
    ) -> KnowledgeBase:
        """Create a new knowledge base.

        Args:
            name: Knowledge base name.
            description: Optional description.

        Returns:
            Created knowledge base entity.
        """
        kb = KnowledgeBase(
            id=str(uuid.uuid4()),
            name=name,
            description=description,
            created_at=datetime.now(timezone.utc),
        )
        return await self._store.create_kb(kb)

    async def list_all(self) -> list[KnowledgeBase]:
        """List all knowledge bases.

        Returns:
            List of all knowledge bases.
        """
        return await self._store.list_kbs()

    async def get(self, kb_id: str) -> KnowledgeBase | None:
        """Get a knowledge base by ID.

        Args:
            kb_id: Knowledge base ID.

        Returns:
            Knowledge base if found, None otherwise.
        """
        return await self._store.get_kb(kb_id)

    async def delete(self, kb_id: str) -> None:
        """Delete a knowledge base.

        Args:
            kb_id: Knowledge base ID to delete.
        """
        await self._store.delete_kb(kb_id)
