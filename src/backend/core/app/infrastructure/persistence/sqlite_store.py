"""SQLite persistence adapter using SQLAlchemy async."""

from __future__ import annotations

import json
from datetime import UTC, datetime

from sqlalchemy import Column, DateTime, Integer, String, Text, select
from sqlalchemy import delete as sa_delete
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from app.domain.models.citation import Citation
from app.domain.models.document import Document, DocumentStatus
from app.domain.models.interaction import Interaction, InteractionStatus
from app.domain.models.knowledge_base import KnowledgeBase
from app.domain.ports.document_store_port import DocumentStorePort
from app.domain.ports.interaction_store_port import InteractionStorePort


class Base(DeclarativeBase):
    """SQLAlchemy declarative base for all ORM models."""

    pass


class KBRow(Base):
    """Knowledge Base table schema."""

    __tablename__ = "knowledge_bases"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)


class DocumentRow(Base):
    """Document table schema."""

    __tablename__ = "documents"

    id = Column(String, primary_key=True)
    kb_id = Column(String, nullable=False, index=True)
    filename = Column(String, nullable=False)
    content_hash = Column(String, nullable=False)
    status = Column(String, nullable=False, default="pending")
    chunks_count = Column(Integer, default=0)
    uploaded_at = Column(DateTime, nullable=True)


class InteractionRow(Base):
    """Interaction table schema."""

    __tablename__ = "interactions"

    id = Column(String, primary_key=True)
    kb_id = Column(String, nullable=False, index=True)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=True)
    status = Column(String, nullable=False, default="unknown")
    citations_json = Column(Text, nullable=True)  # JSON array
    created_at = Column(DateTime, nullable=True)


class SqliteDocumentStore(DocumentStorePort):
    """SQLite implementation of document and knowledge base persistence.

    This adapter uses SQLAlchemy async with aiosqlite to persist
    knowledge bases and documents to a SQLite database.

    Attributes:
        _session_factory: SQLAlchemy session factory for database operations.
    """

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        """Initialize SQLite document store.

        Args:
            session_factory: SQLAlchemy async session factory.
        """
        self._session_factory = session_factory

    async def create_kb(self, kb: KnowledgeBase) -> KnowledgeBase:
        """Create a new knowledge base.

        Args:
            kb: Knowledge base entity to create.

        Returns:
            Created knowledge base entity.
        """
        async with self._session_factory() as session:
            row = KBRow(
                id=kb.id,
                name=kb.name,
                description=kb.description,
                created_at=kb.created_at,
                updated_at=kb.updated_at,
            )
            session.add(row)
            await session.commit()
        return kb

    async def get_kb(self, kb_id: str) -> KnowledgeBase | None:
        """Retrieve a knowledge base by ID.

        Args:
            kb_id: Knowledge base ID.

        Returns:
            Knowledge base entity if found, None otherwise.
        """
        async with self._session_factory() as session:
            row = await session.get(KBRow, kb_id)
            if not row:
                return None
            return KnowledgeBase(
                id=row.id,
                name=row.name,
                description=row.description,
                created_at=row.created_at,
                updated_at=row.updated_at,
            )

    async def list_kbs(self) -> list[KnowledgeBase]:
        """List all knowledge bases.

        Returns:
            List of all knowledge bases.
        """
        async with self._session_factory() as session:
            result = await session.execute(select(KBRow))
            return [
                KnowledgeBase(
                    id=r.id,
                    name=r.name,
                    description=r.description,
                    created_at=r.created_at,
                    updated_at=r.updated_at,
                )
                for r in result.scalars()
            ]

    async def delete_kb(self, kb_id: str) -> None:
        """Delete a knowledge base and all its documents.

        Args:
            kb_id: Knowledge base ID to delete.
        """
        async with self._session_factory() as session:
            await session.execute(sa_delete(DocumentRow).where(DocumentRow.kb_id == kb_id))
            await session.execute(sa_delete(KBRow).where(KBRow.id == kb_id))
            await session.commit()

    async def save_document(self, document: Document) -> Document:
        """Save a document entity.

        Args:
            document: Document entity to save.

        Returns:
            Saved document entity.
        """
        async with self._session_factory() as session:
            row = DocumentRow(
                id=document.id,
                kb_id=document.kb_id,
                filename=document.filename,
                content_hash=document.content_hash,
                status=document.status.value,
                chunks_count=document.chunks_count,
                uploaded_at=document.uploaded_at,
            )
            session.add(row)
            await session.commit()
        return document

    async def get_document(self, document_id: str) -> Document | None:
        """Retrieve a document by ID.

        Args:
            document_id: Document ID.

        Returns:
            Document entity if found, None otherwise.
        """
        async with self._session_factory() as session:
            row = await session.get(DocumentRow, document_id)
            if not row:
                return None
            return Document(
                id=row.id,
                kb_id=row.kb_id,
                filename=row.filename,
                content_hash=row.content_hash,
                status=DocumentStatus(row.status),
                chunks_count=row.chunks_count,
                uploaded_at=row.uploaded_at,
            )

    async def list_documents(self, kb_id: str) -> list[Document]:
        """List all documents in a knowledge base.

        Args:
            kb_id: Knowledge base ID.

        Returns:
            List of documents in the knowledge base.
        """
        async with self._session_factory() as session:
            result = await session.execute(select(DocumentRow).where(DocumentRow.kb_id == kb_id))
            return [
                Document(
                    id=r.id,
                    kb_id=r.kb_id,
                    filename=r.filename,
                    content_hash=r.content_hash,
                    status=DocumentStatus(r.status),
                    chunks_count=r.chunks_count,
                    uploaded_at=r.uploaded_at,
                )
                for r in result.scalars()
            ]

    async def delete_document(self, document_id: str) -> None:
        """Delete a document.

        Args:
            document_id: Document ID to delete.
        """
        async with self._session_factory() as session:
            await session.execute(sa_delete(DocumentRow).where(DocumentRow.id == document_id))
            await session.commit()

    async def update_document_status(
        self, document_id: str, status: DocumentStatus, chunks_count: int = 0
    ) -> None:
        """Update document processing status.

        Args:
            document_id: Document ID to update.
            status: New status.
            chunks_count: Number of chunks created from the document.
        """
        async with self._session_factory() as session:
            row = await session.get(DocumentRow, document_id)
            if row:
                row.status = status.value
                row.chunks_count = chunks_count
                await session.commit()


