"""
Pydantic schemas for UI ↔ API contract. Keeps UI independently testable.
"""
from typing import Optional

from pydantic import BaseModel, Field


class ChatRequestSchema(BaseModel):
    """Request body for POST /chat. Matches backend contract."""
    message: str = Field(..., min_length=1)
    session_id: Optional[str] = None


class ChatResponseSchema(BaseModel):
    """Response body from POST /chat. Matches backend contract."""
    reply: str
