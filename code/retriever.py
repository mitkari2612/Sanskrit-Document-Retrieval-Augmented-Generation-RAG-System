"""
retriever.py - Hybrid Retrieval Engine for Sanskrit Document RAG System
========================================================================
Implements a dual-mode retrieval approach:
1. Character n-gram TF-IDF for robust Sanskrit transliteration matching
2. Optional semantic vector search using multilingual sentence-transformers
3. Reciprocal Rank Fusion (RRF) for combining results
"""

import os
import json
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class HybridRetriever:
    """
    Hybrid retriever combining keyword-based TF-IDF and optional semantic
    vector search for Sanskrit document retrieval.
    """

    def __init__(self, data_path=None, use_semantic=False):
        """
        Initialize the hybrid retriever.

        Args:
            data_path (str): Path to the processed JSON corpus.
                             Defaults to ../data/gita_processed.json relative to this script.
            use_semantic (bool): Whether to enable semantic vector search.
        """
        if data_path is None:
            code_dir = os.path.dirname(os.path.abspath(__file__))
            data_path = os.path.join(os.path.dirname(code_dir), "data", "gita_processed.json")

        if not os.path.exists(data_path):
            raise FileNotFoundError(
                f"Processed corpus not found at {data_path}. "
                "Run ingest.py first to download and process the data."
            )

        # Load corpus
        with open(data_path, "r", encoding="utf-8") as f:
            self.corpus = json.load(f)

        print(f"[Retriever] Loaded {len(self.corpus)} verses from corpus.")

        # Build searchable text chunks — combine all textual fields per verse
        self.chunks = []
        for verse in self.corpus:
            chunk_text = " ".join(filter(None, [
                verse.get("text", ""),
                verse.get("transliteration", ""),
                verse.get("word_meanings", ""),
                verse.get("english_translation", ""),
                verse.get("hindi_translation", ""),
                f"chapter {verse.get('chapter_number', '')} verse {verse.get('verse_number', '')}",
            ]))
            self.chunks.append(chunk_text)

        # Build TF-IDF index with character n-grams
        # char_wb analyzer with ngram_range (2,5) handles transliteration variations
        print("[Retriever] Building TF-IDF index (character n-grams)...")
        self.tfidf_vectorizer = TfidfVectorizer(
            analyzer="char_wb",
            ngram_range=(2, 5),
            max_features=50000,
            sublinear_tf=True,
            dtype=np.float32,
        )
        self.tfidf_matrix = self.tfidf_vectorizer.fit_transform(self.chunks)
        print(f"[Retriever] TF-IDF index built: {self.tfidf_matrix.shape}")

        # Optional semantic search
        self.use_semantic = use_semantic
        self.semantic_model = None
        self.semantic_embeddings = None

        if use_semantic:
            self._build_semantic_index()

    def _build_semantic_index(self):
        """Build semantic embeddings using sentence-transformers."""
        try:
            from sentence_transformers import SentenceTransformer

            model_name = "paraphrase-multilingual-MiniLM-L12-v2"
            print(f"[Retriever] Loading semantic model: {model_name}...")
            self.semantic_model = SentenceTransformer(model_name)

            print("[Retriever] Encoding corpus for semantic search...")
            # Use a condensed version of each chunk for semantic embedding
            condensed = []
            for verse in self.corpus:
                condensed.append(" ".join(filter(None, [
                    verse.get("transliteration", ""),
                    verse.get("english_translation", ""),
                ])))
            self.semantic_embeddings = self.semantic_model.encode(
                condensed, show_progress_bar=True, batch_size=32
            )
            print(f"[Retriever] Semantic index built: {self.semantic_embeddings.shape}")

        except ImportError:
            print("[Retriever] WARNING: sentence-transformers not installed. "
                  "Falling back to TF-IDF only.")
            self.use_semantic = False

    def _tfidf_retrieve(self, query, top_k=5):
        """
        Retrieve top_k results using TF-IDF character n-gram similarity.

        Args:
            query (str): Search query.
            top_k (int): Number of results to return.

        Returns:
            list of tuples: (index, score) pairs sorted by score descending.
        """
        query_vec = self.tfidf_vectorizer.transform([query])
        scores = cosine_similarity(query_vec, self.tfidf_matrix).flatten()
        top_indices = np.argsort(scores)[::-1][:top_k]
        return [(int(idx), float(scores[idx])) for idx in top_indices if scores[idx] > 0]

    def _semantic_retrieve(self, query, top_k=5):
        """
        Retrieve top_k results using semantic vector similarity.

        Args:
            query (str): Search query.
            top_k (int): Number of results to return.

        Returns:
            list of tuples: (index, score) pairs sorted by score descending.
        """
        if self.semantic_model is None or self.semantic_embeddings is None:
            return []

        query_emb = self.semantic_model.encode([query])
        scores = cosine_similarity(query_emb, self.semantic_embeddings).flatten()
        top_indices = np.argsort(scores)[::-1][:top_k]
        return [(int(idx), float(scores[idx])) for idx in top_indices if scores[idx] > 0]

    def _rrf_fuse(self, tfidf_results, semantic_results, top_k=5, k=60):
        """
        Combine results from multiple retrievers using Reciprocal Rank Fusion.

        RRF Score = sum(1 / (k + rank_i)) for each retriever i.

        Args:
            tfidf_results: List of (index, score) from TF-IDF retriever.
            semantic_results: List of (index, score) from semantic retriever.
            top_k (int): Number of final results.
            k (int): RRF constant (default 60).

        Returns:
            list of tuples: (index, fused_score) pairs.
        """
        scores = {}

        for rank, (idx, _) in enumerate(tfidf_results):
            scores[idx] = scores.get(idx, 0) + 1.0 / (k + rank + 1)

        for rank, (idx, _) in enumerate(semantic_results):
            scores[idx] = scores.get(idx, 0) + 1.0 / (k + rank + 1)

        sorted_results = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return sorted_results[:top_k]

    def retrieve(self, query, top_k=5):
        """
        Retrieve the most relevant verses for a given query.

        Uses hybrid fusion if semantic search is enabled, otherwise TF-IDF only.

        Args:
            query (str): User query in Sanskrit, transliterated, or English.
            top_k (int): Number of results to return.

        Returns:
            list of dict: Top matching verse dictionaries from the corpus.
        """
        # TF-IDF retrieval
        tfidf_results = self._tfidf_retrieve(query, top_k=top_k * 2)

        if self.use_semantic and self.semantic_model is not None:
            # Semantic retrieval
            semantic_results = self._semantic_retrieve(query, top_k=top_k * 2)
            # Fuse results
            fused = self._rrf_fuse(tfidf_results, semantic_results, top_k=top_k)
            indices = [idx for idx, _ in fused]
        else:
            indices = [idx for idx, _ in tfidf_results[:top_k]]

        # Return the corresponding verse dictionaries
        results = []
        for idx in indices:
            if 0 <= idx < len(self.corpus):
                results.append(self.corpus[idx])
        return results


if __name__ == "__main__":
    print("=" * 60)
    print("Sanskrit Document RAG - Retriever Test")
    print("=" * 60)

    retriever = HybridRetriever(use_semantic=False)

    test_queries = [
        "karma yoga duty",
        "dharmaksetre kuruksetre",
        "meditation and yoga",
        "soul is eternal",
    ]

    for query in test_queries:
        print(f"\nQuery: '{query}'")
        print("-" * 40)
        results = retriever.retrieve(query, top_k=3)
        for i, verse in enumerate(results):
            ch = verse.get("chapter_number", "?")
            vn = verse.get("verse_number", "?")
            trans = verse.get("transliteration", "")[:80]
            eng = verse.get("english_translation", "")[:100]
            print(f"  [{i+1}] Ch.{ch} V.{vn}: {trans}...")
            if eng:
                print(f"       {eng}...")
        print()
