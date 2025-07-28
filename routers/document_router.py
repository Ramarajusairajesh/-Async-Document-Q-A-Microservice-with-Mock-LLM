# routers/document_router.py
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db_session
from schemas import DocumentResponse
import services
import logging
import os
import aiofiles  # For asynchronous file operations

logger = logging.getLogger(__name__)

router = APIRouter()

# Define a directory for uploaded files. This should be a path accessible by the container.
# In docker-compose.yml, we mount the current directory to /app, so 'uploaded_files'
# will be created relative to where your docker-compose.yml is.
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
    """
    Uploads a new document, including a file, its title, and text content for LLM Q&A.
    The file is saved to a local directory, and metadata is stored in the database.
    """
    logger.info(
        f"Received request to upload document: '{title}' with file '{file.filename}'"
    )

    # Ensure the upload directory exists
    if not os.path.exists(UPLOAD_DIRECTORY):
        os.makedirs(UPLOAD_DIRECTORY)
        logger.info(f"Created upload directory: {UPLOAD_DIRECTORY}")

    # Define the path where the file will be saved
    file_location = os.path.join(UPLOAD_DIRECTORY, file.filename)

    try:
        # Asynchronously save the uploaded file in chunks
        async with aiofiles.open(file_location, "wb") as out_file:
            while content_chunk := await file.read(1024 * 1024):  # Read in 1MB chunks
                await out_file.write(content_chunk)
        logger.info(f"File '{file.filename}' saved to {file_location}")

        # Create the document entry in the database
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
        await file.close()


@router.get(
    "/{document_id}",
    response_model=DocumentResponse,
    summary="Retrieve a document by ID",
)
async def retrieve_document(
    document_id: int, db: AsyncSession = Depends(get_db_session)
):
    """
    Retrieves a document's details by its unique ID.
    Returns the document's ID, title, content (for LLM), original filename, file path, and timestamps.
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
