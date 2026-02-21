"""
Pydantic schemas for the triage pipeline.
Used for classifier output, tool inputs/outputs, and API request/response.
"""
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


class Intent(str, Enum):
    """Customer intent classification."""
    SCHEDULE_VISIT = "schedule_site_visit"
    REQUEST_DOCUMENTS = "request_property_documents"
    PAYMENT_RECEIPT = "payment_receipt_issue"
    PROPERTY_INQUIRY = "property_inquiry"
    COMPLAINT = "complaint"
    OTHER = "other"


class Urgency(str, Enum):
    """Detected urgency level."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ExtractedEntities(BaseModel):
    """Structured entities extracted from the customer message."""
    flat_id: Optional[str] = Field(None, description="Apartment/flat identifier")
    tower: Optional[str] = Field(None, description="Tower or building name")
    date: Optional[str] = Field(None, description="Requested or relevant date")
    time: Optional[str] = Field(None, description="Requested or relevant time")
    extra: dict[str, Any] = Field(default_factory=dict, description="Other key-value pairs")


class ClassifierOutput(BaseModel):
    """Output of the intent/urgency/entity classifier."""
    intent: Intent
    urgency: Urgency
    entities: ExtractedEntities
    raw_confidence: Optional[float] = None


class TriageRequest(BaseModel):
    """Incoming customer message to the API."""
    message: str = Field(..., min_length=1)
    customer_id: Optional[str] = None
    session_id: Optional[str] = None


class TriageResponse(BaseModel):
    """Full triage pipeline response."""
    intent: Intent
    urgency: Urgency
    entities: ExtractedEntities
    knowledge_snippets: list[str] = Field(default_factory=list)
    tool_result: Optional[dict[str, Any]] = None
    draft_reply: str
    metadata: dict[str, Any] = Field(default_factory=dict)
