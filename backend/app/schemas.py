from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr
from uuid import UUID
from fastapi_users import schemas

from app.models import TaskStatus


# User Schemas (fastapi-users)
class UserRead(schemas.BaseUser[UUID]):
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class UserCreate(schemas.BaseUserCreate):
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class UserUpdate(schemas.BaseUserUpdate):
    first_name: Optional[str] = None
    last_name: Optional[str] = None


# PDF Document Schemas
class PDFDocumentBase(BaseModel):
    filename: str
    original_filename: str


class PDFDocumentCreate(PDFDocumentBase):
    file_path: str
    file_size: int


class PDFDocumentResponse(BaseModel):
    id: int
    filename: str
    original_filename: str
    file_size: int
    page_count: Optional[int]
    status: str
    created_at: datetime
    updated_at: datetime
    summary: Optional["SummaryResponse"] = None

    class Config:
        from_attributes = True


class PDFDocumentListResponse(BaseModel):
    id: int
    original_filename: str
    file_size: int
    page_count: Optional[int]
    status: str
    created_at: datetime
    has_summary: bool

    class Config:
        from_attributes = True


# Summary Schemas
class SummaryBase(BaseModel):
    content: str


class SummaryCreate(SummaryBase):
    pdf_document_id: int
    extracted_text: Optional[str] = None
    word_count: Optional[int] = None
    processing_time: Optional[float] = None


class SummaryResponse(BaseModel):
    id: int
    content: str
    word_count: Optional[int]
    processing_time: Optional[float]
    email_sent: bool
    email_sent_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class SummaryDetailResponse(SummaryResponse):
    pdf_document: PDFDocumentBase

    class Config:
        from_attributes = True


# Task Response
class TaskResponse(BaseModel):
    task_id: str
    status: str
    message: str


# Upload Response
class UploadResponse(BaseModel):
    document_id: int
    task_id: str
    message: str
