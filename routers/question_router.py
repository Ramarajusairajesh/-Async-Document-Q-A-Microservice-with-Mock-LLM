# routers/question_router.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from database import (
    get_db_session,
)
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
    logger.info(
        f"Question for document ID {document_id}: '{question_data.question_text}'"
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

    question = await services.create_question(db, document_id, question_data)
    asyncio.create_task(
        services.simulate_llm_answer(question.id, question.question_text)
    )

    return question


@router.get(
    "/{question_id}",
    response_model=QuestionStatusResponse,
    summary="Retrieve status and answer of a question",
)
async def get_question_status(
    question_id: int, db: AsyncSession = Depends(get_db_session)
):
    logger.info(f"Request for status of question ID: {question_id}")
    question = await services.get_question(db, question_id)
    if not question:
        logger.warning(f"Question with ID {question_id} not found.")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Question with ID {question_id} not found.",
        )
    return QuestionStatusResponse(status=question.status, answer=question.answer)
