"""Dependency injection setup."""

from __future__ import annotations

from app.application.use_cases.document_use_case import DocumentUseCase
from app.application.use_cases.interaction_use_case import InteractionUseCase
from app.application.use_cases.knowledge_base_use_case import KnowledgeBaseUseCase
from app.application.use_cases.query_use_case import QueryUseCase
from app.domain.services.grounding_service import GroundingService
from app.infrastructure.llm.stub import StubLLMProvider
from app.infrastructure.persistence.in_memory_store import (
    InMemoryDocumentStore,
    InMemoryInteractionStore,
)
from app.infrastructure.vectorstore.in_memory_store import InMemoryVectorStore

# Singletons for in-memory stores
_llm = StubLLMProvider()
_vectorstore = InMemoryVectorStore()
_document_store = InMemoryDocumentStore()
_interaction_store = InMemoryInteractionStore()
_grounding_service = GroundingService()


def get_query_use_case() -> QueryUseCase:
    """Get query use case with dependencies.

    Returns:
        Configured query use case instance.
    """
    return QueryUseCase(_llm, _vectorstore, _interaction_store, _grounding_service)


def get_kb_use_case() -> KnowledgeBaseUseCase:
    """Get knowledge base use case with dependencies.

    Returns:
        Configured knowledge base use case instance.
    """
    return KnowledgeBaseUseCase(_document_store)


def get_document_use_case() -> DocumentUseCase:
    """Get document use case with dependencies.

    Returns:
        Configured document use case instance.
    """
    return DocumentUseCase(_document_store, _vectorstore)


def get_interaction_use_case() -> InteractionUseCase:
    """Get interaction use case with dependencies.

    Returns:
        Configured interaction use case instance.
    """
    return InteractionUseCase(_interaction_store)
