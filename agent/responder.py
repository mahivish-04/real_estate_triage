"""
STEP 6 — Response generation. LLM produces professional, concise reply from
original message, triage output, retrieved context, and tool output.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from langchain_core.messages import HumanMessage, SystemMessage

from agent.llm_factory import get_llm
from agent.prompts import RESPONDER_SYSTEM, RESPONDER_USER


def generate_reply(
    message: str,
    intent: str,
    urgency: str,
    entities: dict[str, str],
    context: str,
    tool_output: str,
) -> str:
    """
    Generate final response using LLM. Professional and concise.
    """
    flat_id = entities.get("flat_id") or ""
    tower = entities.get("tower") or ""
    date = entities.get("date") or ""
    time = entities.get("time") or ""
    user_prompt = RESPONDER_USER.format(
        message=message,
        intent=intent,
        urgency=urgency,
        flat_id=flat_id,
        tower=tower,
        date=date,
        time=time,
        context=context or "(none)",
        tool_output=tool_output or "(none)",
    )
    llm = get_llm()
    response = llm.invoke([
        SystemMessage(content=RESPONDER_SYSTEM),
        HumanMessage(content=user_prompt),
    ])
    text = response.content if hasattr(response, "content") else str(response)
    return (text or "Thank you for contacting us. We will assist you shortly.").strip()
