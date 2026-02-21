"""
STEP 2 — Classification + NER using LLM.
Returns structured JSON: intent, urgency, entities (flat_id, tower, date, time).
The model is forced to return valid JSON via LangChain structured output.
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pydantic import BaseModel, Field

from langchain_core.messages import HumanMessage, SystemMessage

from agent.llm_factory import get_llm
from agent.prompts import CLASSIFY_SYSTEM, get_classify_prompt


# Pydantic model matching required JSON shape (forces valid JSON from LLM)
class ClassificationEntities(BaseModel):
    flat_id: str = ""
    tower: str = ""
    date: str = ""
    time: str = ""


class ClassificationResult(BaseModel):
    intent: str = Field(..., description="One of: schedule_visit, documents, payment, complaint, inquiry")
    urgency: str = Field(..., description="One of: high, medium, low")
    entities: ClassificationEntities = Field(default_factory=ClassificationEntities)


def classify(message: str) -> dict:
    """
    Classify customer message. Returns dict:
    { "intent": str, "urgency": str, "entities": { "flat_id", "tower", "date", "time" } }
    """
    llm = get_llm()
    # Force structured JSON output
    try:
        structured_llm = llm.with_structured_output(ClassificationResult)
        out = structured_llm.invoke([
            SystemMessage(content=CLASSIFY_SYSTEM),
            HumanMessage(content=get_classify_prompt(message)),
        ])
    except Exception:
        # Fallback: prompt for raw JSON and parse
        out = _classify_fallback(llm, message)

    if isinstance(out, ClassificationResult):
        return {
            "intent": out.intent,
            "urgency": out.urgency,
            "entities": {
                "flat_id": out.entities.flat_id or "",
                "tower": out.entities.tower or "",
                "date": out.entities.date or "",
                "time": out.entities.time or "",
            },
        }
    return out if isinstance(out, dict) else _default_classification()


def _classify_fallback(llm, message: str) -> ClassificationResult:
    """When with_structured_output fails, get raw content and parse JSON."""
    response = llm.invoke([
        SystemMessage(content=CLASSIFY_SYSTEM + "\n\nReply with ONLY a single valid JSON object."),
        HumanMessage(content=get_classify_prompt(message)),
    ])
    text = response.content if hasattr(response, "content") else str(response)
    # Strip markdown code block if present
    text = re.sub(r"^```(?:json)?\s*", "", text.strip())
    text = re.sub(r"\s*```\s*$", "", text)
    data = json.loads(text)
    return ClassificationResult(
        intent=data.get("intent", "inquiry"),
        urgency=data.get("urgency", "medium"),
        entities=ClassificationEntities(
            flat_id=data.get("entities", {}).get("flat_id", "") or "",
            tower=data.get("entities", {}).get("tower", "") or "",
            date=data.get("entities", {}).get("date", "") or "",
            time=data.get("entities", {}).get("time", "") or "",
        ),
    )


def _default_classification() -> dict:
    return {
        "intent": "inquiry",
        "urgency": "medium",
        "entities": {"flat_id": "", "tower": "", "date": "", "time": ""},
    }
