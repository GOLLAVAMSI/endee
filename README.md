# CyberSentinel AI
### Enterprise Cyber Threat Intelligence via Semantic RAG 

CyberSentinel AI is a specialized **Retrieval-Augmented Generation (RAG)** application engineered for cybersecurity analysis. Powered by the **Endee Vector Database** and **Groq (Llama-3)**, it instantly retrieves and synthesizes high-fidelity threat intelligence (such as CVE reports and MITRE ATT&CK patterns) into actionable, hallucination-free intelligence reports.

---

### 🔑 Key Features
* **Zero-Hallucination Retrieval:** Forces the LLM to strictly cite intelligence documents from the underlying Vector Database.
* **Persistent Conversation Memory:** Automatically embeds tracking vectors of previous conversations directly into Endee to allow multi-turn, stateful chat context.
* **Intelligent Fallback Architecture:** Features an API-compliant, local NumPy vector store ensuring 100% operational uptime dynamically—even if Endee's Docker container goes offline.
* **Modern Interface:** A highly-performant, responsive glassmorphism UI built entirely out of overridden Streamlit CSS components.

---

### 🧠 Endee Vector Database Integration
The Endee Vector Database serves as the central orchestration engine for the entire semantic search pipeline. It acts in two critical roles:
1. **Intelligence Index (`cyber_knowledge`):** The application autonomously maps JSON threat data into 384-dimensional mathematical arrays via `sentence-transformers`, upserting them alongside metadata into Endee. When users request threat heuristics, Endee's aggressive Sub-second Cosine Similarity querying restricts LLM answers to exact, retrieved context boundaries.
2. **Context Memory Index (`chat_memory`):** To solve LLM token limits, this application creates a secondary Endee index specifically to store previous user-interactions as standalone embedded documents, retrieving them dynamically for accurate conversational flow.

---

### 💻 System Deployment

**1. Clone the repository**
```bash
git clone https://github.com/GOLLAVAMSI/endee.git
cd endee/career_cyber_ai
```

**2. Install runtime dependencies**
```bash
pip install -r requirements.txt
```

**3. Inject Environment Keys**
Rename or create a `.env` file in the project root with your high-speed Groq API key:
```ini
GROQ_API_KEY=your_key_here
LLM_BASE_URL=https://api.groq.com/openai/v1
LLM_MODEL=llama3-70b-8192
```

**4. Execute the Application**
```bash
streamlit run app.py
```

---

### 📂 Codebase Architecture 
* **`app.py`:** The primary routing and UI rendering handler.
* **`modules/data_loader.py`:** Automated ingestion pipeline routing local databases arrays directly into the Endee DB container parameters.
* **`modules/rag_pipeline.py`:** The main orchestrator connecting semantic vectors from Endee to the Llama-3 parsing architecture. 
* **`modules/embeddings.py`:** Standardized embedding payload generator using `all-MiniLM-L6-v2`.
* **`modules/memory.py`:** Specialized abstraction layer storing session interaction hashes securely in the secondary Endee collection.
* **`modules/local_vector_store.py`:** Hardened fail-safes replicating Endee's Python API SDK entirely in local RAM utilizing `numpy.dot`.

---

**Built specifically for the Endee.io Assessment**
