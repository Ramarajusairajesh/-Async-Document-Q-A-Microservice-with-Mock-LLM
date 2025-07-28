from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from models import QuestionStatus  # Import the QuestionStatus enum


class DocumentBase(BaseModel):
    title: str = Field(
        ..., min_length=1, max_length=255, description="Title of the document."
    )
    # This 'content' field is for the LLM processing, provided by the user.
    # It's distinct from the uploaded file's content.
    content: str = Field(
        ..., min_length=10, description="Full text content of the document for LLM Q&A."
    )


class DocumentCreate(DocumentBase):
    # Inherits title and content from DocumentBase
    # File upload is handled directly in the router using Form/File dependencies
    pass


class DocumentResponse(DocumentBase):
    id: int = Field(..., description="Unique ID of the document.")
    filename: Optional[str] = Field(
        None, description="Original filename of the uploaded document."
    )
    filepath: Optional[str] = Field(
        None, description="Server path where the document file is stored."
    )
    created_at: datetime = Field(
        ..., description="Timestamp when the document was created."
    )
    updated_at: Optional[datetime] = Field(
        None, description="Timestamp when the document was last updated."
    )

    class Config:
        from_attributes = True


class QuestionBase(BaseModel):
    question_text: str = Field(
        ..., min_length=5, description="The question asked about the document."
    )


class QuestionCreate(QuestionBase):
    pass


class QuestionResponse(QuestionBase):
    id: int = Field(..., description="Unique ID of the question.")
    document_id: int = Field(
        ..., description="ID of the document the question is related to."
    )
    answer: Optional[str] = Field(
        None, description="The LLM-generated answer to the question."
    )
    status: QuestionStatus = Field(
        ..., description="Current status of the question (pending, answered, failed)."
    )
    created_at: datetime = Field(
        ..., description="Timestamp when the question was created."
    )
    updated_at: Optional[datetime] = Field(
        None, description="Timestamp when the question was last updated."
    )

    class Config:
        from_attributes = True  # Enable ORM mode for Pydantic v2+


class QuestionStatusResponse(BaseModel):
    status: QuestionStatus = Field(
        ..., description="Current status of the question (pending, answered, failed)."
    )
    answer: Optional[str] = Field(
        None, description="The LLM-generated answer to the question."
    )

    class Config:
        from_attributes = True
