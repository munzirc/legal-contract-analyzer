from app.services.document_service.section_based_chunks.section_validation.schemas import (
    DocumentSection,
)
from app.services.document_service.extraction_service.structure_builder.canonical_text_builder import (
    PageTextRange,
)

from app.services.document_service.section_based_chunks.chunking.schemas import BuiltChunk
from app.services.document_service.section_based_chunks.chunking.section_based_chunks import build_section_chunks

from app.services.document_service.section_based_chunks.chunking.overlap_split import build_text_chunks




def build_chunks(
    text: str,
    sections: list[DocumentSection],
    page_ranges: list[PageTextRange],
) -> list[BuiltChunk]:
    
    chunks: list[BuiltChunk] = []

    # No sections: split the entire document using text-based splitting.
    if not sections:
        build_text_chunks(
            text=text,
            start_offset=0,
            page_ranges=page_ranges,
            chunks=chunks,
            identifier=None,
            title=None,
        )
        return chunks

    # Ensure sections are processed in document order.
    # sections = sorted(sections, key=lambda section: section.start_offset)

    # Split introductory text before the first section.
    intro_end = sections[0].start_offset

    if text[:intro_end].strip():
        build_text_chunks(
            text=text[:intro_end],
            start_offset=0,
            page_ranges=page_ranges,
            chunks=chunks,
            identifier="INTRODUCTORY",
            title="Introductory Text",
        )

    # Build one chunk per detected section.
    build_section_chunks(
        text=text,
        sections=sections,
        page_ranges=page_ranges,
        chunks=chunks,
    )

    return chunks