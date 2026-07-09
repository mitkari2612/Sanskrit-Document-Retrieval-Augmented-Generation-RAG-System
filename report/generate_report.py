"""
generate_report.py - Technical Report Generator
=================================================
Generates a professional PDF technical report for the
Sanskrit Document RAG System using ReportLab.
"""

import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak,
    Table, TableStyle, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.lib import colors
from reportlab.lib.units import inch


def generate_report():
    """Generate the complete technical report PDF."""
    report_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(report_dir, "Sanskrit_RAG_Technical_Report.pdf")

    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        leftMargin=0.75 * inch,
        rightMargin=0.75 * inch,
        topMargin=1 * inch,
        bottomMargin=0.75 * inch,
    )

    styles = getSampleStyleSheet()

    # Custom styles
    cover_title = ParagraphStyle(
        "CoverTitle", parent=styles["Normal"],
        fontName="Helvetica-Bold", fontSize=28, leading=34,
        textColor=colors.HexColor("#D35400"), alignment=TA_CENTER,
    )
    cover_sub = ParagraphStyle(
        "CoverSub", parent=styles["Normal"],
        fontName="Helvetica", fontSize=16, leading=22,
        textColor=colors.HexColor("#2C3E50"), alignment=TA_CENTER,
    )
    cover_info = ParagraphStyle(
        "CoverInfo", parent=styles["Normal"],
        fontName="Helvetica-Oblique", fontSize=12, leading=18,
        textColor=colors.HexColor("#7F8C8D"), alignment=TA_CENTER,
    )
    section_hdr = ParagraphStyle(
        "SectionHeader", parent=styles["Normal"],
        fontName="Helvetica-Bold", fontSize=18, leading=24,
        textColor=colors.HexColor("#D35400"), spaceBefore=20, spaceAfter=10,
    )
    subsec_hdr = ParagraphStyle(
        "SubsectionHeader", parent=styles["Normal"],
        fontName="Helvetica-Bold", fontSize=13, leading=17,
        textColor=colors.HexColor("#2C3E50"), spaceBefore=12, spaceAfter=6,
    )
    body = ParagraphStyle(
        "BodyText2", parent=styles["Normal"],
        fontName="Helvetica", fontSize=10, leading=15,
        textColor=colors.HexColor("#2C3E50"), alignment=TA_JUSTIFY,
        spaceAfter=8,
    )
    bullet = ParagraphStyle(
        "BulletText", parent=body,
        leftIndent=20, bulletIndent=10,
    )

    story = []

    # ===================== COVER PAGE =====================
    story.append(Spacer(1, 120))
    story.append(Paragraph("Sanskrit Document RAG System", cover_title))
    story.append(Spacer(1, 15))
    story.append(Paragraph("Technical Report", cover_sub))
    story.append(Spacer(1, 30))
    story.append(HRFlowable(
        width="60%", thickness=2, color=colors.HexColor("#D35400"),
        spaceBefore=10, spaceAfter=10, hAlign="CENTER"
    ))
    story.append(Spacer(1, 30))
    story.append(Paragraph(
        "Retrieval-Augmented Generation for Bhagavad Gita Corpus", cover_info
    ))
    story.append(Spacer(1, 120))
    story.append(Paragraph("Author: Ajay Mitkari", cover_info))
    story.append(Paragraph("Date: July 2026", cover_info))
    story.append(Paragraph("CPU-Only Inference | Hybrid Retrieval | Streamlit UI", cover_info))
    story.append(PageBreak())

    # ===================== TABLE OF CONTENTS =====================
    story.append(Paragraph("Table of Contents", section_hdr))
    story.append(Spacer(1, 10))
    toc_items = [
        "1. System Architecture and Flow",
        "2. Details of Sanskrit Documents Used",
        "3. Preprocessing Pipeline for Sanskrit Documents",
        "4. Retrieval Mechanism",
        "5. Generation Mechanism",
        "6. Performance Observations",
        "7. CPU Optimization Strategies",
        "8. Conclusion",
    ]
    for item in toc_items:
        story.append(Paragraph(f"\u2022  {item}", body))
    story.append(PageBreak())

    # ===================== SECTION 1 =====================
    story.append(Paragraph("1. System Architecture and Flow", section_hdr))
    story.append(Paragraph(
        "The Sanskrit Document RAG System follows a modular Retrieval-Augmented Generation "
        "architecture that separates document ingestion, retrieval, and generation into "
        "independent, composable components. This design ensures maintainability, testability, "
        "and the ability to swap components without affecting the overall pipeline.", body
    ))
    story.append(Paragraph("Architecture Flow", subsec_hdr))
    story.append(Paragraph(
        "The system operates in the following sequential stages:", body
    ))

    flow_items = [
        "<b>Document Loader (ingest.py):</b> Downloads raw Sanskrit verse data and translations "
        "from a public GitHub repository in JSON format.",
        "<b>Preprocessor (ingest.py):</b> Merges verses with their transliterations, word meanings, "
        "and multi-language translations. Outputs a unified JSON database, TXT corpus, and PDF corpus.",
        "<b>Indexer (retriever.py):</b> Builds a character n-gram TF-IDF index over all verse chunks. "
        "Optionally builds a semantic vector index using multilingual sentence-transformers.",
        "<b>Retriever (retriever.py):</b> Accepts user queries and retrieves the most relevant verse "
        "chunks using hybrid TF-IDF + semantic search with Reciprocal Rank Fusion.",
        "<b>Generator (generator.py):</b> Constructs a context-grounded prompt with retrieved verses "
        "and generates a coherent response using a CPU-based LLM (Ollama or HuggingFace Transformers).",
        "<b>Web Interface (app.py):</b> A Streamlit application presenting a saffron-gold themed UI "
        "for interactive query-response with real-time metrics.",
    ]
    for item in flow_items:
        story.append(Paragraph(f"\u2022  {item}", bullet))
    story.append(Spacer(1, 10))

    # ===================== SECTION 2 =====================
    story.append(Paragraph("2. Details of Sanskrit Documents Used", section_hdr))
    story.append(Paragraph(
        "The primary corpus consists of the <b>Srimad Bhagavad Gita</b>, one of the most "
        "important texts in Hindu philosophy and Sanskrit literature. The Gita is a 700-verse "
        "scripture that is part of the Indian epic Mahabharata.", body
    ))

    doc_table_data = [
        ["Property", "Details"],
        ["Source Text", "Srimad Bhagavad Gita"],
        ["Language", "Sanskrit (Devanagari script)"],
        ["Total Chapters", "18"],
        ["Total Verses", "~700"],
        ["Data Format", "JSON (verse text, transliteration, word meanings, translations)"],
        ["Data Source", "praneshp1org/Bhagavad-Gita-JSON-data (GitHub)"],
        ["Translations", "English (Swami Sivananda et al.), Hindi"],
        ["Output Formats", "JSON database, TXT corpus, PDF corpus"],
    ]
    doc_table = Table(doc_table_data, colWidths=[1.8 * inch, 4.2 * inch])
    doc_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#D35400")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("LEADING", (0, 0), (-1, -1), 14),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#BDC3C7")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8F9F9")]),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(doc_table)
    story.append(Spacer(1, 10))

    # ===================== SECTION 3 =====================
    story.append(Paragraph("3. Preprocessing Pipeline for Sanskrit Documents", section_hdr))
    story.append(Paragraph(
        "The preprocessing pipeline transforms raw JSON data into a structured, searchable corpus:", body
    ))
    preproc_items = [
        "<b>Data Download:</b> Raw verse data (verse.json) and translations (translation.json) "
        "are downloaded from the public GitHub repository using urllib.",
        "<b>Parsing and Merging:</b> Verses are matched with their corresponding translations by "
        "verse_id. English translations are prioritized (Swami Sivananda preferred), and Hindi "
        "translations are also extracted.",
        "<b>Text Normalization:</b> Whitespace is normalized, empty lines are removed, and text "
        "is cleaned for consistent indexing.",
        "<b>Chunk Strategy:</b> Each verse constitutes one retrieval chunk, containing all its "
        "metadata: Sanskrit text, transliteration, word meanings, and translations. This ensures "
        "that retrieved chunks are semantically complete.",
        "<b>Output Generation:</b> Three output formats are produced: (1) gita_processed.json "
        "for programmatic access, (2) bhagavad_gita_corpus.txt for readable text, and "
        "(3) bhagavad_gita_corpus.pdf as a formatted document.",
    ]
    for item in preproc_items:
        story.append(Paragraph(f"\u2022  {item}", bullet))

    # ===================== SECTION 4 =====================
    story.append(Paragraph("4. Retrieval Mechanism", section_hdr))
    story.append(Paragraph(
        "The retrieval system employs a hybrid approach combining keyword-based and optional "
        "semantic search to maximize recall and precision across Sanskrit, transliterated, "
        "and English queries.", body
    ))

    story.append(Paragraph("4.1 TF-IDF Character N-Gram Retrieval", subsec_hdr))
    story.append(Paragraph(
        "The primary retriever uses scikit-learn's TfidfVectorizer with a character n-gram "
        "analyzer (analyzer='char_wb', ngram_range=(2,5)). This design choice is critical "
        "for Sanskrit text retrieval because:", body
    ))
    tfidf_items = [
        "Sanskrit transliterations have significant spelling variations (e.g., 'dharma' vs "
        "'dharmma', 'karma' vs 'karmma').",
        "Character n-grams capture sub-word patterns that are resilient to these variations.",
        "The char_wb analyzer respects word boundaries, preventing false matches across words.",
        "Sublinear TF (sublinear_tf=True) dampens the effect of high-frequency terms.",
    ]
    for item in tfidf_items:
        story.append(Paragraph(f"\u2022  {item}", bullet))

    story.append(Paragraph("4.2 Semantic Vector Retrieval (Optional)", subsec_hdr))
    story.append(Paragraph(
        "When enabled, a multilingual sentence-transformer model "
        "(paraphrase-multilingual-MiniLM-L12-v2) encodes verse chunks and queries into dense "
        "vectors. Cosine similarity is used to find semantically similar verses, even when "
        "exact keyword matches are absent.", body
    ))

    story.append(Paragraph("4.3 Reciprocal Rank Fusion (RRF)", subsec_hdr))
    story.append(Paragraph(
        "When both retrievers are active, their results are combined using Reciprocal Rank "
        "Fusion with the formula: RRF_score = \u03a3(1 / (k + rank_i)) for each retriever i. "
        "This produces a balanced ranking that leverages the strengths of both approaches.", body
    ))

    # ===================== SECTION 5 =====================
    story.append(Paragraph("5. Generation Mechanism", section_hdr))
    story.append(Paragraph(
        "The generation component supports two CPU-only inference backends:", body
    ))

    story.append(Paragraph("5.1 Ollama Backend (Primary)", subsec_hdr))
    story.append(Paragraph(
        "Ollama provides a lightweight, optimized runtime for running LLMs locally. The system "
        "uses the qwen2.5:0.5b model (500M parameters), which requires approximately 350MB of "
        "RAM and generates tokens at 5-15 tokens/second on CPU.", body
    ))

    story.append(Paragraph("5.2 HuggingFace Transformers Backend (Fallback)", subsec_hdr))
    story.append(Paragraph(
        "As a fallback, the system can load Qwen/Qwen2.5-0.5B-Instruct directly using the "
        "HuggingFace transformers library with PyTorch. This is fully self-contained but "
        "typically slower than Ollama on CPU.", body
    ))

    story.append(Paragraph("5.3 Prompt Engineering", subsec_hdr))
    story.append(Paragraph(
        "The generator constructs context-grounded prompts that include the retrieved verse "
        "context (Sanskrit text, transliteration, word meanings, and translations) along with "
        "a system instruction to act as a Sanskrit scholar. This ensures responses are grounded "
        "in the actual corpus and reduces hallucination.", body
    ))

    # ===================== SECTION 6 =====================
    story.append(Paragraph("6. Performance Observations", section_hdr))
    story.append(Paragraph(
        "The following table summarizes expected performance characteristics on a typical "
        "CPU-only system (Intel Core i5, 8GB RAM):", body
    ))

    perf_data = [
        ["Metric", "Value", "Notes"],
        ["Retrieval Latency (TF-IDF)", "50-200 ms", "700 verse corpus, sparse matrix ops"],
        ["Retrieval Latency (Semantic)", "200-500 ms", "Depends on model load time"],
        ["Generation Latency (Ollama)", "5-20 s", "qwen2.5:0.5b, 100-200 tokens"],
        ["Generation Latency (HF)", "10-45 s", "Qwen2.5-0.5B-Instruct, CPU float32"],
        ["Total Pipeline Latency", "5-45 s", "Retrieval + Generation combined"],
        ["Model Memory (Ollama)", "~350 MB", "Quantized model in Ollama runtime"],
        ["Model Memory (HF)", "~1.2 GB", "Float32 weights in PyTorch"],
        ["TF-IDF Index Size", "~5 MB", "Sparse matrix in memory"],
        ["Corpus Size", "~2 MB", "700 verses with full metadata"],
    ]
    perf_table = Table(perf_data, colWidths=[2.2 * inch, 1.3 * inch, 2.8 * inch])
    perf_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#D35400")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("LEADING", (0, 0), (-1, -1), 14),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#BDC3C7")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8F9F9")]),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(perf_table)

    # ===================== SECTION 7 =====================
    story.append(Paragraph("7. CPU Optimization Strategies", section_hdr))
    opt_items = [
        "<b>Small Model Selection:</b> The 0.5B parameter Qwen2.5 model was chosen specifically "
        "for CPU inference. It fits comfortably in 350MB-1.2GB RAM while maintaining reasonable "
        "generation quality for scholarly text.",
        "<b>Ollama Runtime:</b> Ollama provides hardware-optimized inference with GGUF quantized "
        "models, typically achieving 2-3x speedup over raw PyTorch on CPU.",
        "<b>Sparse TF-IDF Indexing:</b> The TF-IDF matrix uses scipy sparse matrices, ensuring "
        "near-zero memory overhead for the retrieval index.",
        "<b>Character N-Gram Efficiency:</b> Character-level indexing with max_features=50000 "
        "caps vocabulary size while maintaining retrieval quality.",
        "<b>Streamlit Caching:</b> The @st.cache_resource decorator ensures the pipeline "
        "(model + index) is loaded only once per session.",
        "<b>Optional Semantic Search:</b> Semantic vector search is disabled by default and can "
        "be toggled on only when sufficient RAM is available.",
    ]
    for item in opt_items:
        story.append(Paragraph(f"\u2022  {item}", bullet))

    # ===================== SECTION 8 =====================
    story.append(Paragraph("8. Conclusion", section_hdr))
    story.append(Paragraph(
        "This project demonstrates a complete, modular Retrieval-Augmented Generation system "
        "for Sanskrit documents, operating entirely on CPU-based inference. The system "
        "successfully ingests, indexes, retrieves, and generates responses from the Bhagavad "
        "Gita corpus using a combination of character n-gram keyword search and optional "
        "semantic vector retrieval.", body
    ))
    story.append(Paragraph(
        "Key achievements include: (1) robust handling of Sanskrit text in both Devanagari "
        "and transliterated formats, (2) efficient CPU inference with sub-minute response "
        "times, (3) a modular architecture that allows easy swapping of retrieval and "
        "generation components, and (4) a polished web interface for interactive exploration.", body
    ))
    story.append(Paragraph("Future Improvements", subsec_hdr))
    future_items = [
        "Support for additional Sanskrit texts (Upanishads, Vedas, Arthashastra).",
        "Fine-tuned Sanskrit-specific embedding models for improved semantic retrieval.",
        "GPU-accelerated inference for larger models (7B+ parameters).",
        "Multi-turn conversational interface with chat history.",
        "Devanagari OCR for ingesting scanned Sanskrit manuscripts.",
    ]
    for item in future_items:
        story.append(Paragraph(f"\u2022  {item}", bullet))

    # Build the PDF
    doc.build(story)
    print(f"[Report] Technical report generated at: {output_path}")
    return output_path


if __name__ == "__main__":
    print("=" * 60)
    print("  Generating Sanskrit RAG System Technical Report")
    print("=" * 60)
    path = generate_report()
    print(f"\nReport saved to: {path}")
