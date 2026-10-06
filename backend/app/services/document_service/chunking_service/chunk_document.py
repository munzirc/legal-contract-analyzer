from dataclasses import dataclass

from app.schemas.llm_output_schema import DocumentRegion
from app.services.document_service.extraction_service.canonical_text_builder import PageTextRange


@dataclass
class ChunkData:
    chunk_index: int
    text: str

    start_offset: int
    end_offset: int

    section_number: str | None
    section_title: str | None

    page_start: int
    page_end: int
    


def build_chunks(
    text: str,
    regions: list[DocumentRegion],
    page_ranges: list[PageTextRange],
) -> list[ChunkData]:
    print(f"Building chunks for text of length {len(text)}")
    return []