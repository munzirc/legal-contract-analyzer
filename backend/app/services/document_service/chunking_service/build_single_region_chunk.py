from app.services.document_service.extraction_service.structure_builder.section_builder import DocumentRegion
from app.services.document_service.extraction_service.structure_builder.canonical_text_builder import PageTextRange
from app.services.document_service.chunking_service.chunk_data_types import BuiltChunk
from app.services.document_service.chunking_service.helper import get_page_range

def build_single_region_chunk(
    text: str,
    region: DocumentRegion,
    page_ranges: list[PageTextRange],
    chunk_index: int,
) -> BuiltChunk:
    
    chunk_start = region.start_offset
    chunk_end = region.end_offset

    chunk_text = text[chunk_start:chunk_end]
    
    page_start, page_end = get_page_range(
        text=text,
        start_offset=chunk_start,
        end_offset=chunk_end,
        page_ranges=page_ranges,
    )
    
    return BuiltChunk(
        chunk_index=chunk_index,
        start_offset=chunk_start,
        end_offset=chunk_end,
        text=chunk_text,
        page_start=page_start,
        page_end=page_end,
        region_type=region.region_type,
        region_identifier=region.identifier,
        region_title=region.title,
    )