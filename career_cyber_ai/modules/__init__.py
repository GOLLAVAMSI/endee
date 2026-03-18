# ============================================================
# Package: modules
# Re-export key classes for convenient imports:
#   from modules import EmbeddingEngine, DataLoader, ...
# ============================================================

from modules.embeddings import EmbeddingEngine
from modules.data_loader import DataLoader
from modules.rag_pipeline import RAGPipeline
from modules.memory import MemoryManager

__all__ = [
    "EmbeddingEngine",
    "DataLoader",
    "RAGPipeline",
    "MemoryManager",
]
