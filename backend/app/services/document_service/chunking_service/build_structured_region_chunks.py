from app.services.document_service.extraction_service.structure_builder.section_builder import DocumentRegion
from app.services.document_service.extraction_service.structure_builder.canonical_text_builder import PageTextRange
from app.services.document_service.chunking_service.chunk_data_types import BuiltChunk
from app.services.document_service.chunking_service.helper import get_page_range, build_subsection_reference



def build_structured_region_chunks(
    text: str,
    region: DocumentRegion,
    page_ranges: list[PageTextRange],
    start_chunk_index: int,
) -> list[BuiltChunk]:
    
    chunks: list[BuiltChunk] = []

    sections = region.sections
    
    cursor = region.start_offset
    
    for index, section in enumerate(sections):
        chunk_start = cursor
        chunk_end = (
            sections[index + 1].start_offset
            if index + 1 < len(sections)
            else region.end_offset
        )
        
        chunk_text = text[chunk_start:chunk_end]

        if not chunk_text.strip():
            cursor = chunk_end
            continue

        page_start, page_end = get_page_range(
            text=text,
            start_offset=chunk_start,
            end_offset=chunk_end,
            page_ranges=page_ranges,
        )
        
        chunk = BuiltChunk(
            chunk_index=start_chunk_index + len(chunks),
            start_offset=chunk_start,
            end_offset=chunk_end,
            text=chunk_text,
            page_start=page_start,
            page_end=page_end,
            region_type=region.region_type,
            region_identifier=region.identifier,
            region_title=region.title,
            section_identifier=section.identifier,
            section_title=section.title,
            section_start_offset=section.start_offset,
            section_end_offset=section.end_offset,
            subsections=[
                build_subsection_reference(subsection)
                for subsection in section.subsections
            ],
        )

        chunks.append(chunk)
        cursor = chunk_end

    return chunks