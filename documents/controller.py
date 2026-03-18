import logging

from fastapi import APIRouter, Depends, HTTPException

from auth.scopes import require_scope
from documents.dao import DocumentDAO, IDocumentDAO
from documents.service import DocumentService
from enums import Scope
from exceptions import RetrievalError

logger = logging.getLogger(__name__)

router = APIRouter(tags=["documents"])


def get_document_dao() -> IDocumentDAO:
    return DocumentDAO()


def get_document_service(
    document_dao: IDocumentDAO = Depends(get_document_dao),
) -> DocumentService:
    return DocumentService(document_dao=document_dao)


@router.get("/api/documents")
async def get_documents(
    user=Depends(require_scope(Scope.APP)),
    service: DocumentService = Depends(get_document_service),
):
    """Return all knowledge-base documents grouped by category."""
    try:
        grouped = service.list_documents_by_categories()
    except RetrievalError:
        raise HTTPException(
            status_code=503,
            detail="Couldn't reach the knowledge base. Please try again in a moment.",
        )

    return {"success": True, "data": {"documents": grouped}, "error": None}
