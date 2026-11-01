from uuid import UUID

from pydantic import BaseModel, Field


class EvidenceCoordinate(BaseModel):
    page_number: int
    x1: float
    y1: float
    x2: float
    y2: float


class VerifiedEvidenceResponse(BaseModel):
    quote: str
    document_id: UUID |None = None
    is_verified: bool
    coordinates: list[EvidenceCoordinate] = Field(
        default_factory=list
    )


class VerifiedEvidenceResult(BaseModel):
    evidence: list[VerifiedEvidenceResponse] = Field(
        default_factory=list
    )