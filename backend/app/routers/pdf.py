import os
import uuid
from typing import List

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.auth import current_active_user
from app.config import get_settings
from app.database import get_async_session
from app.models import PDFDocument, Summary, TaskStatus, User
from app.schemas import PDFDocumentListResponse, PDFDocumentResponse, UploadResponse
from app.tasks.worker import process_pdf_task

router = APIRouter(prefix="/pdf", tags=["pdf"])
settings = get_settings()


@router.post("/upload", response_model=UploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_pdf(
    file: UploadFile = File(...),
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    """Upload a PDF file for summarization."""
    # Validate file type
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are allowed",
        )

    # Validate file size
    content = await file.read()
    if len(content) > settings.max_file_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File size exceeds maximum allowed ({settings.max_file_size // (1024 * 1024)}MB)",
        )

    # Create upload directory if it doesn't exist
    os.makedirs(settings.upload_dir, exist_ok=True)

    # Generate unique filename
    unique_filename = f"{uuid.uuid4()}_{file.filename}"
    file_path = os.path.join(settings.upload_dir, unique_filename)

    # Save file
    with open(file_path, "wb") as f:
        f.write(content)

    # Create database record
    pdf_document = PDFDocument(
        user_id=str(user.id),
        filename=unique_filename,
        original_filename=file.filename,
        file_path=file_path,
        file_size=len(content),
        status=TaskStatus.PENDING.value,
    )
    session.add(pdf_document)
    await session.commit()
    await session.refresh(pdf_document)

    # Trigger Celery task
    task = process_pdf_task.delay(pdf_document.id, str(user.email))

    return UploadResponse(
        document_id=pdf_document.id,
        task_id=task.id,
        message="PDF uploaded successfully. Processing started.",
    )


@router.get("/documents", response_model=List[PDFDocumentListResponse])
async def list_documents(
    skip: int = 0,
    limit: int = 20,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    """List all PDF documents for the current user."""
    result = await session.execute(
        select(PDFDocument)
        .where(PDFDocument.user_id == str(user.id))
        .order_by(PDFDocument.created_at.desc())
        .offset(skip)
        .limit(limit)
        .options(selectinload(PDFDocument.summary))
    )
    documents = result.scalars().all()

    return [
        PDFDocumentListResponse(
            id=doc.id,
            original_filename=doc.original_filename,
            file_size=doc.file_size,
            page_count=doc.page_count,
            status=doc.status,
            created_at=doc.created_at,
            has_summary=doc.summary is not None,
        )
        for doc in documents
    ]


@router.get("/documents/{document_id}", response_model=PDFDocumentResponse)
async def get_document(
    document_id: int,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    """Get a specific PDF document with its summary."""
    result = await session.execute(
        select(PDFDocument)
        .where(PDFDocument.id == document_id, PDFDocument.user_id == str(user.id))
        .options(selectinload(PDFDocument.summary))
    )
    document = result.scalar_one_or_none()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    return document


@router.delete("/documents/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: int,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    """Delete a PDF document and its summary."""
    result = await session.execute(
        select(PDFDocument)
        .where(PDFDocument.id == document_id, PDFDocument.user_id == str(user.id))
    )
    document = result.scalar_one_or_none()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    # Delete file from disk
    if os.path.exists(document.file_path):
        os.remove(document.file_path)

    await session.delete(document)
    await session.commit()
