"""Application-layer data transfer objects."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class QueryInput:
    """Input DTO for query use case."""

    knowledge_base_id: str
    question: str


@dataclass(frozen=True)
class CreateKnowledgeBaseInput:
    """Input DTO for knowledge base creation."""

    name: str
    description: str | None = None
