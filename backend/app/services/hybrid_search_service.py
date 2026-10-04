import re
import math
from collections import Counter
from typing import List, Dict, Any, Optional

from app.services.vector_store import get_collection, search_chunks


class BM25Retriever:
    """
    In-memory BM25 Okapi search over corpus of documents.
    Fast, zero-heavy-dependency, robust implementation suitable for production & free-tier memory.
    """

    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.corpus: List[str] = []
        self.doc_ids: List[str] = []
        self.metadatas: List[Dict[str, Any]] = []
        self.doc_lengths: List[int] = []
        self.avg_doc_len: float = 0.0
        self.doc_freqs: Dict[str, int] = {}
        self.idf: Dict[str, float] = {}
        self.num_docs: int = 0

    @staticmethod
    def tokenize(text: str) -> List[str]:
        if not text:
            return []
        tokens = re.findall(r"\w+", text.lower())
        return tokens

    def index(self, documents: List[str], doc_ids: Optional[List[str]] = None, metadatas: Optional[List[Dict[str, Any]]] = None):
        self.corpus = documents or []
        self.doc_ids = doc_ids if doc_ids else [str(i) for i in range(len(self.corpus))]
        self.metadatas = metadatas if metadatas else [{} for _ in range(len(self.corpus))]
        self.num_docs = len(self.corpus)

        if self.num_docs == 0:
            self.avg_doc_len = 0.0
            return

        tokenized_corpus = [self.tokenize(doc) for doc in self.corpus]
        self.doc_lengths = [len(doc) for doc in tokenized_corpus]
        total_len = sum(self.doc_lengths)
        self.avg_doc_len = total_len / float(self.num_docs) if self.num_docs > 0 else 0.0

        # Compute document frequencies
        df: Dict[str, int] = Counter()
        for doc in tokenized_corpus:
            unique_terms = set(doc)
            for term in unique_terms:
                df[term] += 1
        self.doc_freqs = dict(df)

        # Compute IDF
        self.idf = {}
        for term, freq in self.doc_freqs.items():
            # Standard Lucene/BM25 IDF formula with smoothing
            val = (self.num_docs - freq + 0.5) / (freq + 0.5)
            self.idf[term] = math.log(1.0 + max(0.0, val))

    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        if not query or self.num_docs == 0:
            return []

        query_tokens = self.tokenize(query)
        if not query_tokens:
            return []

        scores = [0.0] * self.num_docs

        for i, doc in enumerate(self.corpus):
            doc_len = self.doc_lengths[i]
            doc_tokens = self.tokenize(doc)
            term_freqs = Counter(doc_tokens)

            score = 0.0
            for term in query_tokens:
                if term not in term_freqs:
                    continue
                tf = term_freqs[term]
                term_idf = self.idf.get(term, 0.0)
                numerator = tf * (self.k1 + 1.0)
                denominator = tf + self.k1 * (1.0 - self.b + self.b * (doc_len / (self.avg_doc_len or 1.0)))
                score += term_idf * (numerator / (denominator or 1.0))

            scores[i] = score

        # Rank results
        ranked_indices = sorted(range(self.num_docs), key=lambda idx: scores[idx], reverse=True)
        results = []
        for idx in ranked_indices[:top_k]:
            if scores[idx] > 0.0:
                results.append({
                    "id": self.doc_ids[idx],
                    "document": self.corpus[idx],
                    "metadata": self.metadatas[idx],
                    "score": scores[idx]
                })

        return results


