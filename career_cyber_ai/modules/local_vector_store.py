# ============================================================
# Module: local_vector_store.py
# Purpose: In-memory vector store using numpy for cosine
#          similarity. Used as a fallback when the Endee server
#          is not available so the project can run locally
#          without Docker.
# ============================================================

import json
import numpy as np
from typing import Optional


class LocalVectorStore:
    """
    Lightweight in-memory vector store that mirrors the Endee
    index API (upsert / query) using numpy cosine similarity.

    Used automatically when Endee is unreachable.
    """

    def __init__(self, name: str, dimension: int):
        self.name = name
        self.dimension = dimension
        self.vectors: dict[str, np.ndarray] = {}   # id → vector
        self.metadata: dict[str, dict] = {}         # id → meta

    def upsert(self, records: list[dict]):
        """Insert or update records. Each record must have id, vector, and optionally meta."""
        for record in records:
            rid = record["id"]
            vec = np.array(record["vector"], dtype=np.float32)
            self.vectors[rid] = vec
            self.metadata[rid] = record.get("meta", {})

    def query(self, vector: list[float], top_k: int = 5, **kwargs) -> list[dict]:
        """
        Find the top_k most similar vectors using cosine similarity.

        Returns a list of dicts with keys: id, similarity, meta.
        """
        if not self.vectors:
            return []

        query_vec = np.array(vector, dtype=np.float32)
        query_norm = np.linalg.norm(query_vec)
        if query_norm == 0:
            return []

        similarities = []
        for rid, stored_vec in self.vectors.items():
            stored_norm = np.linalg.norm(stored_vec)
            if stored_norm == 0:
                continue
            sim = float(np.dot(query_vec, stored_vec) / (query_norm * stored_norm))
            similarities.append((rid, sim))

        # Sort by similarity descending, take top_k
        similarities.sort(key=lambda x: x[1], reverse=True)
        results = []
        for rid, sim in similarities[:top_k]:
            results.append({
                "id": rid,
                "similarity": sim,
                "meta": self.metadata.get(rid, {}),
            })
        return results

    def count(self) -> int:
        return len(self.vectors)


class LocalVectorStoreManager:
    """
    Manages multiple LocalVectorStore indexes, mimicking
    the Endee client interface.
    """

    def __init__(self):
        self.indexes: dict[str, LocalVectorStore] = {}

    def create_index(self, name: str, dimension: int, **kwargs):
        if name not in self.indexes:
            self.indexes[name] = LocalVectorStore(name, dimension)

    def get_index(self, name: str) -> LocalVectorStore:
        if name not in self.indexes:
            raise KeyError(f"Index '{name}' not found")
        return self.indexes[name]

    def delete_index(self, name: str):
        self.indexes.pop(name, None)
