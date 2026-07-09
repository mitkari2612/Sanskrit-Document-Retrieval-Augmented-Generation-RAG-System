"""
app.py - Streamlit Web Application for Sanskrit Document RAG System
====================================================================
A premium saffron-gold themed interface for querying the
Bhagavad Gita corpus using the RAG pipeline.
"""

import os
import sys
import time

# Ensure local imports work
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st

# --- Page Configuration ---
st.set_page_config(
    page_title="Sanskrit RAG System",
    page_icon="\U0001f549\ufe0f",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Custom CSS ---
st.markdown("""
<style>
    /* Import Google Font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    /* Global styles */
    .stApp {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
        font-family: 'Inter', sans-serif;
    }

    /* Main header */
    .main-header {
        text-align: center;
        padding: 2rem 0 1rem 0;
    }
    .main-header h1 {
        color: #D35400;
        font-size: 2.8rem;
        font-weight: 700;
        margin-bottom: 0.2rem;
        text-shadow: 0 2px 10px rgba(211,84,0,0.3);
    }
    .main-header p {
        color: #BDC3C7;
        font-size: 1.1rem;
        font-weight: 300;
    }

    /* Decorative divider */
    .saffron-divider {
        height: 3px;
        background: linear-gradient(90deg, transparent, #D35400, #F39C12, #D35400, transparent);
        border: none;
        margin: 1rem 0 2rem 0;
        border-radius: 2px;
    }

    /* Card styling */
    .verse-card {
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(211,84,0,0.2);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 0.8rem 0;
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
    }
    .verse-card:hover {
        border-color: rgba(211,84,0,0.5);
        box-shadow: 0 4px 20px rgba(211,84,0,0.15);
        transform: translateY(-2px);
    }

    /* Sanskrit text */
    .sanskrit-text {
        color: #1ABC9C;
        font-size: 1.1rem;
        line-height: 1.8;
        padding: 0.5rem 0;
    }

    /* Transliteration */
    .translit-text {
        color: #3498DB;
        font-style: italic;
        font-size: 0.95rem;
        line-height: 1.6;
    }

    /* Meaning text */
    .meaning-text {
        color: #95A5A6;
        font-size: 0.85rem;
        line-height: 1.5;
    }

    /* Translation */
    .translation-text {
        color: #ECF0F1;
        font-size: 0.95rem;
        line-height: 1.6;
        padding: 0.5rem 0;
    }

    /* Response container */
    .response-container {
        background: rgba(211,84,0,0.08);
        border-left: 4px solid #D35400;
        border-radius: 0 12px 12px 0;
        padding: 1.5rem;
        margin: 1rem 0;
        color: #ECF0F1;
        line-height: 1.7;
    }

    /* Metric cards */
    .metric-card {
        background: rgba(255,255,255,0.05);
        border-radius: 10px;
        padding: 1rem;
        text-align: center;
        border: 1px solid rgba(243,156,18,0.2);
    }
    .metric-card .value {
        color: #F39C12;
        font-size: 1.5rem;
        font-weight: 700;
    }
    .metric-card .label {
        color: #BDC3C7;
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    /* Example query buttons */
    .example-btn {
        display: inline-block;
        background: rgba(211,84,0,0.15);
        border: 1px solid rgba(211,84,0,0.3);
        color: #F39C12 !important;
        padding: 0.4rem 1rem;
        border-radius: 20px;
        margin: 0.3rem;
        font-size: 0.85rem;
        cursor: pointer;
        transition: all 0.3s ease;
        text-decoration: none;
    }
    .example-btn:hover {
        background: rgba(211,84,0,0.3);
        border-color: #D35400;
    }

    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
    }
    [data-testid="stSidebar"] .stMarkdown h2 {
        color: #D35400;
    }

    /* Input styling */
    .stTextInput > div > div > input {
        background: rgba(255,255,255,0.08) !important;
        border: 1px solid rgba(211,84,0,0.3) !important;
        color: #ECF0F1 !important;
        border-radius: 10px !important;
        padding: 0.8rem 1rem !important;
        font-size: 1rem !important;
    }
    .stTextInput > div > div > input:focus {
        border-color: #D35400 !important;
        box-shadow: 0 0 10px rgba(211,84,0,0.3) !important;
    }

    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #D35400, #E67E22) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 0.6rem 2rem !important;
        font-weight: 600 !important;
        letter-spacing: 0.5px !important;
        transition: all 0.3s ease !important;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #E67E22, #F39C12) !important;
        box-shadow: 0 4px 15px rgba(211,84,0,0.4) !important;
        transform: translateY(-1px) !important;
    }

    /* Expander styling */
    .streamlit-expanderHeader {
        background: rgba(255,255,255,0.05) !important;
        border-radius: 8px !important;
        color: #ECF0F1 !important;
    }

    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* Animation */
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .animate-in {
        animation: fadeInUp 0.5s ease-out;
    }
</style>
""", unsafe_allow_html=True)


# --- Pipeline Initialization ---
@st.cache_resource
def load_pipeline(use_semantic, backend, model_name):
    """Load and cache the RAG pipeline."""
    from rag_pipeline import SanskritRAGPipeline
    return SanskritRAGPipeline(
        use_semantic=use_semantic,
        generator_backend=backend,
        generator_model=model_name if model_name else None,
    )


# --- Sidebar ---
with st.sidebar:
    st.markdown("## Configuration")
    st.markdown("---")

    gen_backend = st.radio(
        "Generator Backend",
        options=["ollama", "transformers"],
        index=0,
        help="Ollama: fast, lightweight. Transformers: self-contained Python."
    )

    if gen_backend == "ollama":
        model_name = st.text_input("Model Name", value="qwen2.5:0.5b")
    else:
        model_name = st.text_input("Model Name", value="Qwen/Qwen2.5-0.5B-Instruct")

    top_k = st.slider("Number of Results", min_value=1, max_value=10, value=5)

    use_semantic = st.toggle("Enable Semantic Search", value=False,
                             help="Uses multilingual sentence-transformers. Requires more RAM.")

    st.markdown("---")
    st.markdown("## 📊 System Info")

    # System stats placeholder
    stats_placeholder = st.empty()

    st.markdown("---")
    st.markdown("## ℹ️ About")
    st.markdown(
        "This system uses **Retrieval-Augmented Generation** to answer "
        "questions about the **Srimad Bhagavad Gita** in Sanskrit, "
        "transliterated text, or English."
    )
    st.markdown(
        "Built with character n-gram TF-IDF retrieval and "
        "CPU-optimized LLM generation."
    )


# --- Main Content ---
st.markdown("""
<div class="main-header animate-in">
    <h1>🕉️ Sanskrit Document RAG System</h1>
    <p>Srimad Bhagavad Gita Knowledge Base • Powered by CPU-Based AI</p>
""", unsafe_allow_html=True)

# Search input
query = st.text_input(
    "Search",
    placeholder="Enter your query in Sanskrit, transliteration, or English...",
    label_visibility="collapsed",
)

# Example queries
st.markdown("**💡 Try these examples:**")
example_cols = st.columns(4)
examples = [
    "What is karma yoga?",
    "\u0915\u0930\u094d\u092e\u0923\u094d\u092f\u0947\u0935\u093e\u0927\u093f\u0915\u093e\u0930\u0938\u094d\u0924\u0947",
    "dharma and duty",
    "What does Krishna say about meditation?",
]
for i, ex in enumerate(examples):
    with example_cols[i]:
        if st.button(ex, key=f"ex_{i}", use_container_width=True):
            query = ex

# Search button
search_clicked = st.button("🔍 Search the Gita", use_container_width=True)

# --- Process Query ---
if (search_clicked or query) and query.strip():
    try:
        # Load pipeline
        with st.spinner("🕉️ Initializing pipeline..."):
            pipeline = load_pipeline(use_semantic, gen_backend, model_name)

        # Run query
        with st.spinner("🔍 Searching and generating response..."):
            result = pipeline.query(query.strip(), top_k=top_k)

        # Metrics
        st.markdown('<div class="animate-in">', unsafe_allow_html=True)
        met_cols = st.columns(4)
        with met_cols[0]:
            st.metric("Retrieval Time", f"{result['retrieval_time_sec']}s")
        with met_cols[1]:
            st.metric("Generation Time", f"{result['generation_time_sec']}s")
        with met_cols[2]:
            st.metric("Total Time", f"{result['total_time_sec']}s")
        with met_cols[3]:
            st.metric("Backend", result['generator_backend'].title())
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("---")

        # Generated Response
        st.markdown("### 💬 Generated Answer")
        st.markdown(
            f'<div class="response-container animate-in">{result["generated_response"]}</div>',
            unsafe_allow_html=True,
        )

        st.markdown("---")

        # Retrieved Verses
        st.markdown(f"### 🗜️ Retrieved Verses ({len(result['retrieved_verses'])} matches)")

        for i, verse in enumerate(result["retrieved_verses"]):
            ch = verse.get("chapter_number", "?")
            vn = verse.get("verse_number", "?")

            with st.expander(f"\U0001f549\ufe0f Chapter {ch}, Verse {vn}", expanded=(i == 0)):
                # Sanskrit text
                if verse.get("text"):
                    st.markdown(
                        f'<div class="sanskrit-text">{verse["text"]}</div>',
                        unsafe_allow_html=True,
                    )

                # Transliteration
                if verse.get("transliteration"):
                    st.markdown(
                        f'<div class="translit-text">{verse["transliteration"]}</div>',
                        unsafe_allow_html=True,
                    )

                # Word meanings
                if verse.get("word_meanings"):
                    st.markdown(
                        f'<div class="meaning-text"><b>Word Meanings:</b> {verse["word_meanings"]}</div>',
                        unsafe_allow_html=True,
                    )

                # English translation
                if verse.get("english_translation"):
                    st.markdown(
                        f'<div class="translation-text"><b>Translation:</b> {verse["english_translation"]}</div>',
                        unsafe_allow_html=True,
                    )

        # Update system stats
        try:
            stats = pipeline.get_system_stats()
            with stats_placeholder:
                st.metric("CPU Usage", f"{stats['cpu_percent']}%")
                st.metric("Memory (Process)", f"{stats['memory_used_mb']} MB")
        except Exception:
            pass

    except FileNotFoundError:
        st.error(
            "\u274c **Corpus not found!** Please run `python ingest.py` first "
            "to download and process the Sanskrit documents."
        )
    except Exception as e:
        st.error(f"\u274c An error occurred: {str(e)}")

else:
    # Welcome state
    st.markdown("""
    <div style="text-align: center; padding: 3rem 0; color: #7F8C8D;">
        <p style="font-size: 3rem;">\U0001f549\ufe0f</p>
        <p style="font-size: 1.2rem; color: #BDC3C7;">
            Ask a question about the Bhagavad Gita
        </p>
        <p style="font-size: 0.9rem;">
            Supports queries in Sanskrit (Devanagari), Roman transliteration, or English
        </p>
    </div>
    """, unsafe_allow_html=True)
