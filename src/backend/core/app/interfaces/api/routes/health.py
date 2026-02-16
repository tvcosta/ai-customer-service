"""Health check endpoint for service monitoring."""

from __future__ import annotations

from typing import Literal

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1", tags=["Health"])


class HealthResponse(BaseModel):
    """Health check response schema."""

    status: Literal["healthy"]


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Health check endpoint.

    Returns:
        Health status indicating service is operational.
    """
    return HealthResponse(status="healthy")
