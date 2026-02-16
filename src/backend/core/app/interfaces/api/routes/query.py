"""Query API routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from app.application.use_cases.query_use_case import QueryUseCase
from app.dependencies import get_query_use_case
from app.interfaces.api.schemas.query import (
    CitationSchema,
    QueryRequestSchema,
    QueryResponseSchema,
)

router = APIRouter(prefix="/api/v1", tags=["query"])


@router.post("/query", response_model=QueryResponseSchema)
async def query(
    request: QueryRequestSchema, use_case: QueryUseCase = Depends(get_query_use_case)
) -> QueryResponseSchema:
    """Execute a query against a knowledge base.

    Args:
        request: Query request with knowledge base ID and question.
        use_case: Injected query use case.

    Returns:
        Query response with answer or unknown status.
    """
    result = await use_case.execute(request.knowledge_base_id, request.question)
    return QueryResponseSchema(
        status=result.status,
        answer=result.answer,
        citations=[
            CitationSchema(
                source_document=c.source_document,
                page=c.page,
                chunk_id=c.chunk_id,
                relevance_score=c.relevance_score,
            )
            for c in result.citations
        ],
        interaction_id=result.interaction_id,
    )
