"""
STEP 4 — Deterministic business tools. No LLM calls.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Type for entities dict from classifier
EntitiesDict = dict[str, str]


def schedule_visit(entities: EntitiesDict) -> str:
    """
    Returns booking confirmation text. Deterministic, no LLM.
    Asks for clarification when date or time is missing (no hallucinated data).
    """
    flat_id = (entities.get("flat_id") or "").strip()
    tower = (entities.get("tower") or "").strip()
    date = (entities.get("date") or "").strip()
    time = (entities.get("time") or "").strip()
    missing = []
    if not date:
        missing.append("preferred date")
    if not time:
        missing.append("preferred time")
    if missing:
        return (
            "To schedule your site visit we need a few details. "
            f"Please share: {', '.join(missing)}. "
            "You can also mention your flat number and tower if relevant."
        )
    flat_id = flat_id or "—"
    tower = tower or "—"
    return (
        f"Your site visit has been scheduled.\n"
        f"Tower: {tower} | Flat: {flat_id} | Date: {date} | Time: {time}\n"
        f"Confirmation reference: SV-{abs(hash((tower, flat_id, date, time))) % 100000:05d}. "
        f"You will receive an SMS/email shortly. For changes, please contact us 24 hours in advance."
    )


def fetch_documents(entities: EntitiesDict) -> str:
    """
    Returns document links text. Deterministic, no LLM.
    Asks for clarification when flat_id is missing (no hallucinated data).
    """
    flat_id = (entities.get("flat_id") or "").strip()
    tower = (entities.get("tower") or "").strip()
    if not flat_id:
        return (
            "To fetch your property documents we need your flat/unit number. "
            "Please share your flat ID (e.g. A-203, 101). Tower or block name is optional but helpful."
        )
    tower = tower or "—"
    base = "https://portal.example.com/documents"
    return (
        f"Document links for Flat {flat_id}, Tower {tower}:\n"
        f"• Sale deed: {base}/sale-deed?flat={flat_id}\n"
        f"• Occupancy certificate: {base}/oc?flat={flat_id}\n"
        f"• Tax receipts: {base}/tax?flat={flat_id}\n"
        f"Login to the customer portal for full list. Contact support if any link fails."
    )


def generate_receipt(entities: EntitiesDict) -> str:
    """
    Returns receipt message. Deterministic, no LLM.
    Asks for clarification when flat_id is missing (no hallucinated data).
    """
    flat_id = (entities.get("flat_id") or "").strip()
    tower = (entities.get("tower") or "").strip()
    if not flat_id:
        return (
            "To generate or resend your payment receipt we need your flat/unit number. "
            "Please share your flat ID (e.g. A-203) so we can look up your payment records."
        )
    tower = tower or "—"
    ref = f"RCP-{abs(hash((flat_id, tower))) % 100000:05d}"
    return (
        f"Receipt generated for your records.\n"
        f"Reference: {ref} | Flat: {flat_id} | Tower: {tower}\n"
        f"Receipts are sent to your registered email within 3 working days. "
        f"For duplicate or correction, quote reference {ref} to accounts."
    )


def knowledge_search(query: str) -> str:
    """
    Returns RAG context (top 5 chunks). No LLM — uses retriever only.
    """
    from rag.retriever import retrieve
    chunks = retrieve(query, top_k=5)
    if not chunks:
        return "No matching knowledge base entries found for your query."
    return "\n\n".join(chunks)
