"""
Document Ingestion & Management Service.
Handles: Upload → Text Extraction → Chunking → Embedding → Vector Indexing in ChromaDB.
"""
from __future__ import annotations
import os
import uuid
import time
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session

from app.config import settings
from app.models.database import (
    Document, DocumentChunk, DocumentStatus, SourceType, Company, User, AuditLog, AuditAction
)
from app.rag.chunker import Chunker
from app.rag.vector_store import get_vector_store
from app.agents.llm_provider import get_llm_provider
from app.research.ingestion.extractor import extract_text_from_file
from app.utils.logger import get_logger

logger = get_logger("document_service")


class DocumentService:
    def __init__(self):
        self.chunker = Chunker()
        self.vector_store = get_vector_store()
        self.llm = get_llm_provider()

    def ingest_file(
        self,
        db: Session,
        file_bytes: bytes,
        filename: str,
        company_id: str,
        user_id: str,
        title: Optional[str] = None,
        source_type: Optional[str] = None,
    ) -> Document:
        """
        Full end-to-end ingestion pipeline for an uploaded file:
        File bytes → Disk save → Text extraction → Document record →
        Chunking → Embedding generation → ChromaDB upsert → DocumentChunk records.
        """
        start = time.time()
        company = db.query(Company).filter(Company.id == company_id).first()
        if not company:
            raise ValueError(f"Company {company_id} not found")

        os.makedirs(settings.upload_dir, exist_ok=True)
        unique_filename = f"{uuid.uuid4().hex[:8]}_{filename}"
        file_path = os.path.join(settings.upload_dir, unique_filename)

        with open(file_path, "wb") as f:
            f.write(file_bytes)

        # Map source_type safely
        st_enum = SourceType.manual
        if source_type:
            try:
                st_enum = SourceType(source_type.lower())
            except ValueError:
                st_enum = SourceType.manual

        # Create Document record with processing status
        doc_id = str(uuid.uuid4())
        doc = Document(
            id=doc_id,
            company_id=company_id,
            filename=filename,
            file_path=file_path,
            source_type=st_enum,
            status=DocumentStatus.processing,
            title=title or filename,
            uploaded_by=user_id,
        )
        db.add(doc)
        db.commit()
        db.refresh(doc)

        try:
            # 1. Extract text
            extracted_text, word_count, page_count = extract_text_from_file(file_path, filename)
            doc.extracted_text = extracted_text
            doc.word_count = word_count
            doc.page_count = page_count

            if not extracted_text.strip():
                doc.status = DocumentStatus.failed
                doc.error_message = "No readable text extracted from document"
                db.commit()
                return doc

            # 2. Chunk text
            base_meta = {
                "document_id": doc_id,
                "company_id": company_id,
                "company_name": company.name,
                "filename": filename,
                "source_type": st_enum.value,
            }
            chunks = self.chunker.chunk_text(extracted_text, metadata=base_meta)

            if not chunks:
                doc.status = DocumentStatus.indexed
                db.commit()
                return doc

            # 3. Generate embeddings
            chunk_texts = [c.text for c in chunks]
            chunk_ids = [f"doc_{doc_id}_chk_{i}" for i in range(len(chunks))]
            embeddings = self.llm.embed(chunk_texts)

            # Ensure embedding list matches chunks
            if not embeddings or len(embeddings) != len(chunks):
                # Fallback to demo embeddings
                from app.agents.llm_provider import DemoProvider
                embeddings = DemoProvider().embed(chunk_texts)

            # 4. Upsert into Vector Store (ChromaDB / InMemory)
            metadatas = []
            for i, c in enumerate(chunks):
                m = dict(c.metadata)
                m["chunk_id"] = chunk_ids[i]
                m["token_count"] = c.token_count
                metadatas.append(m)

            self.vector_store.add(
                ids=chunk_ids,
                embeddings=embeddings,
                texts=chunk_texts,
                metadatas=metadatas,
            )

            # 5. Persist DocumentChunk records in DB
            for i, c in enumerate(chunks):
                db_chunk = DocumentChunk(
                    id=str(uuid.uuid4()),
                    document_id=doc_id,
                    company_id=company_id,
                    chunk_index=i,
                    chunk_text=c.text,
                    token_count=c.token_count,
                    vector_id=chunk_ids[i],
                    meta_data=metadatas[i],
                )
                db.add(db_chunk)

            # 6. Mark Document as ready/indexed
            doc.status = DocumentStatus.ready
            doc.error_message = None
            db.commit()
            db.refresh(doc)

            # Audit log
            log = AuditLog(
                id=str(uuid.uuid4()),
                user_id=user_id,
                action=AuditAction.create,
                resource_type="document",
                resource_id=doc_id,
                success=True,
            )
            db.add(log)
            db.commit()

            latency_ms = round((time.time() - start) * 1000, 1)
            logger.info(
                "document_ingested_successfully",
                doc_id=doc_id,
                filename=filename,
                company=company.name,
                chunks=len(chunks),
                latency_ms=latency_ms,
            )
            return doc

        except Exception as e:
            logger.error("document_ingestion_failed", doc_id=doc_id, error=str(e))
            doc.status = DocumentStatus.failed
            doc.error_message = str(e)
            db.commit()
            db.refresh(doc)
            raise

    def ingest_raw_text(
        self,
        db: Session,
        text: str,
        title: str,
        company_id: str,
        user_id: str,
        source_type: Optional[str] = "company_website",
    ) -> Document:
        """Ingest raw plain text directly (e.g. from web scrapes or user input)."""
        filename = f"{title.replace(' ', '_').lower()[:30]}.txt"
        return self.ingest_file(
            db=db,
            file_bytes=text.encode("utf-8"),
            filename=filename,
            company_id=company_id,
            user_id=user_id,
            title=title,
            source_type=source_type,
        )

    def list_documents(
        self,
        db: Session,
        company_id: Optional[str] = None,
        limit: int = 50,
    ) -> List[Document]:
        """List documents with chunk counts."""
        q = db.query(Document)
        if company_id:
            q = q.filter(Document.company_id == company_id)
        return q.order_by(Document.created_at.desc()).limit(limit).all()

    def get_document_chunks(
        self,
        db: Session,
        document_id: str,
    ) -> List[DocumentChunk]:
        """Retrieve all stored chunks for a specific document."""
        return db.query(DocumentChunk).filter(
            DocumentChunk.document_id == document_id
        ).order_by(DocumentChunk.chunk_index.asc()).all()

    def delete_document(
        self,
        db: Session,
        document_id: str,
        user_id: str,
    ) -> bool:
        """Delete document from DB, remove vectors from ChromaDB, remove file."""
        doc = db.query(Document).filter(Document.id == document_id).first()
        if not doc:
            return False

        chunks = db.query(DocumentChunk).filter(DocumentChunk.document_id == document_id).all()
        vector_ids = [c.vector_id for c in chunks if c.vector_id]

        if vector_ids:
            try:
                self.vector_store.delete(vector_ids)
            except Exception as e:
                logger.warning("chroma_delete_failed_on_doc_removal", error=str(e))

        if doc.file_path and os.path.exists(doc.file_path):
            try:
                os.remove(doc.file_path)
            except Exception:
                pass

        db.delete(doc)
        db.commit()

        log = AuditLog(
            id=str(uuid.uuid4()),
            user_id=user_id,
            action=AuditAction.delete,
            resource_type="document",
            resource_id=document_id,
            success=True,
        )
        db.add(log)
        db.commit()
        return True


_doc_service = None

def get_document_service() -> DocumentService:
    global _doc_service
    if _doc_service is None:
        _doc_service = DocumentService()
    return _doc_service