class SqliteInteractionStore(InteractionStorePort):
    """SQLite implementation of interaction history persistence.

    This adapter uses SQLAlchemy async with aiosqlite to persist
    user interactions and their outcomes.

    Attributes:
        _session_factory: SQLAlchemy session factory for database operations.
    """

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        """Initialize SQLite interaction store.

        Args:
            session_factory: SQLAlchemy async session factory.
        """
        self._session_factory = session_factory

    async def save(self, interaction: Interaction) -> Interaction:
        """Save an interaction.

        Args:
            interaction: Interaction entity to save.

        Returns:
            Saved interaction entity.
        """
        citations_json = json.dumps(
            [
                {
                    "source_document": c.source_document,
                    "page": c.page,
                    "chunk_id": c.chunk_id,
                    "relevance_score": c.relevance_score,
                }
                for c in interaction.citations
            ]
        )
        async with self._session_factory() as session:
            row = InteractionRow(
                id=interaction.id,
                kb_id=interaction.kb_id,
                question=interaction.question,
                answer=interaction.answer,
                status=interaction.status.value,
                citations_json=citations_json,
                created_at=interaction.created_at or datetime.now(UTC),
            )
            session.add(row)
            await session.commit()
        return interaction

    async def get(self, interaction_id: str) -> Interaction | None:
        """Retrieve an interaction by ID.

        Args:
            interaction_id: Interaction ID.

        Returns:
            Interaction entity if found, None otherwise.
        """
        async with self._session_factory() as session:
            row = await session.get(InteractionRow, interaction_id)
            if not row:
                return None
            citations = [Citation(**c) for c in json.loads(row.citations_json or "[]")]
            return Interaction(
                id=row.id,
                kb_id=row.kb_id,
                question=row.question,
                answer=row.answer,
                status=InteractionStatus(row.status),
                citations=citations,
                created_at=row.created_at,
            )

    async def list_all(
        self, kb_id: str | None = None, limit: int = 50, offset: int = 0
    ) -> list[Interaction]:
        """List interactions with optional filtering and pagination.

        Args:
            kb_id: Optional knowledge base ID to filter by.
            limit: Maximum number of results.
            offset: Number of results to skip.

        Returns:
            List of interactions ordered by creation time descending.
        """
        async with self._session_factory() as session:
            stmt = (
                select(InteractionRow)
                .order_by(InteractionRow.created_at.desc())
                .offset(offset)
                .limit(limit)
            )
            if kb_id:
                stmt = stmt.where(InteractionRow.kb_id == kb_id)
            result = await session.execute(stmt)

            interactions = []
            for row in result.scalars():
                citations = [Citation(**c) for c in json.loads(row.citations_json or "[]")]
                interactions.append(
                    Interaction(
                        id=row.id,
                        kb_id=row.kb_id,
                        question=row.question,
                        answer=row.answer,
                        status=InteractionStatus(row.status),
                        citations=citations,
                        created_at=row.created_at,
                    )
                )
            return interactions
