"""Dashboard statistics schema."""

from __future__ import annotations

from pydantic import BaseModel


class DashboardStatsSchema(BaseModel):
    """Aggregated dashboard statistics."""

    total_interactions: int
    answered_count: int
    unknown_count: int
    knowledge_base_count: int
    document_count: int
