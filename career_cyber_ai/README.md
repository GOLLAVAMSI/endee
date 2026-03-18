# 🛡️ CyberSentinel AI — Cyber Threat Intelligence Assistant

> **AI-Powered Cybersecurity Assistant using RAG (Retrieval-Augmented Generation) and Endee Vector Database**

An intelligent cybersecurity assistant that answers questions about cyber attacks, vulnerabilities, CVEs, and defense strategies. Built with a production-grade RAG pipeline powered by the **Endee vector database** for high-performance semantic search.

---

## 📋 Repository Setup (Mandatory Steps)

> [!IMPORTANT]
> This project is built on top of a **forked Endee repository** as required by the evaluation criteria.

### Steps Followed:
1. ⭐ **Starred** the official Endee repository → [github.com/endee-io/endee](https://github.com/endee-io/endee)
2. 🍴 **Forked** the repository to personal GitHub account
3. 📁 **Added project files** into the forked repository under `career_cyber_ai/` directory

### Fork Structure:
```
endee/                          ← Forked Endee repository
├── docs/                       ← Original Endee documentation
├── src/                        ← Original Endee source code
├── install.sh                  ← Original Endee build script
├── run.sh                      ← Original Endee run script
├── LICENSE                     ← Apache 2.0 License
├── README.md                   ← Original Endee README
│
└── career_cyber_ai/            ← 🛡️ AI Project (Added)
    ├── app.py                  ← Streamlit frontend
    ├── requirements.txt        ← Python dependencies
    ├── docker-compose.yml      ← Endee server Docker config
    ├── .env.example            ← Environment variables template
    ├── README.md               ← This file (Project README)
    ├── data/
    │   ├── cyber_data.json     ← Knowledge base (42 entries)
    │   └── memory.json         ← User interaction history (auto-created)
    └── modules/
        ├── __init__.py         ← Package exports
        ├── embeddings.py       ← Sentence-transformer embedding engine
        ├── data_loader.py      ← JSON loader + Endee ingestion
        ├── rag_pipeline.py     ← Full RAG pipeline orchestration
        └── memory.py           ← Dual-storage memory manager
```

---

## ✨ Features

| Feature | Description |
|---|---|
| **RAG-Based Query System** | Natural language questions → Vector search → LLM-generated structured answers |
| **Cybersecurity Knowledge Base** | 42 entries covering OWASP Top 10, common attacks, 16 CVEs, MITRE ATT&CK |
| **Attack ↔ Defense Mapping** | Every entry includes description, mechanism, detection, prevention, and tools |
| **Conversation Memory** | Stores past queries (JSON + vector) for personalised, context-aware responses |
| **Streamlit UI** | Dark-themed dashboard with example queries, history sidebar, and source attribution |

---

## 🏗️ System Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                      STREAMLIT UI (app.py)                       │
│   ┌──────────┐   ┌──────────────┐   ┌────────────────────┐      │
│   │ Query    │   │  Response    │   │ Sidebar            │      │
│   │ Input    │──▶│  Display     │   │ • Example Queries  │      │
│   └──────────┘   └──────────────┘   │ • System Status    │      │
│        │                ▲           │ • Recent History    │      │
└────────┼────────────────┼───────────┴────────────────────┘      │
         │                │                                        │
         ▼                │                                        │
┌─────────────────────────┴────────────────────────────────────────┐
│                    RAG PIPELINE (rag_pipeline.py)                 │
│                                                                   │
│   ① User Query                                                    │
│       │                                                           │
│   ② Embed Query  ◄── EmbeddingEngine (all-MiniLM-L6-v2, 384d)   │
│       │                                                           │
│   ③ Vector Search  ◄── Endee DB (cyber_knowledge index)          │
│       │                                                           │
│   ④ Context Assembly  ◄── Top-K results + Memory Context         │
│       │                                                           │
│   ⑤ LLM Generation  ◄── OpenAI GPT-3.5-Turbo                    │
│       │                                                           │
│   ⑥ Structured Response                                          │
└───────────────────────────────────────────────────────────────────┘
         │                │
         ▼                ▼
┌─────────────┐  ┌───────────────┐
│  ENDEE DB   │  │   MEMORY      │
│ (Docker)    │  │ (memory.py)   │
│             │  │               │
│ Indexes:    │  │ • JSON log    │
│ • cyber_    │  │ • Endee index │
│   knowledge │  │   (user_      │
│ • user_     │  │    memory)    │
│   memory    │  │               │
│             │  │ Semantic      │
│ Port: 8080  │  │ retrieval of  │
│ Cosine sim  │  │ past queries  │
│ INT8 quant  │  │               │
└─────────────┘  └───────────────┘
```

---

## 🔍 How Endee Vector Database is Used

Endee is the **core retrieval engine** powering the RAG pipeline. Here's exactly how it's used at every stage:

### 1. Index Creation
```python
from endee import Endee, Precision

client = Endee()
client.set_base_url("http://localhost:8080/api/v1")

client.create_index(
    name="cyber_knowledge",
    dimension=384,            # MiniLM-L6-v2 embedding dimension
    space_type="cosine",      # Cosine similarity for semantic search
    precision=Precision.INT8  # Quantised storage for efficiency
)
```

### 2. Data Ingestion
Each cybersecurity entry is embedded and stored with rich metadata:
```python
index = client.get_index(name="cyber_knowledge")

index.upsert([{
    "id": "cve-2021-44228",
    "vector": [0.12, -0.34, ...],        # 384-dim embedding
    "meta": {
        "title": "CVE-2021-44228 (Log4Shell)",
        "category": "CVE",
        "description": "Critical zero-day in Apache Log4j 2...",
        "how_it_works": "Attacker sends ${jndi:ldap://...}...",
        "detection": "Scan for vulnerable Log4j versions...",
        "prevention": "Update Log4j to 2.17.1+...",
        "tools": "[\"log4j-scan\", \"Nuclei\"]",
        "severity": "Critical"
    }
}])
```

### 3. Semantic Query
User questions are embedded and matched against the knowledge base:
```python
query_vector = embedding_engine.embed_text("What is SQL Injection?")
results = index.query(vector=query_vector, top_k=3)
# Returns top-3 most semantically similar entries with metadata
```

### 4. Memory Storage (Personalisation)
Past user queries are stored in a separate Endee index:
```python
# Separate 'user_memory' index for conversation history
memory_index = client.get_index(name="user_memory")
memory_index.upsert([{
    "id": "uuid-here",
    "vector": query_embedding,
    "meta": {"query": "...", "response": "...", "timestamp": "..."}
}])
# Future queries retrieve similar past interactions to enhance context
```

### Why Endee?
- **High Performance**: Handles up to 1B vectors on a single node
- **Cosine Similarity**: Ideal for semantic text matching
- **INT8 Quantization**: Reduces memory footprint while preserving accuracy
- **Metadata Payloads**: Store rich structured data alongside vectors
- **Simple Python SDK**: Clean `create_index`, `upsert`, `query` API
- **Docker Deployment**: Single command to start (`docker compose up -d`)

---

## 🚀 Setup Instructions

### Prerequisites
- **Python 3.9+**
- **Docker & Docker Compose** (for Endee server)
- **OpenAI API Key** (for LLM generation)
- **Git** (for cloning the forked repository)

### Step 1: Fork & Clone the Repository
```bash
# 1. Star the official Endee repo: https://github.com/endee-io/endee
# 2. Fork it to your GitHub account
# 3. Clone your fork:
git clone https://github.com/YOUR-USERNAME/endee.git
cd endee/career_cyber_ai
```

### Step 2: Start Endee Vector Database
```bash
docker compose up -d
```
Verify it's running: visit `http://localhost:8080` in your browser or run `docker ps`.

### Step 3: Configure Environment
```bash
cp .env.example .env
# Edit .env and add your OpenAI API key:
# OPENAI_API_KEY=sk-your-key-here
```

### Step 4: Install Python Dependencies
```bash
pip install -r requirements.txt
```

### Step 5: Run the Application
```bash
streamlit run app.py
```

The app will automatically:
1. Load the cybersecurity knowledge base from `data/cyber_data.json`
2. Generate embeddings using `all-MiniLM-L6-v2` (runs locally, no API cost)
3. Create the Endee index and ingest all 42 entries
4. Launch the Streamlit UI at `http://localhost:8501`

---

## 💬 Example Inputs & Outputs

### Example 1: "What is SQL Injection?"
**Response includes:**
- 📋 **Overview**: SQL Injection is a code injection technique that exploits vulnerabilities in web application database interaction…
- ⚙️ **How It Works**: Attacker inserts malicious SQL via input fields (e.g., `' OR 1=1 --`)…
- 🔍 **Detection**: WAF with SQLi signatures, database query log monitoring, DAST tools…
- 🛡️ **Prevention**: Parameterized queries, ORM frameworks, input validation, least privilege DB accounts…
- 🔧 **Tools**: SQLMap, Burp Suite, OWASP ZAP, jSQL Injection
- **Sources**: SQL Injection (SQLi), Injection (OWASP A03:2021)

### Example 2: "Explain CVE-2021-44228"
**Response includes:**
- Full Log4Shell breakdown with JNDI lookup exploitation mechanism
- Detection using Yara rules and WAF patterns
- Mitigation: upgrade to Log4j 2.17.1+, set `formatMsgNoLookups=true`
- **Sources**: CVE-2021-44228 (Log4Shell)

### Example 3: "How to prevent ransomware attacks?"
**Response includes:**
- 3-2-1 backup strategy, EDR deployment, network segmentation
- Detection via mass file encryption patterns, shadow copy deletion monitoring
- Tools: CrowdStrike, SentinelOne, Sophos Intercept X
- **Sources**: Ransomware Attacks, MITRE ATT&CK: Execution

---

## 📸 Screenshots

> Screenshots will appear here once the application is running.

| Screen | Description |
|---|---|
| Main Dashboard | Dark-themed query interface with gradient header |
| Threat Report | Structured response with sections and source badges |
| Sidebar | Example queries, system status, and conversation history |

---

## 🛠️ Tech Stack

| Component | Technology |
|---|---|
| **Vector Database** | [Endee](https://github.com/endee-io/endee) (open-source, cosine similarity, INT8 quantization) |
| **Embeddings** | `all-MiniLM-L6-v2` via sentence-transformers (384-dim, runs locally) |
| **LLM** | OpenAI GPT-3.5-Turbo (configurable via `.env`) |
| **Frontend** | Streamlit with custom CSS dark theme |
| **Language** | Python 3.9+ |
| **Containerization** | Docker Compose (for Endee server) |

---

## 📊 Knowledge Base Coverage

| Category | Count | Examples |
|---|---|---|
| **OWASP Top 10** | 7 | Injection, XSS, SSRF, Broken Auth, Security Misconfiguration |
| **Common Attacks** | 9 | SQLi, CSRF, Phishing, DoS/DDoS, Ransomware, Supply Chain |
| **CVE Examples** | 16 | Log4Shell, EternalBlue, Heartbleed, BlueKeep, Zerologon, Spring4Shell |
| **MITRE ATT&CK** | 8 | Initial Access, Execution, Persistence, Lateral Movement, Exfiltration |
| **Total** | **42** | Each with: Description, How It Works, Detection, Prevention, Tools, Severity |

---

## 📄 License

This project is built on top of the [Endee repository](https://github.com/endee-io/endee), licensed under **Apache License 2.0**.

The cybersecurity AI assistant code is for **educational and research purposes only**. Always verify findings with official security advisories and databases.

---

## 🙏 Acknowledgements

- [Endee](https://github.com/endee-io/endee) — High-performance open-source vector database
- [Sentence Transformers](https://www.sbert.net/) — State-of-the-art text embeddings
- [OpenAI](https://openai.com/) — Large language model API
- [Streamlit](https://streamlit.io/) — Rapid Python web app framework
- [MITRE ATT&CK](https://attack.mitre.org/) — Adversary tactics and techniques knowledge base
- [OWASP](https://owasp.org/) — Open Web Application Security Project
