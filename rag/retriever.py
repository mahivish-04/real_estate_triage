"""
Semantic search over ChromaDB. Returns top-k context chunks.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.config import CHROMA_PERSIST_DIR, CHROMA_COLLECTION_NAME
from rag.embeddings import embed_query


def retrieve(query: str, top_k: int = 5) -> list[str]:
    """
    Run semantic search; return top_k document chunks (list of strings).
    Returns empty list if collection missing or query fails.
    """
    try:
        import chromadb
        client = chromadb.PersistentClient(path=str(CHROMA_PERSIST_DIR))
        collection = client.get_collection(CHROMA_COLLECTION_NAME)
        n = collection.count()
        if n == 0:
            return []
        q_embedding = embed_query(query)
        results = collection.query(query_embeddings=[q_embedding], n_results=min(top_k, n))
        # results["documents"] is list of lists (one row per query)
        docs = results.get("documents") or []
        if docs and len(docs) > 0:
            return list(docs[0])
        return []
    except Exception:
        return []
