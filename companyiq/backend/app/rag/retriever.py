"""
RAG Retriever — hybrid retrieval: semantic + BM25 keyword + metadata filtering.
"""
from typing import List, Dict, Any, Optional
from app.rag.vector_store import VectorStore, SearchResult
from app.agents.llm_provider import LLMProvider
from app.config import settings
from app.utils.logger import get_logger

logger = get_logger("retriever")


class RetrievedChunk:
    def __init__(self, text: str, score: float, metadata: Dict[str, Any], source: str = "semantic"):
        self.text = text
        self.score = score
        self.metadata = metadata
        self.source = source  # "semantic" | "keyword" | "hybrid"


class HybridRetriever:
    def __init__(self, vector_store: VectorStore, llm_provider: LLMProvider):
        self.vector_store = vector_store
        self.llm_provider = llm_provider
        self.alpha = settings.hybrid_alpha  # weight for semantic vs keyword

    def retrieve(
        self,
        query: str,
        top_k: int = None,
        filter_metadata: Optional[Dict[str, str]] = None,
    ) -> List[RetrievedChunk]:
        """
        Hybrid retrieval:
        1. Semantic search via embedding
        2. BM25 keyword search (on stored texts)
        3. Merge and re-rank
        """
        top_k = top_k or settings.top_k_chunks

        # 1. Semantic search
        try:
            query_embedding = self.llm_provider.embed([query])[0]
            semantic_results = self.vector_store.search(query_embedding, top_k=top_k * 2, filter_metadata=filter_metadata)
        except Exception as e:
            logger.error("semantic_retrieval_failed", error=str(e))
            semantic_results = []

        # 2. BM25 keyword search (using stored documents)
        bm25_results = self._bm25_search(query, semantic_results, top_k * 2)

        # 3. Hybrid merge with reciprocal rank fusion
        merged = self._reciprocal_rank_fusion(semantic_results, bm25_results, alpha=self.alpha)

        results = merged[:top_k]
        logger.info(
            "retrieval_complete",
            query_sample=query[:50],
            semantic_count=len(semantic_results),
            bm25_count=len(bm25_results),
            merged_count=len(results),
        )
        return results

    def _bm25_search(self, query: str, candidates: List[SearchResult], top_k: int) -> List[RetrievedChunk]:
        """Simple BM25 over the candidate corpus."""
        if not candidates:
            return []
        try:
            from rank_bm25 import BM25Okapi
            corpus = [r.text.lower().split() for r in candidates]
            bm25 = BM25Okapi(corpus)
            scores = bm25.get_scores(query.lower().split())
            ranked = sorted(zip(scores, candidates), key=lambda x: x[0], reverse=True)
            return [
                RetrievedChunk(text=r.text, score=float(s), metadata=r.metadata, source="keyword")
                for s, r in ranked[:top_k]
            ]
        except Exception as e:
            logger.warning("bm25_failed", error=str(e))
            return []

    def _reciprocal_rank_fusion(
        self,
        semantic: List[SearchResult],
        keyword: List[RetrievedChunk],
        alpha: float = 0.7,
        k: int = 60,
    ) -> List[RetrievedChunk]:
        """Merge two ranked lists via RRF."""
        scores: Dict[str, float] = {}
        texts: Dict[str, str] = {}
        metas: Dict[str, Dict] = {}

        for rank, r in enumerate(semantic):
            key = r.id
            scores[key] = scores.get(key, 0) + alpha * (1 / (k + rank + 1))
            texts[key] = r.text
            metas[key] = r.metadata

        for rank, r in enumerate(keyword):
            key = r.text[:100]  # use text prefix as key for keyword results
            scores[key] = scores.get(key, 0) + (1 - alpha) * (1 / (k + rank + 1))
            texts[key] = r.text
            metas[key] = r.metadata

        merged = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return [
            RetrievedChunk(text=texts[k], score=s, metadata=metas[k], source="hybrid")
            for k, s in merged
        ]
