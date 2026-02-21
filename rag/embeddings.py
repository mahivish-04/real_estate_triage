"""
Embedding model wrapper using sentence-transformers for ChromaDB compatibility.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.config import EMBEDDING_MODEL

_model = None


def get_embedding_model():
    """Lazy-load sentence-transformers model."""
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer(EMBEDDING_MODEL)
    return _model


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Return list of embedding vectors for the given texts."""
    model = get_embedding_model()
    return model.encode(texts, convert_to_numpy=True).tolist()


def embed_query(query: str) -> list[float]:
    """Return single embedding vector for a query string."""
    return embed_texts([query])[0]
