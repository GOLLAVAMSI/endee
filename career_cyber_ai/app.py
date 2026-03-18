# ============================================================
# app.py — CyberSentinel AI — Premium Streamlit UI
# ============================================================

import streamlit as st
import time
import os
from dotenv import load_dotenv

load_dotenv()

from modules.data_loader import DataLoader
from modules.rag_pipeline import RAGPipeline
from modules.memory import MemoryManager

# ──────────────────────────────────────────────────────────────
# Page Config
# ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="CyberSentinel AI",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────────────────────────
# Premium CSS — Apple / Samsung inspired design
# ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

/* ===== GLOBAL ===== */
*, *::before, *::after { font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important; }

.stApp {
    background: #000000;
    color: #f5f5f7;
}
html, body, [data-testid="stAppViewContainer"] {
    background: #000000 !important;
}

/* Remove default Streamlit padding and add bottom padding for fixed footer */
.block-container { padding-top: 2rem !important; padding-bottom: 80px !important; max-width: 900px !important; }

/* ===== SCROLLBAR ===== */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.15); border-radius: 3px; }

/* ===== TYPOGRAPHY ===== */
.hero-title {
    font-size: 3.2rem;
    font-weight: 800;
    letter-spacing: -0.03em;
    text-align: center;
    margin-bottom: 0;
    line-height: 1.1;
    background: linear-gradient(135deg, #60a5fa, #a78bfa, #f472b6);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: shimmer 3s ease-in-out infinite alternate;
}
@keyframes shimmer {
    0% { filter: brightness(1); }
    100% { filter: brightness(1.15); }
}
.hero-subtitle {
    text-align: center;
    color: #86868b;
    font-size: 1.1rem;
    font-weight: 400;
    letter-spacing: 0.01em;
    margin-top: 0.5rem;
    margin-bottom: 2.5rem;
}

/* ===== ALL TEXT — LIGHT ===== */
.stApp p, .stApp li, .stApp span, .stApp label,
.stApp div[data-testid="stMarkdownContainer"] p,
.stApp div[data-testid="stMarkdownContainer"] li,
.stApp div[data-testid="stMarkdownContainer"] span,
.stApp div[data-testid="stMarkdownContainer"] ol,
.stApp div[data-testid="stMarkdownContainer"] ul {
    color: #d1d1d6 !important;
    line-height: 1.7 !important;
}
.stApp h1, .stApp h2, .stApp h3, .stApp h4,
.stApp div[data-testid="stMarkdownContainer"] h1,
.stApp div[data-testid="stMarkdownContainer"] h2,
.stApp div[data-testid="stMarkdownContainer"] h3 {
    color: #f5f5f7 !important;
    font-weight: 600 !important;
    letter-spacing: -0.02em !important;
}
.stApp strong, .stApp b,
.stApp div[data-testid="stMarkdownContainer"] strong {
    color: #ffffff !important;
}

/* ===== GLASS CARD ===== */
.glass-card {
    background: rgba(28, 28, 30, 0.7);
    backdrop-filter: blur(40px);
    -webkit-backdrop-filter: blur(40px);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 20px;
    padding: 2rem 2rem;
    margin-bottom: 1.5rem;
    box-shadow: 0 8px 32px rgba(0,0,0,0.4);
}
.glass-card-sm {
    background: rgba(28, 28, 30, 0.5);
    backdrop-filter: blur(20px);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 14px;
    padding: 1.2rem 1.4rem;
    margin-bottom: 1rem;
}

/* ===== SIDEBAR ===== */
section[data-testid="stSidebar"] {
    background: rgba(18, 18, 20, 0.95) !important;
    border-right: 1px solid rgba(255,255,255,0.06) !important;
}
section[data-testid="stSidebar"] > div {
    background: transparent !important;
}
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] li {
    color: #a1a1a6 !important;
}
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {
    color: #f5f5f7 !important;
    font-weight: 600 !important;
    letter-spacing: -0.01em !important;
    font-size: 0.85rem !important;
    text-transform: uppercase !important;
}
section[data-testid="stSidebar"] hr {
    border-color: rgba(255,255,255,0.06) !important;
    margin: 1rem 0 !important;
}
/* Sidebar buttons */
section[data-testid="stSidebar"] button {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    color: #d1d1d6 !important;
    border-radius: 12px !important;
    font-size: 0.85rem !important;
    font-weight: 400 !important;
    transition: all 0.2s ease !important;
    padding: 0.5rem 0.5rem !important;
    min-height: 48px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: flex-start !important;
}
section[data-testid="stSidebar"] button p {
    font-size: 0.85rem !important;
    margin: 0 !important;
    text-align: left !important;
    line-height: 1.3 !important;
}
section[data-testid="stSidebar"] button:hover {
    background: rgba(59, 130, 246, 0.12) !important;
    border-color: rgba(59, 130, 246, 0.3) !important;
    color: #60a5fa !important;
    transform: translateY(-1px);
}

