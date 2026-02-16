"""Pydantic schemas for interaction endpoints."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from app.interfaces.api.schemas.query import CitationSchema


class InteractionSchema(BaseModel):
    """Schema for interaction entity."""

    id: str
    kb_id: str
    question: str
    answer: str | None = None
    status: str
    citations: list[CitationSchema] = Field(default_factory=list)
    created_at: datetime | None = None
