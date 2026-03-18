# ============================================================
# Module: embeddings.py
# Purpose: Generate vector embeddings from text using
#          sentence-transformers (all-MiniLM-L6-v2, 384-dim).
#          Provides a singleton EmbeddingEngine for efficient
#          model loading and reuse across the application.
# ============================================================

import os
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------------------------
# Singleton pattern: only one model instance per process to avoid
# loading the ~80 MB model multiple times in memory.
# ---------------------------------------------------------------------------
_model_instance = None


def _get_model():
    """
    Return the shared SentenceTransformer model instance.
    Loads the model on first call; reuses it on subsequent calls.
    """
    global _model_instance
    if _model_instance is None:
        model_name = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
        _model_instance = SentenceTransformer(model_name)
    return _model_instance


class EmbeddingEngine:
    """
    Wrapper around SentenceTransformer for generating embeddings.

    Usage:
        engine = EmbeddingEngine()
        vec = engine.embed_text("What is SQL Injection?")
        vecs = engine.embed_batch(["text1", "text2"])
    """

    def __init__(self):
        self.model = _get_model()
        # Dimension of the embedding vectors (384 for MiniLM-L6-v2)
        self.dimension = self.model.get_sentence_embedding_dimension()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def embed_text(self, text: str) -> list[float]:
        """
        Convert a single text string into a dense vector embedding.

        Args:
            text: Input text to embed.

        Returns:
            A list of floats representing the embedding vector.
        """
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding.tolist()

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """
        Convert a batch of texts into embedding vectors.
        Batch encoding is significantly faster than encoding one-by-one
        because it leverages GPU/CPU parallelism internally.

        Args:
            texts: List of input texts.

        Returns:
            A list of embedding vectors (each a list of floats).
        """
        embeddings = self.model.encode(texts, convert_to_numpy=True, show_progress_bar=True)
        return embeddings.tolist()
