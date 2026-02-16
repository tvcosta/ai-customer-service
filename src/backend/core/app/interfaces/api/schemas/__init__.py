"""Pydantic schemas for request and response validation."""

from __future__ import annotations

from app.interfaces.api.schemas.document import DocumentSchema
from app.interfaces.api.schemas.interaction import InteractionSchema
from app.interfaces.api.schemas.knowledge_base import (
    CreateKnowledgeBaseSchema,
    KnowledgeBaseSchema,
)
from app.interfaces.api.schemas.query import (
    CitationSchema,
    QueryRequestSchema,
    QueryResponseSchema,
)

__all__ = [
    "QueryRequestSchema",
    "QueryResponseSchema",
    "CitationSchema",
    "CreateKnowledgeBaseSchema",
    "KnowledgeBaseSchema",
    "DocumentSchema",
    "InteractionSchema",
]
