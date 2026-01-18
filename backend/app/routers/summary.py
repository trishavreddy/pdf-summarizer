from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.auth import current_active_user
from app.database import get_async_session
from app.models import PDFDocument, Summary, User
from app.schemas import SummaryDetailResponse, SummaryResponse
from app.services.email import send_summary_email

router = APIRouter(prefix="/summaries", tags=["summaries"])


@router.get("", response_model=List[SummaryDetailResponse])
async def list_summaries(
    skip: int = 0,
    limit: int = 20,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    """List all summaries for the current user."""
    result = await session.execute(
        select(Summary)
        .join(PDFDocument)
        .where(PDFDocument.user_id == str(user.id))
        .order_by(Summary.created_at.desc())
        .offset(skip)
        .limit(limit)
        .options(selectinload(Summary.pdf_document))
    )
    summaries = result.scalars().all()
    return summaries


@router.get("/{summary_id}", response_model=SummaryDetailResponse)
async def get_summary(
    summary_id: int,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    """Get a specific summary."""
    result = await session.execute(
        select(Summary)
        .join(PDFDocument)
        .where(Summary.id == summary_id, PDFDocument.user_id == str(user.id))
        .options(selectinload(Summary.pdf_document))
    )
    summary = result.scalar_one_or_none()

    if not summary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Summary not found",
        )

    return summary


@router.post("/{summary_id}/resend-email", response_model=dict)
async def resend_summary_email(
    summary_id: int,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    """Resend the summary email."""
    result = await session.execute(
        select(Summary)
        .join(PDFDocument)
        .where(Summary.id == summary_id, PDFDocument.user_id == str(user.id))
        .options(selectinload(Summary.pdf_document))
    )
    summary = result.scalar_one_or_none()

    if not summary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Summary not found",
        )

    # Send email
    success = await send_summary_email(
        to_email=str(user.email),
        filename=summary.pdf_document.original_filename,
        summary_content=summary.content,
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send email",
        )

    return {"message": "Email sent successfully"}
