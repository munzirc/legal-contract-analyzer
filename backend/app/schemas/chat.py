from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    conversation_id: UUID | None = None
    message: str = Field(min_length=1)
    document_ids: list[UUID] = Field(default_factory=list)
    
    
class EvidenceRegionResponse(BaseModel):
    page_number: int
    x1: float
    y1: float
    x2: float
    y2: float


class EvidenceResponse(BaseModel):
    id: UUID
    document_id: UUID
    quote: str
    is_verified: bool
    regions: list[EvidenceRegionResponse]


class ChatMessageResponse(BaseModel):
    id: UUID
    role: str
    content: str
    created_at: datetime
    evidence: list[EvidenceResponse]


class ChatResponse(BaseModel):
    conversation_id: UUID
    document_ids: list[UUID]
    messages: list[ChatMessageResponse]