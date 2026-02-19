"""Shared fixtures for all test modules.

Provides mock implementations of all ports and pre-built sample domain objects
used across unit test suites.
"""

from __future__ import annotations

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.domain.models.chunk import Chunk
from app.domain.models.citation import Citation
from app.domain.models.document import Document, DocumentStatus
from app.domain.models.grounding import GroundingDecision, QueryResult
from app.domain.models.interaction import Interaction, InteractionStatus
from app.domain.models.knowledge_base import KnowledgeBase
from app.domain.ports.document_store_port import DocumentStorePort
from app.domain.ports.interaction_store_port import InteractionStorePort
from app.domain.ports.llm_port import LLMPort
from app.domain.ports.vectorstore_port import VectorStorePort
from app.domain.services.grounding_service import GroundingService
from app.application.use_cases.query_use_case import QueryUseCase


# ---------------------------------------------------------------------------
# Port mocks
# ---------------------------------------------------------------------------

@pytest.fixture
def mock_llm() -> AsyncMock:
    """Mock LLMPort with async embed and generate methods."""
    mock = AsyncMock(spec=LLMPort)
    mock.embed.return_value = [0.1, 0.2, 0.3, 0.4, 0.5]
    mock.generate.return_value = "This is a generated answer."
    return mock


@pytest.fixture
def mock_vectorstore() -> AsyncMock:
    """Mock VectorStorePort with async methods."""
    mock = AsyncMock(spec=VectorStorePort)
    mock.store.return_value = None
    mock.search.return_value = []
    mock.delete_by_document.return_value = None
    mock.delete_by_kb.return_value = None
    return mock


@pytest.fixture
def mock_interaction_store() -> AsyncMock:
    """Mock InteractionStorePort with async methods."""
    mock = AsyncMock(spec=InteractionStorePort)
    mock.save.side_effect = lambda interaction: interaction
    mock.get.return_value = None
    mock.list_all.return_value = []
    return mock


@pytest.fixture
def mock_document_store() -> AsyncMock:
    """Mock DocumentStorePort with async methods."""
    mock = AsyncMock(spec=DocumentStorePort)
    mock.create_kb.side_effect = lambda kb: kb
    mock.get_kb.return_value = None
    mock.list_kbs.return_value = []
    mock.delete_kb.return_value = None
    mock.save_document.side_effect = lambda doc: doc
    mock.get_document.return_value = None
    mock.list_documents.return_value = []
    mock.delete_document.return_value = None
    mock.update_document_status.return_value = None
    return mock


# ---------------------------------------------------------------------------
# Sample domain objects
# ---------------------------------------------------------------------------

@pytest.fixture
def sample_kb() -> KnowledgeBase:
    """A sample KnowledgeBase entity."""
    return KnowledgeBase(
        id="kb-001",
        name="Test KB",
        description="A knowledge base for testing",
        created_at=datetime(2026, 1, 1, tzinfo=UTC),
        updated_at=datetime(2026, 1, 2, tzinfo=UTC),
    )


@pytest.fixture
def sample_document(sample_kb: KnowledgeBase) -> Document:
    """A sample Document entity linked to sample_kb."""
    return Document(
        id="doc-001",
        kb_id=sample_kb.id,
        filename="test-document.pdf",
        content_hash="abc123def456",
        status=DocumentStatus.INDEXED,
        chunks_count=3,
        uploaded_at=datetime(2026, 1, 1, tzinfo=UTC),
    )


@pytest.fixture
def sample_chunk(sample_document: Document) -> Chunk:
    """A single sample Chunk value object."""
    return Chunk(
        id="chunk-001",
        document_id=sample_document.id,
        content="The refund policy allows returns within 30 days of purchase.",
        metadata={"source_document": "test-document.pdf", "page": 1},
        embedding=[0.1, 0.2, 0.3, 0.4, 0.5],
    )


@pytest.fixture
def sample_chunks(sample_document: Document) -> list[Chunk]:
    """A list of sample Chunk value objects."""
    return [
        Chunk(
            id="chunk-001",
            document_id=sample_document.id,
            content="The refund policy allows returns within 30 days of purchase.",
            metadata={"source_document": "test-document.pdf", "page": 1},
            embedding=[0.1, 0.2, 0.3, 0.4, 0.5],
        ),
        Chunk(
            id="chunk-002",
            document_id=sample_document.id,
            content="Customers must present the original receipt to claim a refund.",
            metadata={"source_document": "test-document.pdf", "page": 2},
            embedding=[0.2, 0.3, 0.4, 0.5, 0.6],
        ),
        Chunk(
            id="chunk-003",
            document_id=sample_document.id,
            content="Refunds are processed within 5-7 business days.",
            metadata={"source_document": "test-document.pdf", "page": 2},
            embedding=[0.3, 0.4, 0.5, 0.6, 0.7],
        ),
    ]


@pytest.fixture
def sample_citation() -> Citation:
    """A sample Citation value object."""
    return Citation(
        source_document="test-document.pdf",
        page=1,
        chunk_id="chunk-001",
        relevance_score=0.92,
    )


@pytest.fixture
def sample_interaction(sample_kb: KnowledgeBase, sample_citation: Citation) -> Interaction:
    """A sample answered Interaction entity."""
    return Interaction(
        id="interaction-001",
        kb_id=sample_kb.id,
        question="What is the refund policy?",
        answer="The refund policy allows returns within 30 days.",
        status=InteractionStatus.ANSWERED,
        citations=[sample_citation],
        created_at=datetime(2026, 1, 1, tzinfo=UTC),
    )


@pytest.fixture
def grounding_service() -> GroundingService:
    """A real GroundingService instance (pure domain logic, no mocks needed)."""
    return GroundingService()


@pytest.fixture
def query_use_case(
    mock_llm: AsyncMock,
    mock_vectorstore: AsyncMock,
    mock_interaction_store: AsyncMock,
    grounding_service: GroundingService,
) -> QueryUseCase:
    """QueryUseCase wired up with mocked ports and a real GroundingService."""
    return QueryUseCase(
        llm=mock_llm,
        vectorstore=mock_vectorstore,
        interaction_store=mock_interaction_store,
        grounding_service=grounding_service,
    )
