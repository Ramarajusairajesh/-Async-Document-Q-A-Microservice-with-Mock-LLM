# models.py
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import enum


# Define an Enum for question status
class QuestionStatus(str, enum.Enum):
    PENDING = "pending"
    ANSWERED = "answered"
    FAILED = "failed"  # Added for robustness


class Document(Base):
    """
    SQLAlchemy model for storing document metadata.
    """

    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    # Content is stored as Text, assuming it's the textual content for LLM processing
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Define a relationship to questions associated with this document
    questions = relationship("Question", back_populates="document")

    def __repr__(self):
        return f"<Document(id={self.id}, title='{self.title}')>"


class Question(Base):
    """
    SQLAlchemy model for storing questions asked about documents.
    """

    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    question_text = Column(Text, nullable=False)
    answer = Column(Text, nullable=True)  # Answer can be null initially
    status = Column(
        Enum(QuestionStatus), default=QuestionStatus.PENDING, nullable=False
    )
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Define a relationship to the document this question belongs to
    document = relationship("Document", back_populates="questions")

    def __repr__(self):
        return f"<Question(id={self.id}, document_id={self.document_id}, status='{self.status}')>"
