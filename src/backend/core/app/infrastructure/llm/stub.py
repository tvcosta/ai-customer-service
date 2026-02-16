"""Stub LLM provider for development/testing."""

from __future__ import annotations

from app.domain.ports.llm_port import LLMPort


class StubLLMProvider(LLMPort):
    """Stub implementation of LLM provider for development."""

    async def generate(self, prompt: str, context: str) -> str:
        """Generate a stub response.

        Args:
            prompt: The instruction prompt.
            context: The contextual information.

        Returns:
            Stub response message.
        """
        return "This is a stub response. Configure a real LLM provider for actual answers."

    async def embed(self, text: str) -> list[float]:
        """Generate a stub embedding vector.

        Args:
            text: Input text to embed.

        Returns:
            Stub embedding vector (384 dimensions).
        """
        return [0.0] * 384
