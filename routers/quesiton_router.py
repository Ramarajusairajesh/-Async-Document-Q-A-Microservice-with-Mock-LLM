# routers/question_router.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from database import (
    get_db_session,
    AsyncSessionLocal,
)  # Import AsyncSessionLocal for background task
from schemas import QuestionCreate, QuestionResponse, QuestionStatusResponse
import services
import asyncio
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/{document_id}/question",
    response_model=QuestionResponse,
    status_code=status.HTTP_202_ACCEPTED,  # Use 202 Accepted for async processing
    summary="Submit a question for a document",
)
async def submit_question(
    document_id: int,
    question_data: QuestionCreate,
    db: AsyncSession = Depends(get_db_session),
):
    """
    Submits a new question related to a specific document.
    The question will be processed asynchronously by a simulated LLM.
    Returns the initial status of the question (pending).
    """
    logger.info(
        f"Received question for document ID {document_id}: '{question_data.question_text}'"
    )

    # First, check if the document exists
    document = await services.get_document(db, document_id)
    if not document:
        logger.warning(
            f"Document with ID {document_id} not found for question submission."
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with ID {document_id} not found.",
        )

    # Create the question entry in the database with PENDING status
    question = await services.create_question(db, document_id, question_data)

    # Start the LLM simulation as a background task
    # Pass AsyncSessionLocal factory to the background task for its own session
    asyncio.create_task(
        services.simulate_llm_answer(
            question.id, question.question_text, AsyncSessionLocal
        )
    )
    logger.info(f"LLM simulation task initiated for question ID {question.id}.")

    return question


@router.get(
    "/{question_id}",
    response_model=QuestionStatusResponse,
    summary="Retrieve status and answer of a question",
)
async def get_question_status(
    question_id: int, db: AsyncSession = Depends(get_db_session)
):
    """
    Retrieves the current status (pending or answered) and the answer
    for a specific question by its unique ID.
    """
    logger.info(f"Received request for status of question ID: {question_id}")
    question = await services.get_question(db, question_id)
    if not question:
        logger.warning(f"Question with ID {question_id} not found.")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Question with ID {question_id} not found.",
        )
    # Return only status and answer as per requirement
    return QuestionStatusResponse(status=question.status, answer=question.answer)
