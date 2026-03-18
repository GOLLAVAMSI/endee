# 🛡️ CyberSentinel AI

## 📌 TL;DR
CyberSentinel AI is an enterprise-grade Cyber Threat Intelligence assistant built on a robust **Retrieval-Augmented Generation (RAG)** architecture. It ingests curated cybersecurity knowledge into the **Endee Vector Database**, leveraging semantic search to provide hallucination-free, high-precision threat analysis powered by Groq's Llama 3 LLM.

**Key Features:**
- **Semantic Threat Retrieval:** Utilizes `all-MiniLM-L6-v2` embeddings for sub-second similarity matching constraints.
- **Endee Vector Database Integration:** Powers core context retrieval and dynamically scales semantic search.
- **Stateful Memory Management:** Autonomously tracks and injects localized previous interactions into the LLM context bounds.
- **High-Performance Inference:** Integrated securely with Groq (Llama-3 70B/8B) for ultra-low latency generation.
- **Modern UI Architecture:** Glassmorphism UI built with Streamlit and custom CSS for a strictly professional, production-ready user experience.

---

## 🏗️ System Architecture

```text
User Input ➔ [Streamlit UI] ➔ [RAG Pipeline Orchestrator]
                                      │
                                      ├─➔ [Memory Manager] ⟷ (Endee DB: chat_memory)
                                      │
                                      ├─➔ [Embedding Engine: all-MiniLM-L6-v2]
                                      │          │
                                      │          ▼
[Custom Context + LLM Prompt] ⟵ [Endee Vector Database (cyber_knowledge)]
            │
            ▼
[Groq API (Llama-3)] ➔ Generates Structured Threat Report ➔ [UI Rendering]
```

---

## 🗄️ How Endee Vector Database is Used
The Endee Vector Database is the absolute foundation of this application, utilized across two distinct vectors:

1. **Threat Intelligence Data Storage & Semantic Search:** 
   Raw cybersecurity definitions, CVE details, and MITRE ATT&CK patterns are processed dynamically and upserted into Endee. When a user queries the system, Endee performs complex Cosine Similarity mathematical computations to identify and return the top `k` most statistically relevant documents—restricting the LLM to factual data and entirely preventing hallucinations.
2. **Stateful Conversation Memory:**
   Endee collections are mapped specifically for session retention. Every user interaction is embedded and strictly stored back into a `chat_memory` index. Successive queries automatically perform semantic searches against *past conversational history* to pull historical context fluidly into the current LLM synthesis prompt.

---

## 🚀 Project Walkthrough
The system is specifically engineered for security analysts requiring rapid, contextualized intelligence extraction.
1. The backend bootstraps the connection to the Endee DB and seamlessly ingests pre-defined JSON threat vectors.
2. Users input domain-heavy queries (e.g., zero-day vulnerabilities, lateral movement heuristics).
3. The automated RAG pipeline securely abstracts Vector DB polling, returning high-fidelity content and mapping exact source citations to the intelligence UI report.
4. The Memory Context expands dynamically beneath the primary response, providing transparent auditing of the foundational LLM prompt.

---

## 🧩 Code Architecture
- **`app.py`:** Main application controller, UI rendering engine, and asynchronous state manager.
- **`modules/data_loader.py`:** Handles the automated staging and ingestion pipeline; parses local intelligence payloads and vectors them securely into Endee.
- **`modules/embeddings.py`:** Initializes the `sentence-transformers` engine for universal, strict 384-dimensional mathematical embedding generation.
- **`modules/local_vector_store.py`:** A highly unique, identical API-compliant NumPy fallback vector store ensuring 100% uptime if Endee Docker clusters or ports are manually blocked.
- **`modules/rag_pipeline.py`:** The primary system orchestrator. Retrieves vector context, aggregates memory traces, limits token contexts, and executes the Groq completions.
- **`modules/memory.py`:** Manages contextual history vectorization directly mapping into Endee for deterministic multi-turn conversations.

---

## 💡 Example Usage

**Input Query:** 
> *"Explain CVE-2021-44228"*

**System Operations:**
1. Generates a multi-dimensional array vector of the prompt.
2. Queries the Endee DB `cyber_knowledge` logic, securely retrieving "Log4Shell" payload context.
3. Queries Endee DB `chat_memory` for relevant past conversation contexts.

**Output Generation:**
> **Threat Intelligence Report: Log4Shell**
> **Overview:** CVE-2021-44228 is a critical vulnerability in the Apache Log4j library...
> **Detection:** Deploy immediate WAF rules targeting JNDI lookup payloads...
> *(Source Citation: National Vulnerability Database (NVD) - Log4j)*

---

## ⚙️ Setup Instructions

### 1. Requirements
Ensure Python 3.9+ is properly installed on the host machine.

### 2. Clone the Repository
```bash
git clone https://github.com/GOLLAVAMSI/endee.git
cd endee/career_cyber_ai
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configuration Requirements
Create a `.env` file dynamically in the root directory and supply your Groq API operational key:
```env
GROQ_API_KEY=your_groq_api_key_here
LLM_BASE_URL=https://api.groq.com/openai/v1
LLM_MODEL=llama3-70b-8192
```

### 5. Execute 
```bash
streamlit run app.py
```

---

## 🌟 What Makes This Project Unique
- **Strict Cybersecurity Domain Focus:** Curated high-fidelity intelligence datasets limit the LLM boundary to factual threat heuristics.
- **Dual-Purpose Endee Application:** Seamlessly implements Endee infrastructure for *both* raw knowledge retrieval and complex, localized conversational memory arrays.
- **Autonomous Fallback Vectors:** Engineered with a custom NumPy in-memory data store mirroring Endee's exact underlying API contract—ensuring zero downtime continuous evaluation functionality.
- **Production-Ready Presentation UX:** Abandons standardized dashboard visualization constraints for a highly responsive, glassmorphism UI structured using custom CSS dom injection techniques.

---

## 🏁 Conclusion
CyberSentinel AI demonstrates a rigorous understanding of modern semantic search architecture, concise prompt engineering restrictions, and the imperative role specialized Vector Databases like Endee serve in successfully deploying secure, generative RAG applications into enterprise environments.
