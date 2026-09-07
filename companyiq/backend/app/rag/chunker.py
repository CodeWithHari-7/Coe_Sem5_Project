"""
RAG Chunker — splits documents into overlapping chunks with metadata.
"""
from typing import List, Dict, Any
from app.config import settings


class TextChunk:
    def __init__(self, text: str, index: int, metadata: Dict[str, Any]):
        self.text = text
        self.index = index
        self.metadata = metadata
        self.token_count = len(text.split())  # approximate


class Chunker:
    def __init__(self, chunk_size: int = None, overlap: int = None):
        self.chunk_size = chunk_size or settings.chunk_size
        self.overlap = overlap or settings.chunk_overlap

    def chunk_text(self, text: str, metadata: Dict[str, Any] = None) -> List[TextChunk]:
        """Split text into overlapping word-based chunks."""
        if not text or not text.strip():
            return []

        words = text.split()
        chunks = []
        start = 0
        idx = 0

        while start < len(words):
            end = min(start + self.chunk_size, len(words))
            chunk_words = words[start:end]
            chunk_text = " ".join(chunk_words)

            chunk_meta = {**(metadata or {}), "chunk_index": idx}
            chunks.append(TextChunk(text=chunk_text, index=idx, metadata=chunk_meta))

            idx += 1
            if end == len(words):
                break
            start = end - self.overlap

        return chunks

    def chunk_documents(self, documents: List[Dict[str, Any]]) -> List[TextChunk]:
        """Chunk a list of {text, metadata} dicts."""
        all_chunks = []
        for doc in documents:
            text = doc.get("text", "")
            meta = {k: v for k, v in doc.items() if k != "text"}
            all_chunks.extend(self.chunk_text(text, meta))
        return all_chunks
