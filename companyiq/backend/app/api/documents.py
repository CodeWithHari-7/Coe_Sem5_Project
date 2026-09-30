"""
Documents API — Document Ingestion, Retrieval, Chunk Exploration, and Deletion.
Supports: PDF, DOCX, TXT, MD, CSV, JSON file upload and raw text ingestion.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.api.deps import get_current_user
from app.models.database import User, Document, DocumentChunk
from app.schemas.schemas import (
    DocumentOut, DocumentChunkOut, DocumentTextUploadRequest, SuccessResponse
)
from app.services.document_service import get_document_service
from app.utils.logger import get_logger

router = APIRouter(prefix="/documents", tags=["Documents"])
logger = get_logger("documents_api")


@router.post("/upload", response_model=DocumentOut, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    company_id: str = Form(...),
    title: Optional[str] = Form(None),
    source_type: Optional[str] = Form("manual_upload"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Upload a document (PDF, DOCX, TXT, MD, CSV, JSON).
    Extracts text, splits into chunks, computes vector embeddings,
    stores in ChromaDB, and saves chunks in DB.
    """
    service = get_document_service()
    contents = await file.read()
    if not contents:
        raise HTTPException(400, "Empty file uploaded")

    filename = file.filename or "uploaded_document.txt"
    try:
        doc = service.ingest_file(
            db=db,
            file_bytes=contents,
            filename=filename,
            company_id=company_id,
            user_id=current_user.id,
            title=title or filename,
            source_type=source_type,
        )
        chunk_count = db.query(DocumentChunk).filter(DocumentChunk.document_id == doc.id).count()
        return DocumentOut(
            id=doc.id,
            company_id=doc.company_id,
            filename=doc.filename,
            title=doc.title,
            source_type=doc.source_type.value if hasattr(doc.source_type, "value") else str(doc.source_type),
            status=doc.status.value if hasattr(doc.status, "value") else str(doc.status),
            page_count=doc.page_count,
            word_count=doc.word_count,
            chunks_count=chunk_count,
            error_message=doc.error_message,
            created_at=doc.created_at,
        )
    except Exception as e:
        logger.error("upload_api_failed", error=str(e), filename=filename)
        raise HTTPException(500, f"Document ingestion failed: {str(e)}")


@router.post("/text", response_model=DocumentOut, status_code=status.HTTP_201_CREATED)
def ingest_text(
    req: DocumentTextUploadRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Ingest raw plain text directly (e.g. pasted notes, news, scrape results)."""
    service = get_document_service()
    if not req.text.strip():
        raise HTTPException(400, "Text content cannot be empty")

    try:
        doc = service.ingest_raw_text(
            db=db,
            text=req.text,
            title=req.title,
            company_id=req.company_id,
            user_id=current_user.id,
            source_type=req.source_type or "company_website",
        )
        chunk_count = db.query(DocumentChunk).filter(DocumentChunk.document_id == doc.id).count()
        return DocumentOut(
            id=doc.id,
            company_id=doc.company_id,
            filename=doc.filename,
            title=doc.title,
            source_type=doc.source_type.value if hasattr(doc.source_type, "value") else str(doc.source_type),
            status=doc.status.value if hasattr(doc.status, "value") else str(doc.status),
            page_count=doc.page_count,
            word_count=doc.word_count,
            chunks_count=chunk_count,
            error_message=doc.error_message,
            created_at=doc.created_at,
        )
    except Exception as e:
        logger.error("text_ingest_failed", error=str(e))
        raise HTTPException(500, f"Text ingestion failed: {str(e)}")


@router.get("", response_model=List[DocumentOut])
def list_documents(
    company_id: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List ingested documents with chunk counts."""
    service = get_document_service()
    docs = service.list_documents(db, company_id=company_id, limit=limit)
    out = []
    for d in docs:
        c_count = db.query(DocumentChunk).filter(DocumentChunk.document_id == d.id).count()
        out.append(DocumentOut(
            id=d.id,
            company_id=d.company_id,
            filename=d.filename,
            title=d.title,
            source_type=d.source_type.value if hasattr(d.source_type, "value") else str(d.source_type),
            status=d.status.value if hasattr(d.status, "value") else str(d.status),
            page_count=d.page_count,
            word_count=d.word_count,
            chunks_count=c_count,
            error_message=d.error_message,
            created_at=d.created_at,
        ))
    return out


@router.get("/{document_id}", response_model=DocumentOut)
def get_document(
    document_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get single document details."""
    d = db.query(Document).filter(Document.id == document_id).first()
    if not d:
        raise HTTPException(404, "Document not found")
    c_count = db.query(DocumentChunk).filter(DocumentChunk.document_id == d.id).count()
    return DocumentOut(
        id=d.id,
        company_id=d.company_id,
        filename=d.filename,
        title=d.title,
        source_type=d.source_type.value if hasattr(d.source_type, "value") else str(d.source_type),
        status=d.status.value if hasattr(d.status, "value") else str(d.status),
        page_count=d.page_count,
        word_count=d.word_count,
        chunks_count=c_count,
        error_message=d.error_message,
        created_at=d.created_at,
    )


@router.get("/{document_id}/chunks", response_model=List[DocumentChunkOut])
def get_document_chunks(
    document_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve all chunked segments for a document, including vector IDs."""
    service = get_document_service()
    chunks = service.get_document_chunks(db, document_id)
    return chunks


@router.delete("/{document_id}", response_model=SuccessResponse)
def delete_document(
    document_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete document, its chunks from DB, and vectors from ChromaDB."""
    service = get_document_service()
    success = service.delete_document(db, document_id, current_user.id)
    if not success:
        raise HTTPException(404, "Document not found")
    return SuccessResponse(message="Document and vector chunks deleted successfully")
