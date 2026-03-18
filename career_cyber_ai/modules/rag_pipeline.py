# ============================================================
# Module: rag_pipeline.py
# Purpose: Orchestrate the full RAG flow:
#          Query → Embed → Vector search → Context
#          assembly → LLM generation → Structured response.
#
#          Supports both Endee and local fallback vector store.
# ============================================================

import os
import json

from openai import OpenAI
from dotenv import load_dotenv

from modules.embeddings import EmbeddingEngine

load_dotenv()

# ---------------------------------------------------------------------------
# System prompt for the cybersecurity assistant.
# ---------------------------------------------------------------------------
SYSTEM_PROMPT = """You are **CyberSentinel AI**, a senior cybersecurity analyst and threat intelligence expert.

Your role is to provide accurate, detailed, and actionable cybersecurity information based on the provided context.

**RULES:**
1. ALWAYS base your answers on the provided context from the knowledge base.
2. If context is available, structure your response with clear sections.
3. Be precise and technical, but explain concepts clearly.
4. Include specific tools, CVE IDs, and MITRE ATT&CK references when relevant.
5. If the context doesn't contain relevant information, say so honestly and provide your best general knowledge.
6. When discussing attacks, ALWAYS include defense/mitigation strategies.

**RESPONSE FORMAT (when applicable):**
- 📋 **Overview**: Brief description of the topic
- ⚙️ **How It Works**: Technical explanation of the mechanism
- 🔍 **Detection Methods**: How to identify this threat
- 🛡️ **Prevention & Mitigation**: Defensive strategies
- 🔧 **Recommended Tools**: Security tools for this area
- ⚠️ **Severity**: Risk level assessment
"""


def _connect_vector_store():
    """
    Connect to Endee if available; otherwise use local fallback.
    """
    host = os.getenv("ENDEE_HOST", "localhost")
    port = os.getenv("ENDEE_PORT", "8080")

    try:
        from endee import Endee
        import urllib.request

        url = f"http://{host}:{port}/api/v1"
        req = urllib.request.Request(url, method="GET")
        urllib.request.urlopen(req, timeout=2)

        client = Endee()
        client.set_base_url(url)
        return client, False
    except Exception:
        from modules.local_vector_store import LocalVectorStoreManager
        return LocalVectorStoreManager(), True


class RAGPipeline:
    """
    End-to-end Retrieval-Augmented Generation pipeline for
    cybersecurity question answering.

    Flow:
        1. Embed the user query
        2. Search vector store for top-k similar entries
        3. Assemble context from retrieved metadata
        4. Send system prompt + context + query to the LLM
        5. Return the generated answer
    """

    INDEX_NAME = "cyber_knowledge"

    def __init__(self, vector_client=None, is_local=False):
        self.embedding_engine = EmbeddingEngine()
        if vector_client:
            self.vector_client = vector_client
            self.is_local = is_local
        else:
            self.vector_client, self.is_local = _connect_vector_store()

        # Use Groq (free tier) with OpenAI-compatible client
        # Get your free key at: https://console.groq.com/keys
        api_key = os.getenv("GROQ_API_KEY", os.getenv("OPENAI_API_KEY", ""))
        base_url = os.getenv("LLM_BASE_URL", "https://api.groq.com/openai/v1")
        self.openai_client = OpenAI(api_key=api_key, base_url=base_url)
        self.llm_model = os.getenv("LLM_MODEL", "llama-3.3-70b-versatile")

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _format_context(results: list) -> str:
        """
        Convert search results into a readable context block
        that can be included in the LLM prompt.
        """
        if not results:
            return "No relevant context found in the knowledge base."

        context_parts = []
        for i, result in enumerate(results, 1):
            meta = result.get("meta", {}) if isinstance(result, dict) else {}
            if not meta and hasattr(result, "meta"):
                meta = result.meta or {}

            title = meta.get("title", "Unknown")
            category = meta.get("category", "")
            description = meta.get("description", "")
            how_it_works = meta.get("how_it_works", "")
            detection = meta.get("detection", "")
            prevention = meta.get("prevention", "")
            tools_raw = meta.get("tools", "[]")
            severity = meta.get("severity", "")

            try:
                tools = json.loads(tools_raw) if isinstance(tools_raw, str) else tools_raw
            except (json.JSONDecodeError, TypeError):
                tools = []

            block = (
                f"--- CONTEXT #{i}: {title} [{category}] ---\n"
                f"Description: {description}\n"
                f"How It Works: {how_it_works}\n"
                f"Detection: {detection}\n"
                f"Prevention: {prevention}\n"
                f"Tools: {', '.join(tools) if tools else 'N/A'}\n"
                f"Severity: {severity}\n"
            )
            context_parts.append(block)

        return "\n".join(context_parts)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def search_knowledge_base(self, query: str, top_k: int = 3) -> list:
        """
        Embed the query and perform a vector similarity search.
        """
        query_vector = self.embedding_engine.embed_text(query)
        index = self.vector_client.get_index(name=self.INDEX_NAME)
        results = index.query(vector=query_vector, top_k=top_k)
        return results

    def generate_response(
        self,
        query: str,
        top_k: int = 3,
        memory_context: str = "",
    ) -> dict:
        """
        Full RAG pipeline: retrieve context, optionally blend in
        memory, then generate a response with the LLM.
        """
        # Step 1 — Retrieve relevant context
        search_results = self.search_knowledge_base(query, top_k=top_k)
        context = self._format_context(search_results)

        # Step 2 — Build the user message
        user_message_parts = [
            f"**User Query:** {query}\n",
            f"**Retrieved Context from Knowledge Base:**\n{context}\n",
        ]
        if memory_context:
            user_message_parts.append(
                f"**Previous Interaction Context (for personalisation):**\n"
                f"{memory_context}\n"
            )
        user_message_parts.append(
            "Please provide a comprehensive, structured answer based "
            "on the above context. If the context is insufficient, "
            "supplement with your general cybersecurity knowledge but "
            "clearly indicate which parts come from the knowledge base "
            "and which are general knowledge."
        )
        user_message = "\n".join(user_message_parts)

        # Step 3 — Call the LLM
        response = self.openai_client.chat.completions.create(
            model=self.llm_model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message},
            ],
            temperature=0.3,
            max_tokens=1500,
        )
        answer = response.choices[0].message.content

        # Step 4 — Extract source titles
        sources = []
        for result in search_results:
            meta = result.get("meta", {}) if isinstance(result, dict) else {}
            if not meta and hasattr(result, "meta"):
                meta = result.meta or {}
            title = meta.get("title", "Unknown Source")
            sources.append(title)

        return {
            "answer": answer,
            "sources": sources,
            "query": query,
        }
