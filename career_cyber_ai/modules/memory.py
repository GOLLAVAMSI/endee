# ============================================================
# Module: memory.py
# Purpose: Manage user interaction history to provide
#          context-aware, personalised responses.
#          Stores queries in both a local JSON file (for display)
#          and an Endee vector index (for semantic retrieval).
# ============================================================

import json
import os
import uuid
from datetime import datetime

from endee import Endee, Precision
from dotenv import load_dotenv

from modules.embeddings import EmbeddingEngine

load_dotenv()


class MemoryManager:
    """
    Dual-storage memory system:
    • **Local JSON** (`data/memory.json`): flat log of all queries and
      responses for quick display in the sidebar.
    • **Endee index** (`user_memory`): vector-indexed queries so we can
      semantically retrieve past interactions relevant to the current
      question and feed them into the RAG prompt.
    """

    INDEX_NAME = "user_memory"

    def __init__(self):
        self.embedding_engine = EmbeddingEngine()
        self.client = self._connect_endee()
        self.memory_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "data",
            "memory.json",
        )
        self._ensure_memory_file()
        self._ensure_memory_index()

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _connect_endee(self) -> Endee:
        host = os.getenv("ENDEE_HOST", "localhost")
        port = os.getenv("ENDEE_PORT", "8080")
        client = Endee()
        client.set_base_url(f"http://{host}:{port}/api/v1")
        return client

    def _ensure_memory_file(self):
        """Create the memory JSON file if it doesn't exist."""
        os.makedirs(os.path.dirname(self.memory_path), exist_ok=True)
        if not os.path.exists(self.memory_path):
            with open(self.memory_path, "w", encoding="utf-8") as f:
                json.dump([], f)

    def _ensure_memory_index(self):
        """Create the Endee memory index if it doesn't exist."""
        try:
            self.client.create_index(
                name=self.INDEX_NAME,
                dimension=self.embedding_engine.dimension,
                space_type="cosine",
                precision=Precision.INT8,
            )
        except Exception as e:
            if "already exists" not in str(e).lower():
                raise

    def _load_memory(self) -> list[dict]:
        """Read the full interaction log from disk."""
        try:
            with open(self.memory_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def _save_memory(self, data: list[dict]):
        """Persist the interaction log to disk."""
        with open(self.memory_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def store_interaction(self, query: str, response: str):
        """
        Save a user interaction (query + AI response) to both storage
        backends.

        1. Append to the local JSON log.
        2. Embed the query and upsert into the Endee user_memory index
           so future queries can semantically retrieve relevant past
           interactions.
        """
        interaction_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()

        # ---- Local JSON store -----------------------------------------
        memory = self._load_memory()
        interaction = {
            "id": interaction_id,
            "query": query,
            "response": response[:500],  # Truncate long responses
            "timestamp": timestamp,
        }
        memory.append(interaction)
        # Keep only the last 100 interactions to avoid unbounded growth
        memory = memory[-100:]
        self._save_memory(memory)

        # ---- Endee vector store ---------------------------------------
        try:
            query_vector = self.embedding_engine.embed_text(query)
            index = self.client.get_index(name=self.INDEX_NAME)
            index.upsert(
                [
                    {
                        "id": interaction_id,
                        "vector": query_vector,
                        "meta": {
                            "query": query,
                            "response": response[:300],
                            "timestamp": timestamp,
                        },
                    }
                ]
            )
        except Exception as e:
            # Memory storage is best-effort; don't crash the app
            print(f"[Memory] Warning: Could not store to Endee — {e}")

    def get_relevant_history(self, query: str, top_k: int = 3) -> str:
        """
        Retrieve past interactions that are semantically similar to the
        current query.  The returned string can be injected into the RAG
        prompt for personalised / context-aware answers.

        Args:
            query:  The current user question.
            top_k:  Number of past interactions to retrieve.

        Returns:
            A formatted string of relevant past interactions, or an
            empty string if none are found.
        """
        try:
            query_vector = self.embedding_engine.embed_text(query)
            index = self.client.get_index(name=self.INDEX_NAME)
            results = index.query(vector=query_vector, top_k=top_k)

            if not results:
                return ""

            history_parts = []
            for result in results:
                meta = result.get("meta", {}) if isinstance(result, dict) else {}
                if not meta and hasattr(result, "meta"):
                    meta = result.meta or {}

                past_query = meta.get("query", "")
                past_response = meta.get("response", "")
                if past_query:
                    history_parts.append(
                        f"• Previous Q: {past_query}\n  Previous A: {past_response}"
                    )

            return "\n".join(history_parts) if history_parts else ""
        except Exception:
            # Graceful degradation: return empty if Endee is unreachable
            return ""

    def get_recent_queries(self, n: int = 10) -> list[dict]:
        """
        Return the *n* most recent interactions for display in the UI.

        Returns:
            List of dicts with keys: id, query, response, timestamp.
        """
        memory = self._load_memory()
        return memory[-n:][::-1]  # Most recent first

    def clear_memory(self):
        """
        Wipe all stored interactions from both local JSON and Endee.
        Useful for privacy or resetting the assistant.
        """
        self._save_memory([])
        try:
            # Re-create the memory index (quickest way to clear vectors)
            self.client.delete_index(name=self.INDEX_NAME)
            self._ensure_memory_index()
        except Exception:
            pass
