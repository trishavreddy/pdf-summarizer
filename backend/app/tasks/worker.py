import time
from datetime import datetime
from celery import Celery
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config import get_settings
from app.models import PDFDocument, Summary, TaskStatus
from app.services.pdf_extractor import extract_text_from_pdf
from app.services.summarizer import summarize_text, count_words
from app.services.email import send_summary_email_sync

settings = get_settings()

# Create Celery app
celery_app = Celery(
    "pdf_summarizer",
    broker=settings.redis_url,
    backend=settings.redis_url,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=600,  # 10 minutes max
    worker_prefetch_multiplier=1,
)

# Create sync database session for Celery
engine = create_engine(settings.database_url_sync)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@celery_app.task(bind=True, max_retries=3)
def process_pdf_task(self, document_id: int, user_email: str):
    """
    Celery task to process PDF: extract text, summarize, and send email.

    Args:
        document_id: ID of the PDFDocument to process
        user_email: Email address to send the summary to
    """
    db = SessionLocal()
    start_time = time.time()

    try:
        # Get document from database
        document = db.query(PDFDocument).filter(PDFDocument.id == document_id).first()

        if not document:
            raise Exception(f"Document {document_id} not found")

        # Update status to processing
        document.status = TaskStatus.PROCESSING.value
        db.commit()

        # Step 1: Extract text from PDF
        print(f"Extracting text from PDF: {document.original_filename}")
        extracted_text, page_count = extract_text_from_pdf(document.file_path)

        # Update page count
        document.page_count = page_count
        db.commit()

        if not extracted_text.strip():
            raise Exception("No text could be extracted from the PDF")

        # Step 2: Summarize text using GPT-4
        print(f"Summarizing text ({len(extracted_text)} characters)")
        summary_content = summarize_text(extracted_text)

        # Calculate processing time
        processing_time = time.time() - start_time

        # Step 3: Save summary to database
        summary = Summary(
            pdf_document_id=document_id,
            content=summary_content,
            extracted_text=extracted_text[:50000],  # Store first 50k chars
            word_count=count_words(summary_content),
            processing_time=processing_time,
        )
        db.add(summary)

        # Update document status
        document.status = TaskStatus.COMPLETED.value
        db.commit()

        # Step 4: Send email with summary
        print(f"Sending summary email to {user_email}")
        email_sent = send_summary_email_sync(
            to_email=user_email,
            filename=document.original_filename,
            summary_content=summary_content,
        )

        if email_sent:
            summary.email_sent = True
            summary.email_sent_at = datetime.utcnow()
            db.commit()

        print(f"PDF processing completed for document {document_id}")

        return {
            "status": "completed",
            "document_id": document_id,
            "summary_length": len(summary_content),
            "processing_time": processing_time,
            "email_sent": email_sent,
        }

    except Exception as e:
        print(f"Error processing PDF {document_id}: {str(e)}")

        # Update document status to failed
        document = db.query(PDFDocument).filter(PDFDocument.id == document_id).first()
        if document:
            document.status = TaskStatus.FAILED.value
            db.commit()

        # Retry if attempts remaining
        if self.request.retries < self.max_retries:
            raise self.retry(exc=e, countdown=60 * (self.request.retries + 1))

        return {
            "status": "failed",
            "document_id": document_id,
            "error": str(e),
        }

    finally:
        db.close()
