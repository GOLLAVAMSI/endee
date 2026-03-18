# ============================================================
# Module: data_loader.py
# Purpose: Load the cybersecurity knowledge base from JSON and
#          ingest it into the Endee vector database. Handles
#          index creation, text concatenation for embedding,
#          and batch upsert with metadata payloads.
#
#          Falls back to a local in-memory vector store if
#          Endee is not available (no Docker required).
# ============================================================

import json
import os

from dotenv import load_dotenv

from modules.embeddings import EmbeddingEngine

load_dotenv()


def _connect_endee():
    """
    Try to connect to the Endee server. If it's not available,
    fall back to the local in-memory vector store.

    Returns:
        (client, is_local) — the client object and a boolean flag
        indicating whether we're using the local fallback.
    """
    host = os.getenv("ENDEE_HOST", "localhost")
    port = os.getenv("ENDEE_PORT", "8080")

    try:
        from endee import Endee
        import urllib.request

        # Quick connectivity check before using the SDK
        url = f"http://{host}:{port}/api/v1"
        req = urllib.request.Request(url, method="GET")
        urllib.request.urlopen(req, timeout=2)

        client = Endee()
        client.set_base_url(url)
        print("[DataLoader] ✅ Connected to Endee server.")
        return client, False
    except Exception as e:
        print(f"[DataLoader] ⚠️ Endee not available ({e}). Using local vector store.")
        from modules.local_vector_store import LocalVectorStoreManager
        return LocalVectorStoreManager(), True


class DataLoader:
    """
    Responsible for:
    1. Reading cyber_data.json from disk.
    2. Creating (or reusing) an index for the knowledge base.
    3. Embedding each entry's combined text and upserting into the store.
    """

    INDEX_NAME = "cyber_knowledge"

    def __init__(self):
        self.embedding_engine = EmbeddingEngine()
        self.client, self.is_local = _connect_endee()
        self.data_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "data",
            "cyber_data.json",
        )

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _build_document_text(entry: dict) -> str:
        """
        Concatenate the most important text fields of a knowledge-base
        entry into a single string for embedding.  Including all fields
        produces richer, more search-relevant vectors.
        """
        parts = [
            entry.get("title", ""),
            entry.get("category", ""),
            entry.get("description", ""),
            entry.get("how_it_works", ""),
            entry.get("detection", ""),
            entry.get("prevention", ""),
        ]
        # Join tool names as well
        tools = entry.get("tools", [])
        if tools:
            parts.append("Tools: " + ", ".join(tools))
        return " | ".join(filter(None, parts))

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def load_data(self) -> list[dict]:
        """
        Load and return the cybersecurity dataset from the JSON file.

        Returns:
            List of knowledge-base entry dictionaries.

        Raises:
            FileNotFoundError: If cyber_data.json is missing.
        """
        if not os.path.exists(self.data_path):
            raise FileNotFoundError(
                f"Knowledge base not found at {self.data_path}. "
                "Please ensure data/cyber_data.json exists."
            )
        with open(self.data_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data

    def initialize_index(self):
        """
        Create the index for the cybersecurity knowledge base.
        Uses cosine similarity and INT8 precision (when using Endee).

        If the index already exists, this is a no-op.
        """
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
                    dimension=self.embedding_engine.dimension,  # 384
                    space_type="cosine",
                    precision=Precision.INT8,
                )
            print(f"[DataLoader] Created index '{self.INDEX_NAME}'")
        except Exception as e:
            # Index already exists — safe to continue
            if "already exists" in str(e).lower():
                print(f"[DataLoader] Index '{self.INDEX_NAME}' already exists — skipping creation.")
            else:
                raise

    def ingest_data(self) -> int:
        """
        Full ingestion pipeline:
        1. Load JSON dataset.
        2. Generate embeddings for each entry.
        3. Upsert vectors + metadata into the store.

        Returns:
            The number of records ingested.
        """
        data = self.load_data()
        if not data:
            print("[DataLoader] No data to ingest.")
            return 0

        # --- Build combined texts for embedding -------------------------
        texts = [self._build_document_text(entry) for entry in data]

        # --- Batch-embed all texts at once (faster than one-by-one) -----
        print(f"[DataLoader] Embedding {len(texts)} knowledge-base entries …")
        vectors = self.embedding_engine.embed_batch(texts)

        # --- Prepare upsert payloads ------------------------------------
        records = []
        for entry, vector in zip(data, vectors):
            records.append(
                {
                    "id": entry["id"],
                    "vector": vector,
                    "meta": {
                        "title": entry.get("title", ""),
                        "category": entry.get("category", ""),
                        "description": entry.get("description", ""),
                        "how_it_works": entry.get("how_it_works", ""),
                        "detection": entry.get("detection", ""),
                        "prevention": entry.get("prevention", ""),
                        "tools": json.dumps(entry.get("tools", [])),
                        "severity": entry.get("severity", ""),
                    },
                }
            )

        # --- Upsert in batches of 50 ------------------------------------
        index = self.client.get_index(name=self.INDEX_NAME)
        batch_size = 50
        for i in range(0, len(records), batch_size):
            batch = records[i : i + batch_size]
            index.upsert(batch)
            print(f"[DataLoader] Upserted batch {i // batch_size + 1} "
                  f"({len(batch)} records)")

        backend = "local store" if self.is_local else "Endee"
        print(f"[DataLoader] ✅ Ingested {len(records)} records into {backend}.")
        return len(records)
