"""Dashboard statistics API route."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from app.application.use_cases.document_use_case import DocumentUseCase
from app.application.use_cases.interaction_use_case import InteractionUseCase
from app.application.use_cases.knowledge_base_use_case import KnowledgeBaseUseCase
from app.dependencies import get_document_use_case, get_interaction_use_case, get_kb_use_case
from app.interfaces.api.schemas.dashboard import DashboardStatsSchema

router = APIRouter(prefix="/api/v1", tags=["dashboard"])


@router.get("/dashboard/stats", response_model=DashboardStatsSchema)
async def get_dashboard_stats(
    kb_use_case: KnowledgeBaseUseCase = Depends(get_kb_use_case),
    doc_use_case: DocumentUseCase = Depends(get_document_use_case),
    interaction_use_case: InteractionUseCase = Depends(get_interaction_use_case),
) -> DashboardStatsSchema:
    """Get aggregated dashboard statistics.

    Returns:
        Dashboard statistics including interaction counts, KB count, and document count.
    """
    kbs = await kb_use_case.list_all()
    interactions = await interaction_use_case.list_all()

    answered = sum(1 for i in interactions if i.status.value == "answered")
    unknown = sum(1 for i in interactions if i.status.value == "unknown")

    doc_count = 0
    for kb in kbs:
        docs = await doc_use_case.list_documents(kb.id)
        doc_count += len(docs)

    return DashboardStatsSchema(
        total_interactions=len(interactions),
        answered_count=answered,
        unknown_count=unknown,
        knowledge_base_count=len(kbs),
        document_count=doc_count,
    )
