"""Document API routes."""

from __future__ import annotations

import hashlib

from fastapi import APIRouter, Depends, File, UploadFile

from app.application.use_cases.document_use_case import DocumentUseCase
from app.dependencies import get_document_use_case
from app.interfaces.api.schemas.document import DocumentSchema

router = APIRouter(prefix="/api/v1", tags=["documents"])


@router.post(
    "/knowledge-bases/{kb_id}/documents",
    response_model=DocumentSchema,
    status_code=201,
)
async def upload_document(
    kb_id: str,
    file: UploadFile = File(...),
    use_case: DocumentUseCase = Depends(get_document_use_case),
) -> DocumentSchema:
    """Upload a document to a knowledge base.

    Args:
        kb_id: Knowledge base ID.
        file: Uploaded file.
        use_case: Injected document use case.

    Returns:
        Created document entity.
    """
    content = await file.read()
    content_hash = hashlib.sha256(content).hexdigest()
    doc = await use_case.upload(kb_id, file.filename or "unnamed", content_hash)
    return DocumentSchema(
        id=doc.id,
        kb_id=doc.kb_id,
        filename=doc.filename,
        status=doc.status.value,
        chunks_count=doc.chunks_count,
        uploaded_at=doc.uploaded_at,
    )


@router.get("/knowledge-bases/{kb_id}/documents", response_model=list[DocumentSchema])
async def list_documents(
    kb_id: str, use_case: DocumentUseCase = Depends(get_document_use_case)
) -> list[DocumentSchema]:
    """List all documents in a knowledge base.

    Args:
        kb_id: Knowledge base ID.
        use_case: Injected document use case.

    Returns:
        List of documents.
    """
    docs = await use_case.list_documents(kb_id)
    return [
        DocumentSchema(
            id=d.id,
            kb_id=d.kb_id,
            filename=d.filename,
            status=d.status.value,
            chunks_count=d.chunks_count,
            uploaded_at=d.uploaded_at,
        )
        for d in docs
    ]


@router.delete(
    "/knowledge-bases/{kb_id}/documents/{doc_id}",
    status_code=204,
)
async def delete_document(
    kb_id: str, doc_id: str, use_case: DocumentUseCase = Depends(get_document_use_case)
) -> None:
    """Delete a document and its chunks.

    Args:
        kb_id: Knowledge base ID (for validation).
        doc_id: Document ID to delete.
        use_case: Injected document use case.
    """
    await use_case.delete(kb_id, doc_id)


@router.post("/knowledge-bases/{kb_id}/index", status_code=202)
async def trigger_indexing(kb_id: str) -> dict[str, str]:
    """Trigger indexing for a knowledge base.

    Args:
        kb_id: Knowledge base ID.

    Returns:
        Status message.
    """
    return {"status": "indexing_triggered", "kb_id": kb_id}
