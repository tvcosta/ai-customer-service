"""LLM port interface for language model operations."""

from __future__ import annotations

from abc import ABC, abstractmethod


class LLMPort(ABC):
    """Abstract interface for language model providers."""

    @abstractmethod
    async def generate(self, prompt: str, context: str) -> str:
        """Generate text based on prompt and context.

        Args:
            prompt: The instruction prompt for the LLM.
            context: The contextual information to ground the response.

        Returns:
            Generated text response.
        """
        ...

    @abstractmethod
    async def embed(self, text: str) -> list[float]:
        """Generate embedding vector for the given text.

        Args:
            text: Input text to embed.

        Returns:
            Embedding vector as list of floats.
        """
        ...
