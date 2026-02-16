"""Interaction history use case."""

from __future__ import annotations

from app.domain.models.interaction import Interaction
from app.domain.ports.interaction_store_port import InteractionStorePort


class InteractionUseCase:
    """Use case for interaction history management."""

    def __init__(self, interaction_store: InteractionStorePort) -> None:
        """Initialize the interaction use case.

        Args:
            interaction_store: Interaction store port.
        """
        self._store = interaction_store

    async def list_all(
        self, kb_id: str | None = None, limit: int = 50, offset: int = 0
    ) -> list[Interaction]:
        """List interactions with optional filtering and pagination.

        Args:
            kb_id: Optional knowledge base ID to filter by.
            limit: Maximum number of results.
            offset: Number of results to skip.

        Returns:
            List of interactions.
        """
        return await self._store.list_all(kb_id=kb_id, limit=limit, offset=offset)

    async def get(self, interaction_id: str) -> Interaction | None:
        """Get an interaction by ID.

        Args:
            interaction_id: Interaction ID.

        Returns:
            Interaction if found, None otherwise.
        """
        return await self._store.get(interaction_id)
