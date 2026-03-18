# ============================================================
# Module: memory.py
# Purpose: Manage user interaction history to provide
#          context-aware, personalised responses.
#          Stores queries in both a local JSON file (for display)
#          and a vector index (for semantic retrieval).
#
#          Supports both Endee and local fallback vector store.
# ============================================================

import json
import os
import uuid
from datetime import datetime

from dotenv import load_dotenv

from modules.embeddings import EmbeddingEngine

load_dotenv()


def _connect_vector_store():
    """Connect to Endee or fall back to local store."""
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


class MemoryManager:
    """
    Dual-storage memory system:
    • **Local JSON** (`data/memory.json`): flat log of all queries and
      responses for quick display in the sidebar.
    • **Vector index** (`user_memory`): vector-indexed queries so we can
      semantically retrieve past interactions relevant to the current
      question and feed them into the RAG prompt.
    """

    INDEX_NAME = "user_memory"

    def __init__(self, vector_client=None, is_local=False):
        self.embedding_engine = EmbeddingEngine()
        if vector_client:
            self.client = vector_client
            self.is_local = is_local
        else:
            self.client, self.is_local = _connect_vector_store()
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

    def _ensure_memory_file(self):
        """Create the memory JSON file if it doesn't exist."""
        os.makedirs(os.path.dirname(self.memory_path), exist_ok=True)
        if not os.path.exists(self.memory_path):
            with open(self.memory_path, "w", encoding="utf-8") as f:
                json.dump([], f)

    def _ensure_memory_index(self):
        """Create the memory vector index if it doesn't exist."""
        try:
            if self.is_local:
                self.client.create_index(
                    name=self.INDEX_NAME,
                    dimension=self.embedding_engine.dimension,
                )
            else:
                from endee import Precision
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
        """
        interaction_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()

        # ---- Local JSON store -----------------------------------------
        memory = self._load_memory()
        interaction = {
            "id": interaction_id,
            "query": query,
            "response": response[:500],
            "timestamp": timestamp,
        }
        memory.append(interaction)
        memory = memory[-100:]
        self._save_memory(memory)

        # ---- Vector store ---------------------------------------------
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
            print(f"[Memory] Warning: Could not store to vector index — {e}")

    def get_relevant_history(self, query: str, top_k: int = 3) -> str:
        """
        Retrieve past interactions that are semantically similar to the
        current query.
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
            return ""

    def get_recent_queries(self, n: int = 10) -> list[dict]:
        """Return the *n* most recent interactions for display in the UI."""
        memory = self._load_memory()
        return memory[-n:][::-1]

    def clear_memory(self):
        """Wipe all stored interactions."""
        self._save_memory([])
        try:
            self.client.delete_index(name=self.INDEX_NAME)
            self._ensure_memory_index()
        except Exception:
            pass
