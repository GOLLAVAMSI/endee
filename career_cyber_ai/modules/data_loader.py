# ============================================================
# Module: data_loader.py
# Purpose: Load the cybersecurity knowledge base from JSON and
#          ingest it into the Endee vector database. Handles
#          index creation, text concatenation for embedding,
#          and batch upsert with metadata payloads.
# ============================================================

import json
import os

from endee import Endee, Precision
from dotenv import load_dotenv

from modules.embeddings import EmbeddingEngine

load_dotenv()


class DataLoader:
    """
    Responsible for:
    1. Reading cyber_data.json from disk.
    2. Creating (or reusing) an Endee index for the knowledge base.
    3. Embedding each entry's combined text and upserting into Endee.
    """

    INDEX_NAME = "cyber_knowledge"

    def __init__(self):
        self.embedding_engine = EmbeddingEngine()
        self.client = self._connect_endee()
        self.data_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "data",
            "cyber_data.json",
        )

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _connect_endee(self) -> Endee:
        """
        Create and return an Endee client connected to the local server.
        Reads host/port from environment variables with sensible defaults.
        """
        host = os.getenv("ENDEE_HOST", "localhost")
        port = os.getenv("ENDEE_PORT", "8080")

        client = Endee()
        client.set_base_url(f"http://{host}:{port}/api/v1")
        return client

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
        Create the Endee index for the cybersecurity knowledge base.
        Uses cosine similarity and INT8 precision (quantised storage)
        for a good balance of accuracy and memory efficiency.

        If the index already exists, this is a no-op.
        """
        try:
            self.client.create_index(
                name=self.INDEX_NAME,
                dimension=self.embedding_engine.dimension,  # 384
                space_type="cosine",
                precision=Precision.INT8,
            )
            print(f"[DataLoader] Created Endee index '{self.INDEX_NAME}'")
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
        3. Upsert vectors + metadata into Endee.

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

        # --- Upsert into Endee in batches of 50 -------------------------
        index = self.client.get_index(name=self.INDEX_NAME)
        batch_size = 50
        for i in range(0, len(records), batch_size):
            batch = records[i : i + batch_size]
            index.upsert(batch)
            print(f"[DataLoader] Upserted batch {i // batch_size + 1} "
                  f"({len(batch)} records)")

        print(f"[DataLoader] ✅ Ingested {len(records)} records into Endee.")
        return len(records)
