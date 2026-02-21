"""
FastAPI server for Real Estate Support Triage Agent.
STEP 1: /chat endpoint — request { message, session_id? }, response { reply }.
"""
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI
from pydantic import BaseModel, Field

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from backend.config import API_HOST, API_PORT


# --- Request/Response for /chat (Step 1) ---
class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    reply: str


# --- Lifespan: init RAG at startup ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        from rag.ingest import ensure_knowledge_base
        ensure_knowledge_base()
    except Exception:
        pass  # RAG optional at startup
    yield


app = FastAPI(title="Real Estate Triage API", lifespan=lifespan)


def _get_reply(message: str, session_id: Optional[str]) -> str:
    """Orchestrator pipeline: classify → retrieve → tool → generate response."""
    try:
        from backend.orchestrator import run_pipeline
        return run_pipeline(message)
    except Exception as e:
        return f"Thank you for your message. We're here to help. (Error: {e})"


@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest) -> ChatResponse:
    """Handle customer chat: classify, retrieve knowledge, return draft reply."""
    reply = _get_reply(req.message, req.session_id)
    return ChatResponse(reply=reply)


@app.get("/health")
async def health():
    return {"status": "ok"}


def main():
    import uvicorn
    uvicorn.run("backend.app:app", host=API_HOST, port=API_PORT, reload=False)


if __name__ == "__main__":
    main()