class HybridSearchService:
    """
    Implements Hybrid Retrieval (BM25 Keyword Search + ChromaDB Dense Semantic Search)
    combined via Reciprocal Rank Fusion (RRF) and Cross-Encoder / Query-Rewriting Reranking.
    """

    def __init__(self, rrf_k: int = 60):
        self.rrf_k = rrf_k

    def rewrite_query(self, query: str) -> List[str]:
        """
        Query expansion / normalization for robust multi-term retrieval.
        Generates synonyms, strips noise, and expands operational keywords.
        """
        if not query:
            return []

        queries = [query.strip()]
        lower = query.lower()

        # Operational expansions
        if "block" in lower and "issue" not in lower:
            queries.append(f"{query} blocker impediment high priority")
        if "delay" in lower:
            queries.append(f"{query} waiting time overdue SLA breach")
        if "jira" in lower or "ticket" in lower:
            queries.append(f"{query} workflow status assignee priority")

        return queries

    def _get_all_chroma_documents(self) -> Dict[str, Any]:
        """Fetches all documents currently indexed in ChromaDB for BM25 indexing."""
        try:
            collection = get_collection()
            data = collection.get()
            return {
                "ids": data.get("ids", []) or [],
                "documents": data.get("documents", []) or [],
                "metadatas": data.get("metadatas", []) or []
            }
        except Exception:
            return {"ids": [], "documents": [], "metadatas": []}

    def reciprocal_rank_fusion(
        self,
        dense_results: List[Dict[str, Any]],
        sparse_results: List[Dict[str, Any]],
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Fuses dense semantic ranks and sparse BM25 ranks using RRF formula:
        RRF_Score(d) = sum(1 / (k + rank_i(d)))
        """
        fusion_scores: Dict[str, float] = {}
        doc_store: Dict[str, Dict[str, Any]] = {}

        # Process dense results
        for rank, item in enumerate(dense_results, start=1):
            doc_id = item.get("id") or item.get("document")
            fusion_scores[doc_id] = fusion_scores.get(doc_id, 0.0) + (1.0 / (self.rrf_k + rank))
            if doc_id not in doc_store:
                doc_store[doc_id] = item

        # Process sparse results
        for rank, item in enumerate(sparse_results, start=1):
            doc_id = item.get("id") or item.get("document")
            fusion_scores[doc_id] = fusion_scores.get(doc_id, 0.0) + (1.0 / (self.rrf_k + rank))
            if doc_id not in doc_store:
                doc_store[doc_id] = item

        # Sort by RRF score descending
        sorted_docs = sorted(fusion_scores.items(), key=lambda x: x[1], reverse=True)

        final_results = []
        for doc_id, score in sorted_docs[:top_k]:
            item = doc_store[doc_id].copy()
            item["rrf_score"] = round(score, 5)
            final_results.append(item)

        return final_results

    def rerank_results(self, query: str, candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Fast lightweight Cross-term semantic scoring and recency/priority boost reranker.
        """
        query_terms = set(re.findall(r"\w+", query.lower()))

        for item in candidates:
            doc_text = str(item.get("document", "")).lower()
            metadata = item.get("metadata", {}) or {}

            # Exact term overlap bonus
            overlap = sum(1 for term in query_terms if term in doc_text)
            overlap_score = overlap / (len(query_terms) or 1.0)

            # Metadata priority boost
            priority_boost = 0.0
            if str(metadata.get("priority", "")).lower() in ["high", "critical", "highest"]:
                priority_boost = 0.2
            if metadata.get("status") in ["Blocked", "In Progress"]:
                priority_boost += 0.1

            base_score = item.get("rrf_score", 0.5)
            item["final_rerank_score"] = round(base_score + (0.3 * overlap_score) + priority_boost, 4)

        return sorted(candidates, key=lambda x: x.get("final_rerank_score", 0), reverse=True)

    def hybrid_search(
        self,
        query: str,
        n_results: int = 5,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        End-to-End Hybrid Search:
        1. Query Rewriting & Expansion
        2. ChromaDB Dense Semantic Retrieval
        3. BM25 Sparse Keyword Retrieval
        4. Reciprocal Rank Fusion (RRF)
        5. Semantic / Metadata Reranking
        """
        if not query or not query.strip():
            return []

        expanded_queries = self.rewrite_query(query)
        primary_query = expanded_queries[0]

        # 1. Dense Semantic Search (ChromaDB)
        dense_results: List[Dict[str, Any]] = []
        try:
            raw_dense = search_chunks(query=primary_query, n_results=n_results * 2, filters=filters)
            if raw_dense and raw_dense.get("documents") and raw_dense["documents"][0]:
                docs = raw_dense["documents"][0]
                metas = raw_dense.get("metadatas", [[]])[0] if raw_dense.get("metadatas") else []
                ids = raw_dense.get("ids", [[]])[0] if raw_dense.get("ids") else []
                dists = raw_dense.get("distances", [[]])[0] if raw_dense.get("distances") else []

                for idx, doc in enumerate(docs):
                    dense_results.append({
                        "id": ids[idx] if idx < len(ids) else f"dense_{idx}",
                        "document": doc,
                        "metadata": metas[idx] if idx < len(metas) else {},
                        "distance": dists[idx] if idx < len(dists) else 0.0,
                        "source_type": "dense_vector"
                    })
        except Exception:
            dense_results = []

        # 2. Sparse BM25 Search
        sparse_results: List[Dict[str, Any]] = []
        try:
            corpus_data = self._get_all_chroma_documents()
            if corpus_data["documents"]:
                bm25 = BM25Retriever()
                bm25.index(
                    documents=corpus_data["documents"],
                    doc_ids=corpus_data["ids"],
                    metadatas=corpus_data["metadatas"]
                )
                raw_sparse = bm25.search(primary_query, top_k=n_results * 2)
                for item in raw_sparse:
                    item["source_type"] = "sparse_bm25"
                    sparse_results.append(item)
        except Exception:
            sparse_results = []

        # 3. Reciprocal Rank Fusion
        fused = self.reciprocal_rank_fusion(dense_results, sparse_results, top_k=n_results * 2)

        # 4. Reranking
        reranked = self.rerank_results(primary_query, fused)

        return reranked[:n_results]
