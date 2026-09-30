"""
Document Text Extractor — extracts plain text and metadata from PDF, DOCX, TXT, MD, CSV, JSON.
"""
from __future__ import annotations
import os
from typing import Dict, Any, Tuple
from app.utils.logger import get_logger

logger = get_logger("extractor")


def extract_text_from_file(file_path: str, filename: str) -> Tuple[str, int, int]:
    """
    Extracts text, word count, and estimated page count from a file.
    Returns: (extracted_text, word_count, page_count)
    """
    ext = os.path.splitext(filename)[1].lower()
    text = ""
    page_count = 1

    try:
        if ext == ".pdf":
            text, page_count = _extract_from_pdf(file_path)
        elif ext in (".docx", ".doc"):
            text = _extract_from_docx(file_path)
            page_count = max(1, len(text.split()) // 400)
        elif ext in (".txt", ".md", ".json", ".csv", ".log"):
            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                text = f.read()
            page_count = max(1, len(text.split()) // 400)
        else:
            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                text = f.read()
            page_count = 1

    except Exception as e:
        logger.error("text_extraction_failed", filename=filename, error=str(e))
        raise RuntimeError(f"Failed to extract text from {filename}: {str(e)}")

    clean_text = _clean_text(text)
    words = clean_text.split()
    word_count = len(words)

    return clean_text, word_count, max(1, page_count)


def _extract_from_pdf(file_path: str) -> Tuple[str, int]:
    """Extract text from PDF using PyPDF2 or pdfplumber."""
    pages_text = []
    page_count = 0

    # Try PyPDF2
    try:
        import PyPDF2
        with open(file_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            page_count = len(reader.pages)
            for page in reader.pages:
                t = page.extract_text() or ""
                if t.strip():
                    pages_text.append(t)
        if pages_text:
            return "\n\n".join(pages_text), page_count
    except Exception as e:
        logger.warning("pypdf2_failed_trying_pdfplumber", error=str(e))

    # Fallback to pdfplumber
    try:
        import pdfplumber
        with pdfplumber.open(file_path) as pdf:
            page_count = len(pdf.pages)
            for page in pdf.pages:
                t = page.extract_text() or ""
                if t.strip():
                    pages_text.append(t)
        return "\n\n".join(pages_text), page_count
    except Exception as e:
        logger.error("pdfplumber_failed", error=str(e))

    if not pages_text:
        # Last resort fallback: binary string scan
        with open(file_path, "rb") as f:
            raw = f.read()
        import re
        text_chunks = re.findall(b"[\x20-\x7e\n]{4,}", raw)
        return b"\n".join(text_chunks).decode("latin-1", errors="replace"), 1

    return "\n\n".join(pages_text), max(1, page_count)


def _extract_from_docx(file_path: str) -> str:
    """Extract text from DOCX."""
    try:
        import docx
        doc = docx.Document(file_path)
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        return "\n\n".join(paragraphs)
    except Exception as e:
        logger.error("docx_extraction_failed", error=str(e))
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            return f.read()


def _clean_text(text: str) -> str:
    """Normalize whitespace and remove non-printable characters."""
    import re
    text = re.sub(r"\r\n", "\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()
