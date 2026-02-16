"""Knowledge base API routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from app.application.use_cases.knowledge_base_use_case import KnowledgeBaseUseCase
from app.dependencies import get_kb_use_case
from app.interfaces.api.schemas.knowledge_base import (
    CreateKnowledgeBaseSchema,
    KnowledgeBaseSchema,
)

router = APIRouter(prefix="/api/v1", tags=["knowledge-bases"])


@router.post("/knowledge-bases", response_model=KnowledgeBaseSchema, status_code=201)
async def create_kb(
    request: CreateKnowledgeBaseSchema,
    use_case: KnowledgeBaseUseCase = Depends(get_kb_use_case),
) -> KnowledgeBaseSchema:
    """Create a new knowledge base.

    Args:
        request: Knowledge base creation request.
        use_case: Injected knowledge base use case.

    Returns:
        Created knowledge base entity.
    """
    kb = await use_case.create(request.name, request.description)
    return KnowledgeBaseSchema(
        id=kb.id, name=kb.name, description=kb.description, created_at=kb.created_at
    )


@router.get("/knowledge-bases", response_model=list[KnowledgeBaseSchema])
async def list_kbs(
    use_case: KnowledgeBaseUseCase = Depends(get_kb_use_case),
) -> list[KnowledgeBaseSchema]:
    """List all knowledge bases.

    Args:
        use_case: Injected knowledge base use case.

    Returns:
        List of all knowledge bases.
    """
    kbs = await use_case.list_all()
    return [
        KnowledgeBaseSchema(
            id=kb.id, name=kb.name, description=kb.description, created_at=kb.created_at
        )
        for kb in kbs
    ]


@router.get("/knowledge-bases/{kb_id}", response_model=KnowledgeBaseSchema)
async def get_kb(
    kb_id: str, use_case: KnowledgeBaseUseCase = Depends(get_kb_use_case)
) -> KnowledgeBaseSchema:
    """Get a knowledge base by ID.

    Args:
        kb_id: Knowledge base ID.
        use_case: Injected knowledge base use case.

    Returns:
        Knowledge base entity.

    Raises:
        HTTPException: If knowledge base is not found.
    """
    kb = await use_case.get(kb_id)
    if not kb:
        raise HTTPException(status_code=404, detail="Knowledge base not found")
    return KnowledgeBaseSchema(
        id=kb.id, name=kb.name, description=kb.description, created_at=kb.created_at
    )


@router.delete("/knowledge-bases/{kb_id}", status_code=204)
async def delete_kb(
    kb_id: str, use_case: KnowledgeBaseUseCase = Depends(get_kb_use_case)
) -> None:
    """Delete a knowledge base.

    Args:
        kb_id: Knowledge base ID to delete.
        use_case: Injected knowledge base use case.
    """
    await use_case.delete(kb_id)
