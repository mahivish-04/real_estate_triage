"""
STEP 5 — Orchestrator pipeline.
1. Classify message
2. Retrieve context (RAG)
3. Choose tool by intent
4. Execute tool
5. Generate response (LLM)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from agent.classifier import classify
from agent.tools import (
    fetch_documents,
    generate_receipt,
    knowledge_search,
    schedule_visit,
)
from agent.responder import generate_reply
from rag.retriever import retrieve

# Intent → tool (decision mapping)
INTENT_TO_TOOL = {
    "schedule_visit": "schedule_visit",
    "payment": "generate_receipt",
    "documents": "fetch_documents",
    "inquiry": "knowledge_search",
    "complaint": "knowledge_search",  # use RAG for policy/process context
}


def run_pipeline(message: str) -> str:
    """
    Full pipeline: classify → retrieve → choose tool → execute → generate reply.
    Returns the final reply string.
    """
    # 1. Classify
    triage = classify(message)
    intent = triage.get("intent", "inquiry")
    urgency = triage.get("urgency", "medium")
    entities = triage.get("entities") or {}

    # 2. Retrieve context (RAG)
    chunks = retrieve(message, top_k=5)
    context = "\n\n".join(chunks) if chunks else ""

    # 3. Choose tool
    tool_name = INTENT_TO_TOOL.get(intent, "knowledge_search")

    # 4. Execute tool (no LLM)
    if tool_name == "schedule_visit":
        tool_output = schedule_visit(entities)
    elif tool_name == "fetch_documents":
        tool_output = fetch_documents(entities)
    elif tool_name == "generate_receipt":
        tool_output = generate_receipt(entities)
    else:
        tool_output = knowledge_search(message)

    # 5. Generate response (LLM)
    reply = generate_reply(
        message=message,
        intent=intent,
        urgency=urgency,
        entities=entities,
        context=context,
        tool_output=tool_output,
    )
    return reply
