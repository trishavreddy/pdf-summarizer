from pypdf import PdfReader
from typing import Tuple
import re


def extract_text_from_pdf(file_path: str) -> Tuple[str, int]:
    """
    Extract text content from a PDF file using pypdf.

    Args:
        file_path: Path to the PDF file

    Returns:
        Tuple of (extracted_text, page_count)
    """
    text_content = []
    page_count = 0

    try:
        reader = PdfReader(file_path)
        page_count = len(reader.pages)

        for page_num, page in enumerate(reader.pages, 1):
            page_text = page.extract_text()

            if page_text and page_text.strip():
                text_content.append(f"--- Page {page_num} ---\n{page_text}")

    except Exception as e:
        raise Exception(f"Failed to extract text from PDF: {str(e)}")

    full_text = "\n\n".join(text_content)

    # Clean up text
    full_text = clean_extracted_text(full_text)

    return full_text, page_count


def clean_extracted_text(text: str) -> str:
    """
    Clean up extracted text by removing excessive whitespace and artifacts.

    Args:
        text: Raw extracted text

    Returns:
        Cleaned text
    """
    # Replace multiple newlines with double newlines
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Replace multiple spaces with single space
    text = re.sub(r" {2,}", " ", text)

    # Remove leading/trailing whitespace from each line
    lines = [line.strip() for line in text.split("\n")]
    text = "\n".join(lines)

    # Remove empty lines at start and end
    text = text.strip()

    return text


def get_pdf_metadata(file_path: str) -> dict:
    """
    Get metadata from a PDF file.

    Args:
        file_path: Path to the PDF file

    Returns:
        Dictionary containing PDF metadata
    """
    try:
        reader = PdfReader(file_path)
        metadata = reader.metadata
        page_count = len(reader.pages)

        return {
            "title": metadata.title if metadata else "",
            "author": metadata.author if metadata else "",
            "subject": metadata.subject if metadata else "",
            "creator": metadata.creator if metadata else "",
            "producer": metadata.producer if metadata else "",
            "page_count": page_count,
        }

    except Exception as e:
        raise Exception(f"Failed to get PDF metadata: {str(e)}")
