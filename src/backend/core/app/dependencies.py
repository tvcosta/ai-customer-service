"""Dependency injection setup."""

from __future__ import annotations

from pathlib import Path

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.application.use_cases.document_use_case import DocumentUseCase
from app.application.use_cases.interaction_use_case import InteractionUseCase
from app.application.use_cases.knowledge_base_use_case import KnowledgeBaseUseCase
from app.application.use_cases.query_use_case import QueryUseCase
from app.config import Settings
from app.domain.services.grounding_service import GroundingService
from app.infrastructure.llm.ollama import OllamaProvider
from app.infrastructure.persistence.sqlite_store import (
    Base,
    SqliteDocumentStore,
    SqliteInteractionStore,
)
from app.infrastructure.vectorstore.faiss_adapter import FaissVectorStore

_settings = Settings()

# Database engine and session factory
_db_dir = Path(_settings.database_url.replace("sqlite+aiosqlite:///", "")).parent
_db_dir.mkdir(parents=True, exist_ok=True)
_engine = create_async_engine(_settings.database_url, echo=False)
_session_factory = async_sessionmaker(_engine, expire_on_commit=False)

# Real adapter singletons
_llm = OllamaProvider(base_url=_settings.ollama_base_url, model=_settings.ollama_model)
_vectorstore = FaissVectorStore(dimension=768)
_document_store = SqliteDocumentStore(_session_factory)
_interaction_store = SqliteInteractionStore(_session_factory)
_grounding_service = GroundingService()


async def init_db() -> None:
    """Create database tables if they don't exist."""
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def shutdown() -> None:
    """Clean up resources on application shutdown."""
    await _llm.close()
    await _engine.dispose()


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
