from pydantic import BaseModel, Field


class EvidenceQuote(BaseModel):
    document_id: str = Field(
        description="ID of the selected document containing the quotation."
    )
    quote: str = Field(
        description="Exact, unchanged quotation copied from the selected document."
    )
    chunk_ids: list[str] = Field(
        description=(
            "IDs of the source chunks containing the quotation, "
            "including consecutive chunks if the quotation spans "
            "a chunk boundary."
        )
    )
    

class AgentResponse(BaseModel):
    answer: str = Field(
        description="Answer based only on the selected documents."
    )
    evidence: list[EvidenceQuote] = Field(
        description="Exact quotations supporting the answer."
    )


class AgentRunResult(BaseModel):
    response: AgentResponse | None = None
    interaction_id: str | None = None
    completed: bool = False
    error: str | None = None