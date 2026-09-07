"""
Vector Store Abstraction — ChromaDB implementation.
Swap to Pinecone/Weaviate by implementing VectorStore ABC.
"""
from __future__ import annotations
import uuid
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from app.config import settings
from app.utils.logger import get_logger

logger = get_logger("vector_store")


class SearchResult:
    def __init__(self, id: str, text: str, score: float, metadata: Dict[str, Any]):
        self.id = id
        self.text = text
        self.score = score
        self.metadata = metadata


class VectorStore(ABC):
    @abstractmethod
    def add(self, ids: List[str], embeddings: List[List[float]], texts: List[str], metadatas: List[Dict]) -> None:
        pass

    @abstractmethod
    def search(self, query_embedding: List[float], top_k: int = 10, filter_metadata: Optional[Dict] = None) -> List[SearchResult]:
        pass

    @abstractmethod
    def delete(self, ids: List[str]) -> None:
        pass

    @abstractmethod
    def count(self) -> int:
        pass


class ChromaVectorStore(VectorStore):
    def __init__(self, collection_name: str = "companyiq"):
        try:
            import chromadb
            self.client = chromadb.PersistentClient(path=settings.vector_db_path)
            self.collection = self.client.get_or_create_collection(
                name=collection_name,
                metadata={"hnsw:space": "cosine"},
            )
            logger.info("chroma_initialized", collection=collection_name, count=self.collection.count())
        except Exception as e:
            logger.error("chroma_init_failed", error=str(e))
            raise

    def add(self, ids: List[str], embeddings: List[List[float]], texts: List[str], metadatas: List[Dict]) -> None:
        if not ids:
            return
        # ChromaDB requires string metadata values
        clean_meta = []
        for m in metadatas:
            clean_meta.append({k: str(v) if v is not None else "" for k, v in m.items()})
        try:
            self.collection.upsert(ids=ids, embeddings=embeddings, documents=texts, metadatas=clean_meta)
            logger.info("vectors_added", count=len(ids))
        except Exception as e:
            logger.error("chroma_add_failed", error=str(e))
            raise

    def search(self, query_embedding: List[float], top_k: int = 10, filter_metadata: Optional[Dict] = None) -> List[SearchResult]:
        try:
            kwargs: Dict[str, Any] = {"query_embeddings": [query_embedding], "n_results": min(top_k, max(1, self.collection.count()))}
            if filter_metadata:
                where = {k: {"$eq": str(v)} for k, v in filter_metadata.items() if v}
                if where:
                    kwargs["where"] = where
            results = self.collection.query(**kwargs)
            output = []
            for i, (doc_id, doc, dist, meta) in enumerate(zip(
                results["ids"][0], results["documents"][0],
                results["distances"][0], results["metadatas"][0]
            )):
                score = 1.0 - dist  # cosine distance → similarity
                output.append(SearchResult(id=doc_id, text=doc, score=score, metadata=meta))
            return output
        except Exception as e:
            logger.error("chroma_search_failed", error=str(e))
            return []

    def delete(self, ids: List[str]) -> None:
        try:
            self.collection.delete(ids=ids)
        except Exception as e:
            logger.error("chroma_delete_failed", error=str(e))

    def count(self) -> int:
        return self.collection.count()


class InMemoryVectorStore(VectorStore):
    """Fallback in-memory store — for testing or when ChromaDB unavailable."""
    def __init__(self):
        self._store: Dict[str, Dict] = {}
        logger.warning("using_in_memory_vector_store")

    def add(self, ids, embeddings, texts, metadatas):
        for i, doc_id in enumerate(ids):
            self._store[doc_id] = {"embedding": embeddings[i], "text": texts[i], "metadata": metadatas[i]}

    def search(self, query_embedding, top_k=10, filter_metadata=None):
        import math
        results = []
        for doc_id, item in self._store.items():
            emb = item["embedding"]
            dot = sum(a * b for a, b in zip(query_embedding, emb))
            norm_q = math.sqrt(sum(x**2 for x in query_embedding)) or 1
            norm_e = math.sqrt(sum(x**2 for x in emb)) or 1
            score = dot / (norm_q * norm_e)
            if filter_metadata:
                if not all(str(item["metadata"].get(k)) == str(v) for k, v in filter_metadata.items() if v):
                    continue
            results.append(SearchResult(id=doc_id, text=item["text"], score=score, metadata=item["metadata"]))
        results.sort(key=lambda r: r.score, reverse=True)
        return results[:top_k]

    def delete(self, ids):
        for doc_id in ids:
            self._store.pop(doc_id, None)

    def count(self):
        return len(self._store)


def get_vector_store() -> VectorStore:
    try:
        if settings.vector_db_type == "chroma":
            return ChromaVectorStore()
    except Exception as e:
        logger.warning("chroma_unavailable_fallback", error=str(e))
    return InMemoryVectorStore()