/* ===== PRIMARY BUTTON (Analyze) ===== */
.stApp button[data-testid="stBaseButton-primary"],
.stApp button[kind="primary"] {
    background: #0a84ff !important;
    border: none !important;
    color: #ffffff !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    border-radius: 14px !important;
    padding: 0.65rem 2rem !important;
    letter-spacing: 0.01em !important;
    box-shadow: 0 4px 16px rgba(10, 132, 255, 0.3) !important;
    transition: all 0.25s ease !important;
}
.stApp button[data-testid="stBaseButton-primary"]:hover,
.stApp button[kind="primary"]:hover {
    background: #409cff !important;
    box-shadow: 0 6px 24px rgba(10, 132, 255, 0.45) !important;
    transform: translateY(-1px);
}

/* ===== SLIDER (blue) ===== */
.stApp div[data-testid="stSlider"] > div > div > div > div {
    background: #0a84ff !important;
}
.stApp div[data-testid="stSlider"] div[role="slider"] {
    background: #ffffff !important;
    border: 2px solid #0a84ff !important;
    box-shadow: 0 2px 8px rgba(10,132,255,0.3) !important;
}
.stApp .stSlider > div > div > div > div:first-child {
    background: #0a84ff !important;
}
.stApp div[data-testid="stSlider"] label span {
    color: #a1a1a6 !important;
}

/* ===== TEXT INPUT ===== */
.stApp .stTextInput > div > div {
    background: rgba(28, 28, 30, 0.8) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 14px !important;
    transition: border-color 0.2s ease !important;
}
.stApp .stTextInput > div > div:focus-within {
    border-color: #0a84ff !important;
    box-shadow: 0 0 0 3px rgba(10,132,255,0.15) !important;
}
.stApp .stTextInput input {
    color: #f5f5f7 !important;
    font-size: 1rem !important;
    padding: 0.75rem 1rem !important;
}
.stApp .stTextInput input::placeholder {
    color: #636366 !important;
}

/* ===== SOURCE BADGE ===== */
.source-badge {
    display: inline-block;
    background: rgba(10, 132, 255, 0.1);
    border: 1px solid rgba(10, 132, 255, 0.25);
    border-radius: 100px;
    padding: 6px 16px;
    margin: 3px 4px;
    font-size: 0.8rem;
    font-weight: 500;
    color: #60a5fa !important;
    letter-spacing: 0.01em;
}

/* ===== STATUS PILLS ===== */
.status-pill {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 4px 14px;
    border-radius: 100px;
    font-size: 0.78rem;
    font-weight: 500;
    letter-spacing: 0.02em;
}
.status-ok {
    background: rgba(48, 209, 88, 0.1);
    color: #30d158 !important;
    border: 1px solid rgba(48, 209, 88, 0.2);
    font-weight: 500;
}
.status-err {
    background: rgba(255, 69, 58, 0.1);
    color: #ff453a !important;
    border: 1px solid rgba(255, 69, 58, 0.2);
    font-weight: 500;
}

/* ===== MEMORY ITEMS ===== */
.memory-item {
    background: rgba(255,255,255,0.03);
    border-left: 2px solid rgba(10,132,255,0.4);
    padding: 10px 14px;
    margin: 6px 0;
    border-radius: 0 10px 10px 0;
    font-size: 0.82rem;
    color: #a1a1a6 !important;
    transition: background 0.2s ease;
}
.memory-item:hover {
    background: rgba(255,255,255,0.06);
}

