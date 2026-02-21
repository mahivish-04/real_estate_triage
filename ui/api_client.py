"""
API client for chat endpoint. Modular and independently testable.
Uses Pydantic schemas and config (no hardcoded URLs or keys).
"""
from typing import Optional

import httpx

from ui.config import BACKEND_URL, CHAT_TIMEOUT
from ui.schemas import ChatRequestSchema, ChatResponseSchema


def chat(message: str, session_id: Optional[str] = None) -> str:
    """
    POST to backend /chat; returns reply text.
    Raises on network or validation errors.
    """
    payload = ChatRequestSchema(message=message.strip(), session_id=session_id)
    url = f"{BACKEND_URL}/chat"
    with httpx.Client(timeout=CHAT_TIMEOUT) as client:
        response = client.post(
            url,
            json=payload.model_dump(exclude_none=True),
        )
        response.raise_for_status()
    data = response.json()
    return ChatResponseSchema(**data).reply
