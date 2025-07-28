# routers/document_router.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db_session
from schemas import DocumentCreate, DocumentResponse
import services
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload a new document",
)
async def upload_document(
    doc_data: DocumentCreate, db: AsyncSession = Depends(get_db_session)
):
    """
    Uploads a new document with a title and its textual content.
    The content will be used for simulated LLM answers.
    """
    logger.info(f"Received request to upload document: '{doc_data.title}'")
    document = await services.create_document(db, doc_data)
    return document


@router.get(
    "/{document_id}",
    response_model=DocumentResponse,  # Changed to DocumentResponse to include content
    summary="Retrieve a document by ID",
)
async def retrieve_document(
    document_id: int, db: AsyncSession = Depends(get_db_session)
):
    """
    Retrieves a document's details by its unique ID.
    Returns the document's ID, title, content, and timestamps.
    """
    logger.info(f"Received request to retrieve document ID: {document_id}")
    document = await services.get_document(db, document_id)
    if not document:
        logger.warning(f"Document with ID {document_id} not found.")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with ID {document_id} not found.",
        )
    return document
