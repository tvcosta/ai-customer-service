"""Pydantic schemas for knowledge base endpoints."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class CreateKnowledgeBaseSchema(BaseModel):
    """Request schema for creating a knowledge base."""

    name: str
    description: str | None = None


class KnowledgeBaseSchema(BaseModel):
    """Schema for knowledge base entity."""

    id: str
    name: str
    description: str | None = None
    created_at: datetime | None = None
