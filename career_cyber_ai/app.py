# ============================================================
# app.py — Streamlit Frontend
# AI Cyber Threat Intelligence Assistant
# ============================================================
#
# Run with:  streamlit run app.py
# ============================================================

import streamlit as st
import time
import os
from dotenv import load_dotenv

# Load environment variables before importing modules
load_dotenv()

from modules.data_loader import DataLoader
from modules.rag_pipeline import RAGPipeline
from modules.memory import MemoryManager

# ──────────────────────────────────────────────────────────────
# Page Config & Custom CSS
# ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="CyberSentinel AI — Threat Intelligence Assistant",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    /* Global dark theme overrides */
    .stApp {
        background: linear-gradient(135deg, #0a0a1a 0%, #1a1a2e 50%, #16213e 100%);
    }
    .main-header {
        background: linear-gradient(90deg, #00d2ff 0%, #3a7bd5 50%, #6c5ce7 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.5rem;
        font-weight: 800;
        text-align: center;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        color: #a0aec0;
        text-align: center;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    .source-badge {
        display: inline-block;
        background: rgba(106, 90, 205, 0.2);
        border: 1px solid rgba(106, 90, 205, 0.4);
        border-radius: 16px;
        padding: 4px 12px;
        margin: 2px 4px;
        font-size: 0.82rem;
        color: #b8c0ff;
    }
    .status-ok {
        color: #48bb78;
        font-weight: 600;
    }
    .status-err {
        color: #fc8181;
        font-weight: 600;
    }
    .memory-item {
        background: rgba(255,255,255,0.03);
        border-left: 3px solid #6c5ce7;
        padding: 8px 12px;
        margin: 6px 0;
        border-radius: 0 6px 6px 0;
        font-size: 0.88rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ──────────────────────────────────────────────────────────────
# Session State Initialization
# ──────────────────────────────────────────────────────────────
if "initialized" not in st.session_state:
    st.session_state.initialized = False
if "rag_pipeline" not in st.session_state:
    st.session_state.rag_pipeline = None
if "memory_manager" not in st.session_state:
    st.session_state.memory_manager = None


# ──────────────────────────────────────────────────────────────
# Initialization Logic (runs once on first load)
# ──────────────────────────────────────────────────────────────
@st.cache_resource(show_spinner=False)
def initialize_system():
    """
    One-time setup: load data into Endee, instantiate pipeline
    and memory manager.  Cached so it only runs once per process.
    """
    loader = DataLoader()
    loader.initialize_index()
    loader.ingest_data()

    pipeline = RAGPipeline()
    memory = MemoryManager()
    return pipeline, memory


# ──────────────────────────────────────────────────────────────
# Sidebar
# ──────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🛡️ CyberSentinel AI")
    st.markdown("---")

    # --- System Status ------------------------------------------------
    st.markdown("### ⚡ System Status")
    api_key_set = bool(os.getenv("OPENAI_API_KEY"))
    st.markdown(
        f"OpenAI API: <span class='{'status-ok' if api_key_set else 'status-err'}'>"
        f"{'Connected' if api_key_set else 'Not Configured'}</span>",
        unsafe_allow_html=True,
    )
    endee_host = os.getenv("ENDEE_HOST", "localhost")
    endee_port = os.getenv("ENDEE_PORT", "8080")
    st.markdown(
        f"Endee DB: <span class='status-ok'>{endee_host}:{endee_port}</span>",
        unsafe_allow_html=True,
    )
    st.markdown("---")

    # --- Example Queries ----------------------------------------------
    st.markdown("### 💡 Example Queries")
    examples = [
        "What is SQL Injection?",
        "Explain CVE-2021-44228 (Log4Shell)",
        "How does phishing work?",
        "What is MITRE ATT&CK Lateral Movement?",
        "How to prevent ransomware attacks?",
        "Explain the EternalBlue exploit",
        "What are OWASP Top 10 vulnerabilities?",
        "How to detect XSS attacks?",
    ]
    selected_example = None
    for example in examples:
        if st.button(f"🔹 {example}", key=f"ex_{example}", use_container_width=True):
            selected_example = example

    st.markdown("---")

    # --- Recent Queries -----------------------------------------------
    st.markdown("### 📜 Recent Queries")
    if st.session_state.memory_manager:
        recent = st.session_state.memory_manager.get_recent_queries(5)
        if recent:
            for item in recent:
                st.markdown(
                    f"<div class='memory-item'>🔍 {item['query']}</div>",
                    unsafe_allow_html=True,
                )
        else:
            st.caption("No queries yet. Ask something!")
    else:
        st.caption("System initializing …")

    st.markdown("---")

    # --- Clear Memory Button ------------------------------------------
    if st.button("🗑️ Clear Memory", use_container_width=True):
        if st.session_state.memory_manager:
            st.session_state.memory_manager.clear_memory()
            st.success("Memory cleared!")
            st.rerun()

# ──────────────────────────────────────────────────────────────
# Main Content Area
# ──────────────────────────────────────────────────────────────
st.markdown("<h1 class='main-header'>🛡️ CyberSentinel AI</h1>", unsafe_allow_html=True)
st.markdown(
    "<p class='sub-header'>"
    "AI-Powered Cyber Threat Intelligence Assistant · "
    "Powered by RAG + Endee Vector DB"
    "</p>",
    unsafe_allow_html=True,
)

# ---- Initialise the backend (on first run) -----------------------
if not st.session_state.initialized:
    with st.spinner("🔄 Initializing CyberSentinel AI — loading knowledge base into Endee …"):
        try:
            pipeline, memory = initialize_system()
            st.session_state.rag_pipeline = pipeline
            st.session_state.memory_manager = memory
            st.session_state.initialized = True
            st.success("✅ System ready! Knowledge base loaded into Endee Vector DB.")
        except Exception as e:
            st.error(
                f"❌ Initialization failed: {e}\n\n"
                "Make sure Endee is running (`docker compose up -d`) "
                "and your .env file is configured."
            )
            st.stop()

# ---- Query Input Area --------------------------------------------
st.markdown("### 🔍 Ask a Cybersecurity Question")

# Use example query if one was selected in the sidebar
query = st.text_input(
    "Enter your query:",
    value=selected_example or "",
    placeholder="e.g., What is SQL Injection and how can I prevent it?",
    label_visibility="collapsed",
)

col1, col2 = st.columns([1, 5])
with col1:
    search_clicked = st.button("🚀 Analyze", type="primary", use_container_width=True)
with col2:
    top_k = st.slider("Context depth", min_value=1, max_value=5, value=3, help="Number of knowledge base entries to retrieve")

# ---- Process Query -----------------------------------------------
if search_clicked and query:
    if not os.getenv("OPENAI_API_KEY"):
        st.error("⚠️ Please set your OPENAI_API_KEY in the .env file.")
        st.stop()

    with st.spinner("🧠 Analyzing threat intelligence …"):
        start_time = time.time()

        # Retrieve relevant memory context for personalisation
        memory_context = ""
        if st.session_state.memory_manager:
            memory_context = st.session_state.memory_manager.get_relevant_history(query)

        # Run the RAG pipeline
        result = st.session_state.rag_pipeline.generate_response(
            query=query,
            top_k=top_k,
            memory_context=memory_context,
        )

        elapsed = time.time() - start_time

    # ---- Display Results -----------------------------------------
    st.markdown("---")
    st.markdown("### 📋 Threat Intelligence Report")

    # Metadata bar
    st.markdown(
        f"⏱️ Response time: **{elapsed:.2f}s** &nbsp;|&nbsp; "
        f"📚 Sources: **{len(result['sources'])}** entries"
    )

    # Main answer
    st.markdown(result["answer"])

    # Source attribution
    if result["sources"]:
        st.markdown("#### 🔗 Knowledge Base Sources")
        badges = " ".join(
            f"<span class='source-badge'>{src}</span>" for src in result["sources"]
        )
        st.markdown(badges, unsafe_allow_html=True)

    # Memory context indicator
    if memory_context:
        with st.expander("🧠 Memory Context Used"):
            st.markdown(memory_context)

    # Store interaction in memory
    if st.session_state.memory_manager:
        st.session_state.memory_manager.store_interaction(query, result["answer"])

elif search_clicked and not query:
    st.warning("⚠️ Please enter a query first.")

# ──────────────────────────────────────────────────────────────
# Footer
# ──────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<div style='text-align:center; color:#4a5568; font-size:0.85rem;'>"
    "🛡️ CyberSentinel AI — Built with Endee Vector DB, "
    "OpenAI, and Sentence Transformers<br>"
    "⚠️ For educational and research purposes only. "
    "Always verify findings with official sources."
    "</div>",
    unsafe_allow_html=True,
)
