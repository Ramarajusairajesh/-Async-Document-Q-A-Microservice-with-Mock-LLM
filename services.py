# services.py
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
)  # Added async_sessionmaker import
from sqlalchemy.future import select
from models import Document, Question, QuestionStatus
from schemas import DocumentCreate, QuestionCreate
import asyncio
import logging

logger = logging.getLogger(__name__)

# --- Document Services ---


async def create_document(db: AsyncSession, doc_data: DocumentCreate) -> Document:
    """
    Creates a new document in the database.

    Args:
        db (AsyncSession): The database session.
        doc_data (DocumentCreate): Pydantic schema containing document title and content.

    Returns:
        Document: The newly created Document ORM object.
    """
    new_document = Document(title=doc_data.title, content=doc_data.content)
    db.add(new_document)
    await db.commit()
    await db.refresh(new_document)
    logger.info(f"Document created: ID {new_document.id}, Title '{new_document.title}'")
    return new_document


async def get_document(db: AsyncSession, document_id: int) -> Document | None:
    """
    Retrieves a document by its ID from the database.

    Args:
        db (AsyncSession): The database session.
        document_id (int): The ID of the document to retrieve.

    Returns:
        Document | None: The Document ORM object if found, otherwise None.
    """
    result = await db.execute(select(Document).where(Document.id == document_id))
    document = result.scalar_one_or_none()
    logger.info(
        f"Document retrieved: ID {document_id} - {'Found' if document else 'Not Found'}"
    )
    return document


# --- Question Services ---


async def create_question(
    db: AsyncSession, document_id: int, question_data: QuestionCreate
) -> Question:
    """
    Creates a new question for a given document in the database.

    Args:
        db (AsyncSession): The database session.
        document_id (int): The ID of the document the question relates to.
        question_data (QuestionCreate): Pydantic schema containing the question text.

    Returns:
        Question: The newly created Question ORM object.
    """
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
    """
    Retrieves a question by its ID from the database.

    Args:
        db (AsyncSession): The database session.
        question_id (int): The ID of the question to retrieve.

    Returns:
        Question | None: The Question ORM object if found, otherwise None.
    """
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
    """
    Updates the status and optionally the answer of a question in the database.

    Args:
        db (AsyncSession): The database session.
        question_id (int): The ID of the question to update.
        status (QuestionStatus): The new status for the question.
        answer (str | None): The answer text, if the status is ANSWERED.

    Returns:
        Question | None: The updated Question ORM object if found, otherwise None.
    """
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


async def simulate_llm_answer(
    question_id: int, question_text: str, db_session_factory: async_sessionmaker
):
    """
    Simulates an LLM generating an answer in the background.
    Updates the question's status and answer in the database.

    Args:
        question_id (int): The ID of the question to process.
        question_text (str): The text of the question.
        db_session_factory (async_sessionmaker): A factory to create new async sessions.
    """
    logger.info(f"Simulating LLM for question ID {question_id}...")
    try:
        # Simulate LLM processing time
        await asyncio.sleep(5)  # Simulate a 5-second processing delay

        # Generate a dummy answer
        dummy_answer = f"This is a generated answer to your question: '{question_text}'"

        # Update the question in the database
        async with db_session_factory() as db:
            await update_question_status_and_answer(
                db, question_id, QuestionStatus.ANSWERED, dummy_answer
            )
            logger.info(
                f"LLM simulation complete for question ID {question_id}. Answered."
            )

    except Exception as e:
        logger.error(f"LLM simulation failed for question ID {question_id}: {e}")
        # If an error occurs, update the question status to FAILED
        async with db_session_factory() as db:
            await update_question_status_and_answer(
                db, question_id, QuestionStatus.FAILED, f"Error: {e}"
            )
