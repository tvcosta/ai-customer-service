"""Pydantic schemas for document endpoints."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class DocumentSchema(BaseModel):
    """Schema for document entity."""

    id: str
    kb_id: str
    filename: str
    status: str
    chunks_count: int
    uploaded_at: datetime | None = None
