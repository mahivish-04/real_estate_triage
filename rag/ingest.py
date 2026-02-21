"""
STEP 3 — RAG knowledge base.
Load text files from /data, chunk them, generate embeddings, store in ChromaDB.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.config import DATA_DIR, CHROMA_PERSIST_DIR, CHROMA_COLLECTION_NAME
from rag.embeddings import embed_texts

CHUNK_SIZE = 500
CHUNK_OVERLAP = 50


def _load_text_files() -> list[tuple[str, str]]:
    """Load all .txt files from data/; return list of (source_name, content)."""
    if not DATA_DIR.exists():
        return []
    out = []
    for p in DATA_DIR.glob("*.txt"):
        try:
            out.append((p.name, p.read_text(encoding="utf-8", errors="replace")))
        except Exception:
            continue
    return out


def _chunk_text(content: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    """Split content into overlapping chunks (by character)."""
    chunks = []
    start = 0
    while start < len(content):
        end = start + chunk_size
        chunk = content[start:end]
        if chunk.strip():
            chunks.append(chunk.strip())
        start = end - overlap
    return chunks


def _ingest_into_chroma(documents: list[str], metadatas: list[dict], ids: list[str]) -> None:
    """Create or get collection, add embeddings, persist."""
    import chromadb
    from chromadb.config import Settings

    client = chromadb.PersistentClient(path=str(CHROMA_PERSIST_DIR))
    collection = client.get_or_create_collection(
        name=CHROMA_COLLECTION_NAME,
        metadata={"description": "Real estate knowledge chunks"},
    )
    embeddings = embed_texts(documents)
    collection.upsert(ids=ids, documents=documents, metadatas=metadatas, embeddings=embeddings)


def run_ingest() -> int:
    """
    Load data/*.txt, chunk, embed, store in ChromaDB.
    Returns number of chunks ingested.
    """
    pairs = _load_text_files()
    all_chunks = []
    all_metas = []
    chunk_id = 0
    for source_name, content in pairs:
        chunks = _chunk_text(content)
        for i, c in enumerate(chunks):
            all_chunks.append(c)
            all_metas.append({"source": source_name, "chunk_index": i})
            chunk_id += 1
    if not all_chunks:
        return 0
    ids = [f"chunk_{i}" for i in range(len(all_chunks))]
    _ingest_into_chroma(all_chunks, all_metas, ids)
    return len(all_chunks)


def ensure_knowledge_base() -> int:
    """
    Ensure ChromaDB has content. If collection is empty or missing, run ingest.
    Returns number of chunks in knowledge base (after possible ingest).
    """
    import chromadb
    from chromadb.config import Settings

    CHROMA_PERSIST_DIR.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(CHROMA_PERSIST_DIR))
    try:
        coll = client.get_collection(CHROMA_COLLECTION_NAME)
        n = coll.count()
        if n > 0:
            return n
    except Exception:
        pass
    return run_ingest()
