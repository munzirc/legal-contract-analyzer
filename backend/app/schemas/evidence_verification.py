from uuid import UUID
from pathlib import Path

from pydantic import BaseModel, ConfigDict


class VerifiedEvidence(BaseModel):
  
    model_config = ConfigDict(frozen=True)

    document_id: UUID
    pdf_storage_path: Path
    quote: str

    canonical_start_offset: int
    canonical_end_offset: int

    page_start: int | None
    page_end: int | None


    chunk_ids: list[UUID]
