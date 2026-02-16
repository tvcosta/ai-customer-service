"""Interaction API routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query

from app.application.use_cases.interaction_use_case import InteractionUseCase
from app.dependencies import get_interaction_use_case
from app.interfaces.api.schemas.interaction import InteractionSchema
from app.interfaces.api.schemas.query import CitationSchema

router = APIRouter(prefix="/api/v1", tags=["interactions"])


@router.get("/interactions", response_model=list[InteractionSchema])
async def list_interactions(
    kb_id: str | None = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    use_case: InteractionUseCase = Depends(get_interaction_use_case),
) -> list[InteractionSchema]:
    """List interactions with optional filtering and pagination.

    Args:
        kb_id: Optional knowledge base ID to filter by.
        limit: Maximum number of results (1-200).
        offset: Number of results to skip.
        use_case: Injected interaction use case.

    Returns:
        List of interactions.
    """
    interactions = await use_case.list_all(kb_id=kb_id, limit=limit, offset=offset)
    return [
        InteractionSchema(
            id=i.id,
            kb_id=i.kb_id,
            question=i.question,
            answer=i.answer,
            status=i.status.value,
            citations=[
                CitationSchema(
                    source_document=c.source_document,
                    page=c.page,
                    chunk_id=c.chunk_id,
                    relevance_score=c.relevance_score,
                )
                for c in i.citations
            ],
            created_at=i.created_at,
        )
        for i in interactions
    ]


@router.get("/interactions/{interaction_id}", response_model=InteractionSchema)
async def get_interaction(
    interaction_id: str,
    use_case: InteractionUseCase = Depends(get_interaction_use_case),
) -> InteractionSchema:
    """Get an interaction by ID.

    Args:
        interaction_id: Interaction ID.
        use_case: Injected interaction use case.

    Returns:
        Interaction entity.

    Raises:
        HTTPException: If interaction is not found.
    """
    interaction = await use_case.get(interaction_id)
    if not interaction:
        raise HTTPException(status_code=404, detail="Interaction not found")
    return InteractionSchema(
        id=interaction.id,
        kb_id=interaction.kb_id,
        question=interaction.question,
        answer=interaction.answer,
        status=interaction.status.value,
        citations=[
            CitationSchema(
                source_document=c.source_document,
                page=c.page,
                chunk_id=c.chunk_id,
                relevance_score=c.relevance_score,
            )
            for c in interaction.citations
        ],
        created_at=interaction.created_at,
    )
