from datetime import datetime
from typing import Optional
from sqlalchemy import String, Text, ForeignKey, DateTime, Integer, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from fastapi_users.db import SQLAlchemyBaseUserTableUUID
import enum

from app.database import Base


class TaskStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class User(SQLAlchemyBaseUserTableUUID, Base):
    __tablename__ = "users"

    first_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    last_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Relationships
    pdf_documents: Mapped[list["PDFDocument"]] = relationship(back_populates="user", cascade="all, delete-orphan")


class PDFDocument(Base):
    __tablename__ = "pdf_documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    page_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default=TaskStatus.PENDING.value)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user: Mapped["User"] = relationship(back_populates="pdf_documents")
    summary: Mapped[Optional["Summary"]] = relationship(back_populates="pdf_document", uselist=False, cascade="all, delete-orphan")


class Summary(Base):
    __tablename__ = "summaries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    pdf_document_id: Mapped[int] = mapped_column(ForeignKey("pdf_documents.id"), nullable=False, unique=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    extracted_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    word_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    processing_time: Mapped[Optional[float]] = mapped_column(nullable=True)
    email_sent: Mapped[bool] = mapped_column(default=False)
    email_sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    pdf_document: Mapped["PDFDocument"] = relationship(back_populates="summary")