/* ===== REPORT SECTION ===== */
.report-header {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 0.5rem;
}
.report-meta {
    display: flex;
    gap: 20px;
    padding: 12px 0;
    border-bottom: 1px solid rgba(255,255,255,0.06);
    margin-bottom: 1.2rem;
    font-size: 0.85rem;
    color: #86868b;
}
.report-meta span { color: #86868b !important; }
.report-meta strong { color: #f5f5f7 !important; }

/* ===== CODE ===== */
.stApp code {
    color: #64d2ff !important;
    background: rgba(255,255,255,0.06) !important;
    padding: 2px 6px !important;
    border-radius: 6px !important;
    font-size: 0.88em !important;
}

/* ===== DIVIDERS ===== */
.stApp hr {
    border-color: rgba(255,255,255,0.06) !important;
}

/* ===== EXPANDER ===== */
.stApp details {
    background: rgba(28, 28, 30, 0.5) !important;
    border: 1px solid rgba(255,255,255,0.06) !important;
    border-radius: 14px !important;
}
.stApp details summary {
    display: flex !important;
    align-items: center !important;
    padding: 1rem !important;
    list-style-type: none !important; /* Hide native HTML triangle */
}
.stApp details summary::-webkit-details-marker {
    display: none !important; /* Hide Safari/Chrome default triangle */
}
.stApp details summary span {
    color: #a1a1a6 !important;
    font-weight: 500 !important;
}
/* Completely hide Streamlit's custom SVG/text chevron to prevent overlap */
.stApp details summary svg,
.stApp details summary .stIcon {
    display: none !important;
}

/* Hide fallback text like 'arrow_down' if it renders inside the summary text area */
.stApp details summary p {
    margin: 0 !important;
}

/* Ensure only the title text shows up in the summary */
.stApp details summary div[data-testid="stMarkdownContainer"] {
    display: flex !important;
    align-items: center !important;
    font-size: 0.95rem !important;
    color: #a1a1a6 !important;
    visibility: visible !important;
    opacity: 1 !important;
}

/* ===== FOOTER ===== */
.footer-text {
    position: fixed;
    bottom: 0;
    left: 0;
    width: 100%;
    text-align: center;
    color: #636366;
    font-size: 0.78rem;
    letter-spacing: 0.02em;
    padding: 1rem 0;
    background: rgba(0, 0, 0, 0.8);
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
    z-index: 999;
    border-top: 1px solid rgba(255,255,255,0.06);
}
.footer-text a { color: #0a84ff; text-decoration: none; }

/* ===== ANIMATIONS ===== */
@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}
.animate-in {
    animation: fadeInUp 0.6s ease-out;
}

/* ===== ALERT BOXES ===== */
.stApp div[data-testid="stAlert"] {
    background: rgba(28, 28, 30, 0.7) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 14px !important;
    color: #d1d1d6 !important;
}

/* Hide Streamlit branding and sidebar toggle */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
[data-testid="collapsedControl"] {display: none;}
[data-testid="stSidebarCollapseButton"] {display: none;}
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────
# Session State
# ──────────────────────────────────────────────────────────────
if "initialized" not in st.session_state:
    st.session_state.initialized = False
if "rag_pipeline" not in st.session_state:
    st.session_state.rag_pipeline = None
if "memory_manager" not in st.session_state:
    st.session_state.memory_manager = None

# ──────────────────────────────────────────────────────────────
# Cached Initialization
# ──────────────────────────────────────────────────────────────
@st.cache_resource(show_spinner=False)
def initialize_system():
    loader = DataLoader()
    loader.initialize_index()
    loader.ingest_data()
    pipeline = RAGPipeline(vector_client=loader.client, is_local=loader.is_local)
    memory = MemoryManager(vector_client=loader.client, is_local=loader.is_local)
    return pipeline, memory, loader.is_local

# ──────────────────────────────────────────────────────────────
# Sidebar — Clean, minimal
# ──────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🛡️ &nbsp; CyberSentinel AI")
    st.markdown("---")

    # Status
    st.markdown("##### System")
    api_ok = bool(os.getenv("GROQ_API_KEY") or os.getenv("OPENAI_API_KEY"))
    is_local = st.session_state.get("is_local", False)

    col_s1, col_s2 = st.columns(2)
    with col_s1:
        st.markdown(
            f"<span class='status-pill {'status-ok' if api_ok else 'status-err'}'>"
            f"● LLM</span>",
            unsafe_allow_html=True,
        )
    with col_s2:
        st.markdown(
            "<span class='status-pill status-ok'>● Vector DB</span>",
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # Example queries (4 items)
    st.markdown("##### Try These")
    examples = [
        "What is SQL Injection?",
        "Explain CVE-2021-44228",
        "How does phishing work?",
        "MITRE ATT&CK Lateral Movement"
    ]
    sidebar_query = None
    for ex in examples:
        if st.button(f"→ {ex}", key=f"ex_{ex}", use_container_width=True):
            sidebar_query = ex

    st.markdown("---")

    # Recent queries
    st.markdown("##### Recent")
    if st.session_state.memory_manager:
        recent = st.session_state.memory_manager.get_recent_queries(4)
        if recent:
            for item in recent:
                q = item["query"][:50] + ("…" if len(item["query"]) > 50 else "")
                st.markdown(
                    f"<div class='memory-item'>{q}</div>",
                    unsafe_allow_html=True,
                )
        else:
            st.caption("No queries yet")
    else:
        st.caption("Initializing…")

    st.markdown("---")
    if st.button("Clear History", use_container_width=True):
        if st.session_state.memory_manager:
            st.session_state.memory_manager.clear_memory()
            st.rerun()

# ──────────────────────────────────────────────────────────────
# Main Content
# ──────────────────────────────────────────────────────────────

# Hero
st.markdown(
    "<div class='animate-in'>"
    "<h1 class='hero-title'>CyberSentinel AI</h1>"
    "<p class='hero-subtitle'>Threat Intelligence, powered by AI</p>"
    "</div>",
    unsafe_allow_html=True,
)

# Init
if not st.session_state.initialized:
    with st.spinner("Loading knowledge base…"):
        try:
            pipeline, memory, is_local = initialize_system()
            st.session_state.rag_pipeline = pipeline
            st.session_state.memory_manager = memory
            st.session_state.is_local = is_local
            st.session_state.initialized = True
        except Exception as e:
            st.error(f"Initialization failed: {e}")
            st.stop()

# ---- Search Area ----

query = st.text_input(
    "search",
    value=sidebar_query if sidebar_query else "",
    placeholder="Ask anything about cybersecurity…",
    label_visibility="collapsed",
)

col1, col2 = st.columns([1, 4])
with col1:
    search_clicked = st.button("Analyze", type="primary", use_container_width=True)
with col2:
    top_k = st.slider(
        "Sources",
        min_value=1, max_value=5, value=3,
        help="Number of knowledge base entries to retrieve",
    )



# ---- Process Query ----
# Auto-trigger analysis if a sidebar query was clicked
if sidebar_query:
    search_clicked = True
    query = sidebar_query

if search_clicked and query:
    if not (os.getenv("GROQ_API_KEY") or os.getenv("OPENAI_API_KEY")):
        st.error("Please set your GROQ_API_KEY in the .env file.")
        st.stop()

    with st.spinner("Analyzing…"):
        t0 = time.time()

        memory_context = ""
        if st.session_state.memory_manager:
            memory_context = st.session_state.memory_manager.get_relevant_history(query)

        result = st.session_state.rag_pipeline.generate_response(
            query=query, top_k=top_k, memory_context=memory_context,
        )
        elapsed = time.time() - t0

    # ---- Report ----

    st.markdown("### Threat Intelligence Report")

    st.markdown(
        f"<div class='report-meta'>"
        f"<span>⏱ <strong>{elapsed:.1f}s</strong></span>"
        f"<span>📚 <strong>{len(result['sources'])}</strong> sources</span>"
        f"</div>",
        unsafe_allow_html=True,
    )

    st.markdown(result["answer"])

    # Sources
    if result["sources"]:
        st.markdown("---")
        badges = " ".join(
            f"<span class='source-badge'>{src}</span>"
            for src in result["sources"]
        )
        st.markdown(badges, unsafe_allow_html=True)



    # Memory context
    if memory_context:
        with st.expander("Memory context used"):
            st.markdown(memory_context)

    # Store
    if st.session_state.memory_manager:
        st.session_state.memory_manager.store_interaction(query, result["answer"])

elif search_clicked and not query:
    st.warning("Enter a query to get started.")

# ---- Footer ----
st.markdown(
    "<div class='footer-text'>"
    "CyberSentinel AI &nbsp;·&nbsp; "
    "Built with Endee Vector DB &nbsp;·&nbsp; "
    "For educational purposes only"
    "</div>",
    unsafe_allow_html=True,
)
