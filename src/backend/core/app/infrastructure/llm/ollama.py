"""Ollama LLM provider implementation."""

from __future__ import annotations

import httpx

from app.domain.ports.llm_port import LLMPort


class OllamaProvider(LLMPort):
    """Ollama LLM provider using local or remote Ollama service.

    This adapter communicates with the Ollama API to generate text
    completions and embeddings using specified models.

    Attributes:
        _base_url: Base URL of the Ollama API endpoint.
        _model: Model name to use for generation and embedding.
        _client: Async HTTP client for API requests.
    """

    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        model: str = "llama3.2",
    ) -> None:
        """Initialize Ollama provider.

        Args:
            base_url: Base URL of the Ollama API endpoint.
            model: Model name to use for generation and embedding.
        """
        self._base_url = base_url.rstrip("/")
        self._model = model
        self._client = httpx.AsyncClient(base_url=self._base_url, timeout=120.0)

    async def generate(self, prompt: str, context: str) -> str:
        """Generate text based on prompt and context.

        Args:
            prompt: The instruction prompt for the LLM.
            context: The contextual information to ground the response.

        Returns:
            Generated text response.

        Raises:
            httpx.HTTPError: If the API request fails.
        """
        full_prompt = f"{context}\n\n{prompt}"
        response = await self._client.post(
            "/api/generate",
            json={
                "model": self._model,
                "prompt": full_prompt,
                "stream": False,
            },
        )
        response.raise_for_status()
        data = response.json()
        return data["response"]

    async def embed(self, text: str) -> list[float]:
        """Generate embedding vector for the given text.

        Args:
            text: Input text to embed.

        Returns:
            Embedding vector as list of floats.

        Raises:
            httpx.HTTPError: If the API request fails.
        """
        response = await self._client.post(
            "/api/embed",
            json={
                "model": self._model,
                "input": text,
            },
        )
        response.raise_for_status()
        data = response.json()
        # Ollama returns {"embeddings": [[...]]}
        return data["embeddings"][0]

    async def close(self) -> None:
        """Close the HTTP client connection.

        This method should be called during application shutdown
        to properly release HTTP resources.
        """
        await self._client.aclose()
