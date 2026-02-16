"""Pydantic schemas for query endpoints."""

from __future__ import annotations

from pydantic import BaseModel, Field


class QueryRequestSchema(BaseModel):
    """Request schema for query endpoint."""

    knowledge_base_id: str
    question: str


class CitationSchema(BaseModel):
    """Schema for citation information."""

    source_document: str
    page: int | None = None
    chunk_id: str
    relevance_score: float


class QueryResponseSchema(BaseModel):
    """Response schema for query endpoint."""

    status: str
    answer: str | None = None
    citations: list[CitationSchema] = Field(default_factory=list)
    interaction_id: str
    error: str | None = None
