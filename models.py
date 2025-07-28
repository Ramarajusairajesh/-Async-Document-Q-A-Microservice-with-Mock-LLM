from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import enum


class QuestionStatus(str, enum.Enum):
    PENDING = "pending"
    ANSWERED = "answered"
    FAILED = "failed"
    # Only for the thought of what if the transfer failed


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    content = Column(Text, nullable=False)
    filename = Column(String, nullable=True)  # Original name of the uploaded file
    filepath = Column(String, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    questions = relationship("Question", back_populates="document")

    def __repr__(self):
        return f"<Document(id={self.id}, title='{self.title}', filename='{self.filename}')>"


class Question(Base):
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
