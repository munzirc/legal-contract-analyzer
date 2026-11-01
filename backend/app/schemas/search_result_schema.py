
from dataclasses import dataclass
from uuid import UUID


@dataclass
class DocumentSearchResult:
    document_id: UUID
    chunk_id: UUID
    text: str
    page_start: int
    page_end: int
    start_offset: int
    end_offset: int
    section_identifier: str | None
    section_title: str | None
    piece_index: int
    similarity: float
