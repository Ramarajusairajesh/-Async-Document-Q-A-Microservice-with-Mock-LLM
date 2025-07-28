from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models import Document, Question, QuestionStatus
from schemas import DocumentCreate, QuestionCreate
import asyncio
import logging
from typing import Optional
from database import get_session_for_background_task  # Import the new session getter

logger = logging.getLogger(__name__)


async def create_document(
    db: AsyncSession,
    title: str,
    content: str,
    filename: Optional[str] = None,
    filepath: Optional[str] = None,
) -> Document:
    new_document = Document(
        title=title, content=content, filename=filename, filepath=filepath
    )
    db.add(new_document)
    await db.commit()
    await db.refresh(new_document)
    logger.info(
        f"Document created: ID {new_document.id}, Title '{new_document.title}', File '{new_document.filename}'"
    )
    return new_document


async def get_document(db: AsyncSession, document_id: int) -> Document | None:
    result = await db.execute(select(Document).where(Document.id == document_id))
    document = result.scalar_one_or_none()
    logger.info(
        f"Document retrieved: ID {document_id} - {'Found' if document else 'Not Found'}"
    )
    return document


async def create_question(
    db: AsyncSession, document_id: int, question_data: QuestionCreate
) -> Question:
    new_question = Question(
        document_id=document_id,
        question_text=question_data.question_text,
        status=QuestionStatus.PENDING,  # Initially set to pending
    )
    db.add(new_question)
    await db.commit()
    await db.refresh(new_question)
    logger.info(f"Question created: ID {new_question.id} for Document ID {document_id}")
    return new_question


async def get_question(db: AsyncSession, question_id: int) -> Question | None:
    result = await db.execute(select(Question).where(Question.id == question_id))
    question = result.scalar_one_or_none()
    logger.info(
        f"Question retrieved: ID {question_id} - {'Found' if question else 'Not Found'}"
    )
    return question


async def update_question_status_and_answer(
    db: AsyncSession,
    question_id: int,
    status: QuestionStatus,
    answer: str | None = None,
) -> Question | None:
    question = await get_question(db, question_id)
    if question:
        question.status = status
        if answer:
            question.answer = answer
        await db.commit()
        await db.refresh(question)
        logger.info(f"Question ID {question_id} updated to status '{status.value}'")
    return question


# --- LLM Simulation ---


async def simulate_llm_answer(question_id: int, question_text: str):
    logger.info(f"Simulating LLM for question ID {question_id}...")
    logger.info(f"[simulate_llm_answer] Entering function.")
    try:
        await asyncio.sleep(5)  # Simulate a 5-second processing delay

        dummy_answer = f"AI response: '{question_text}'"

        async with get_session_for_background_task() as db:
            await update_question_status_and_answer(
                db, question_id, QuestionStatus.ANSWERED, dummy_answer
            )
            updated_question = await get_question(db, question_id)

    except Exception as e:
        logger.error(f"LLM simulation failed for question ID {question_id}: {e}")
        # If an error occurs, update the question status to FAILED
        async with get_session_for_background_task() as db:
            await update_question_status_and_answer(
                db, question_id, QuestionStatus.FAILED, f"Error: {e}"
            )
