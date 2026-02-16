"""Interaction store port interface."""

from __future__ import annotations

from abc import ABC, abstractmethod

from app.domain.models.interaction import Interaction


class InteractionStorePort(ABC):
    """Abstract interface for interaction history persistence."""

    @abstractmethod
    async def save(self, interaction: Interaction) -> Interaction:
        """Save an interaction.

        Args:
            interaction: Interaction entity to save.

        Returns:
            Saved interaction entity.
        """
        ...

    @abstractmethod
    async def get(self, interaction_id: str) -> Interaction | None:
        """Retrieve an interaction by ID.

        Args:
            interaction_id: Interaction ID.

        Returns:
            Interaction entity if found, None otherwise.
        """
        ...

    @abstractmethod
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
        ...
