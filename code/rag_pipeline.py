"""
rag_pipeline.py - Main RAG Pipeline Coordinator
=================================================
Ties together the retriever and generator components into a unified
query-response pipeline with timing and system metrics.
"""

import os
import sys
import time
import json

# Ensure local imports work
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from retriever import HybridRetriever
from generator import Generator


def format_verse_for_display(verse):
    """
    Format a verse dictionary into a readable multi-line string.

    Args:
        verse (dict): A verse dictionary from the corpus.

    Returns:
        str: Nicely formatted verse text.
    """
    ch = verse.get("chapter_number", "?")
    vn = verse.get("verse_number", "?")

    lines = [f"Chapter {ch}, Verse {vn}", ""]

    if verse.get("text"):
        lines.append(f"Sanskrit Text:")
        lines.append(f"  {verse['text']}")
        lines.append("")

    if verse.get("transliteration"):
        lines.append(f"Transliteration:")
        lines.append(f"  {verse['transliteration']}")
        lines.append("")

    if verse.get("word_meanings"):
        lines.append(f"Word Meanings:")
        lines.append(f"  {verse['word_meanings']}")
        lines.append("")

    if verse.get("english_translation"):
        lines.append(f"English Translation:")
        lines.append(f"  {verse['english_translation']}")
        lines.append("")

    return "\n".join(lines)


class SanskritRAGPipeline:
    """
    Main RAG pipeline that coordinates retrieval and generation
    for Sanskrit document queries.
    """

    def __init__(
        self,
        data_path=None,
        use_semantic=False,
        generator_backend="ollama",
        generator_model=None,
    ):
        """
        Initialize the RAG pipeline.

        Args:
            data_path (str): Path to gita_processed.json. Auto-detected if None.
            use_semantic (bool): Enable semantic vector retrieval.
            generator_backend (str): 'ollama' or 'transformers'.
            generator_model (str): Model name override.
        """
        if data_path is None:
            code_dir = os.path.dirname(os.path.abspath(__file__))
            data_path = os.path.join(
                os.path.dirname(code_dir), "data", "gita_processed.json"
            )

        print("[Pipeline] Initializing Sanskrit RAG Pipeline...")
        print(f"[Pipeline] Data path: {data_path}")

        # Initialize retriever
        print("[Pipeline] Loading retriever...")
        self.retriever = HybridRetriever(
            data_path=data_path, use_semantic=use_semantic
        )

        # Initialize generator
        print("[Pipeline] Loading generator...")
        self.generator = Generator(
            backend=generator_backend, model_name=generator_model
        )

        if self.generator.active_backend == "none" and generator_backend == "ollama":
            print("[Pipeline] Ollama backend unavailable. Falling back to Transformers...")
            self.generator = Generator(
                backend="transformers", model_name=generator_model
            )

        print("[Pipeline] Pipeline ready!")
        print(f"[Pipeline] Generator backend: {self.generator.active_backend}")

    def query(self, user_query, top_k=5):
        """
        Run the full RAG pipeline: retrieve context, generate response.

        Args:
            user_query (str): The user's question.
            top_k (int): Number of context chunks to retrieve.

        Returns:
            dict: {
                query, retrieved_verses, generated_response,
                retrieval_time_sec, generation_time_sec, total_time_sec,
                generator_backend
            }
        """
        total_start = time.time()

        # Step 1: Retrieve relevant verses
        retrieval_start = time.time()
        retrieved_verses = self.retriever.retrieve(user_query, top_k=top_k)
        retrieval_time = time.time() - retrieval_start

        # Step 2: Build prompt with context
        prompt = self.generator.build_prompt(user_query, retrieved_verses)

        # Step 3: Generate response
        gen_result = self.generator.generate(prompt)

        total_time = time.time() - total_start

        return {
            "query": user_query,
            "retrieved_verses": retrieved_verses,
            "generated_response": gen_result["response"],
            "retrieval_time_sec": round(retrieval_time, 3),
            "generation_time_sec": gen_result["generation_time_sec"],
            "total_time_sec": round(total_time, 2),
            "generator_backend": gen_result["backend"],
            "tokens_generated": gen_result["tokens_generated"],
        }

    def get_system_stats(self):
        """
        Get approximate system resource usage.

        Returns:
            dict: {cpu_percent, memory_used_mb}
        """
        stats = {"cpu_percent": 0.0, "memory_used_mb": 0.0}

        try:
            import psutil
            stats["cpu_percent"] = psutil.cpu_percent(interval=0.5)
            process = psutil.Process(os.getpid())
            stats["memory_used_mb"] = round(
                process.memory_info().rss / (1024 * 1024), 1
            )
        except ImportError:
            # Fallback: rough estimate using os
            try:
                import resource
                usage = resource.getrusage(resource.RUSAGE_SELF)
                stats["memory_used_mb"] = round(usage.ru_maxrss / 1024, 1)
            except (ImportError, AttributeError):
                stats["memory_used_mb"] = 0.0

        return stats


if __name__ == "__main__":
    print("=" * 70)
    print("  Sanskrit Document RAG System - Pipeline Test")
    print("=" * 70)

    # Create pipeline
    pipeline = SanskritRAGPipeline(
        use_semantic=False,
        generator_backend="ollama",
    )

    # Test queries
    test_queries = [
        "What does the Gita say about karma and duty?",
        "dharma and righteousness",
    ]

    for q in test_queries:
        print(f"\n{'='*70}")
        print(f"QUERY: {q}")
        print(f"{'='*70}")

        result = pipeline.query(q, top_k=3)

        print(f"\n--- Retrieved Verses ({result['retrieval_time_sec']}s) ---")
        for i, verse in enumerate(result["retrieved_verses"]):
            print(f"\n[{i+1}] {format_verse_for_display(verse)[:200]}...")

        print(f"\n--- Generated Response ({result['generation_time_sec']}s) ---")
        print(result["generated_response"][:500])

        print(f"\n--- Timing ---")
        print(f"Retrieval: {result['retrieval_time_sec']}s")
        print(f"Generation: {result['generation_time_sec']}s")
        print(f"Total: {result['total_time_sec']}s")
        print(f"Backend: {result['generator_backend']}")
