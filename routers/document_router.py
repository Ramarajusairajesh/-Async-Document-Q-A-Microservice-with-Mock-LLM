from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db_session
from schemas import DocumentResponse
import services
import logging
import os
import aiofiles

logger = logging.getLogger(__name__)

router = APIRouter()
UPLOAD_DIRECTORY = "uploaded_files"


@router.post(
    "/",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload a new document file with title and content",
)
async def upload_document(
    title: str = Form(
        ..., min_length=1, max_length=255, description="Title of the document."
    ),
    content: str = Form(
        ..., min_length=10, description="Full text content of the document for LLM Q&A."
    ),
    file: UploadFile = File(..., description="The document file to upload."),
    db: AsyncSession = Depends(get_db_session),
):
    logger.info(
        f"Received request to upload document: '{title}' with file '{file.filename}'"
    )

    if not os.path.exists(UPLOAD_DIRECTORY):
        os.makedirs(UPLOAD_DIRECTORY)
        logger.info(f"Created upload directory: {UPLOAD_DIRECTORY}")

    file_location = os.path.join(UPLOAD_DIRECTORY, file.filename)

    try:
        async with aiofiles.open(file_location, "wb") as out_file:
            while content_chunk := await file.read(1024 * 1024):  # Read in 1MB chunks
                await out_file.write(content_chunk)
        logger.info(f"File '{file.filename}' saved to {file_location}")

        document = await services.create_document(
            db,
            title=title,
            content=content,
            filename=file.filename,
            filepath=file_location,
        )
        return document
    except Exception as e:
        logger.error(f"Error uploading or saving document file '{file.filename}': {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"There was an error uploading the document: {e}",
        )
    finally:
        # Ensure the uploaded file's internal buffer is closed
        # Otherwise, the file will be left open and cannot be deleted or sometimes random bugs will arise
        await file.close()


@router.get(
    "/{document_id}",
    response_model=DocumentResponse,
    summary="Retrieve a document by ID",
)
async def retrieve_document(
    document_id: int, db: AsyncSession = Depends(get_db_session)
):
    logger.info(f"Request to retrieve document ID: {document_id}")
    document = await services.get_document(db, document_id)
    if not document:
        logger.warning(f"Document with ID {document_id} not found.")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with ID {document_id} not found.",
        )
    return document
