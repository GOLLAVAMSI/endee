# 🛡️ CyberSentinel AI

**CyberSentinel AI** is an intelligent, completely local cybersecurity threat intelligence assistant powered by **Retrieval-Augmented Generation (RAG)** and the **Endee Vector Database**.

This project provides an interactive chat platform designed for security engineers, analysts, and students to quickly get highly accurate, context-aware information about vulnerabilities, CVEs, exploits, and defense mechanisms based on a curated threat intelligence database.

---

## 🌟 Key Features
- **Semantic RAG Engine:** Instead of looking for exact keyword matches, the AI understands the *semantic meaning* of your questions and searches the vector database for identical contexts.
- **Premium Apple-inspired UI:** A clean, modern dark mode interface built with Streamlit, completely removing default Streamlit branding for a production-ready application feel.
- **Lightning Fast LLM:** Powered by **Groq** integration running Llama 3 (70B/8B parameters), providing instant intelligent report generation.
- **Local Fallback Mode:** If the Endee Vector Database API is unavailable, the application gracefully constructs an in-memory NumPy/JSON vector store running entirely on your local machine using the `all-MiniLM-L6-v2` embedding model.
- **Contextual Memory:** conversational history is tracked, embedded, and injected into the prompt so the AI remembers what you previously asked it.

---

## 🏗️ System Architecture

1. **User Interface (`app.py`)**: A Streamlit application rendering the glassmorphism dark theme and handling the UI state.
2. **Data Ingestion (`data_loader.py`)**: Reads the raw intelligence from `data/cyber_data.json` and converts the data payloads into high-dimensional vectors.
3. **Vector Database (`local_vector_store.py`)**: Stores the data chunks mathematically so semantic search operations (Cosine Similarity) can quickly locate the most relevant threat intel.
4. **LLM Controller (`rag_pipeline.py`)**: Packages the user query, conversational history, and the vector DB context, sending it to the Groq LLM API.

> Note: Detailed line-by-line code documentation can be found in `PROJECT_EXPLANATION.txt`.

---

## 💻 Installation & Setup

### 1. Requirements
Ensure you have Python 3.9+ installed.

### 2. Clone the Repository
```bash
git clone https://github.com/GOLLAVAMSI/endee.git
cd endee/career_cyber_ai
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configuration
You must provide an API key to the LLM backend. Rename `.env.example` to `.env` or create a new `.env` file in the `career_cyber_ai` folder with your Groq API key:
```env
# Create a free account at https://console.groq.com/keys
GROQ_API_KEY=your_groq_api_key_here

LLM_BASE_URL=https://api.groq.com/openai/v1
LLM_MODEL=llama3-70b-8192
```

### 5. Run the Application
Start the Streamlit Web Application:
```bash
streamlit run app.py
```
Open your browser to `http://localhost:8501`.

---

## 🧠 Example Queries
You can try asking the assistant questions like:
- *"What is SQL Injection?"*
- *"Explain CVE-2021-44228 (Log4Shell)"*
- *"How does Lateral Movement work in the MITRE ATT&CK framework?"*
- *"What are the best practices for preventing ransomware attacks?"*

---

## 📂 Project Structure
```text
career_cyber_ai/
│
├── app.py                      # Main Streamlit User Interface
├── requirements.txt            # Python Dependencies
├── .env                        # Environment keys (not tracked in Git)
├── PROJECT_EXPLANATION.txt     # Complete architecture and line-by-line code explanation
│
├── data/
│   └── cyber_data.json         # Simulated curated threat intelligence dataset
│
└── modules/                    # Application Core Logic
    ├── __init__.py
    ├── data_loader.py          # Data ingestion engine
    ├── embeddings.py           # Text embedding wrapper logic
    ├── local_vector_store.py   # Vector mathematics and NumPy storage handler
    ├── memory.py               # Memory context management
    └── rag_pipeline.py         # Retrieves context and generates the LLM response
```

---

*This project was built for educational and demonstration purposes using open-source tools and the Endee Vector Database ecosystem.*
