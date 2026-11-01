from app.services.document_service.extraction_service.structure_builder.canonical_text_builder import PageTextRange
from app.services.document_service.extraction_service.structure_builder.section_builder import  DocumentSection,DocumentSubsection
from app.services.document_service.chunking_service.chunk_data_types import ChunkStructureReference

def get_page_range(
    text: str,
    start_offset: int,
    end_offset: int,
    page_ranges: list[PageTextRange],
) -> tuple[int, int]:
    overlapping_pages = [
        page.page_number
        for page in page_ranges
        if start_offset < page.end_offset
        and end_offset > page.start_offset
    ]
    

    if not overlapping_pages:
        print(f"\nChunk range: [{start_offset}, {end_offset})")
        print("Chunk text:", repr(text[start_offset:end_offset]))

        for page in page_ranges:
            if page.start_offset <= start_offset <= page.end_offset:
                print("Nearby page range:", page)

        raise ValueError("Chunk offsets do not overlap any PDF page.")
        
    return overlapping_pages[0], overlapping_pages[-1]

def build_section_reference(
    section: DocumentSection,
) -> ChunkStructureReference:
    return ChunkStructureReference(
        identifier=section.identifier,
        title=section.title,
        start_offset=section.start_offset,
        end_offset=section.end_offset,
    )
    
def build_subsection_reference(
    subsection: DocumentSubsection,
) -> ChunkStructureReference:
    return ChunkStructureReference(
        identifier=subsection.identifier,
        title=subsection.title,
        start_offset=subsection.start_offset,
        end_offset=subsection.end_offset,
    )
