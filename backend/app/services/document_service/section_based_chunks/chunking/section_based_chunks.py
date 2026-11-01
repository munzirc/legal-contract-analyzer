
from app.services.document_service.section_based_chunks.section_validation.schemas import DocumentSection
from app.services.document_service.extraction_service.structure_builder.canonical_text_builder import PageTextRange

from app.services.document_service.section_based_chunks.chunking.schemas import BuiltChunk, ChunkStructureReference
from app.services.document_service.chunking_service.helper import get_page_range



def build_section_chunks(
    text: str,
    sections: list[DocumentSection],
    page_ranges: list[PageTextRange],
    chunks: list[BuiltChunk],
) -> None:
    for index, section in enumerate(sections):
        chunk_start = section.start_offset

        # Include gaps in the preceding section's chunk.
        # The final section also includes trailing text.
        chunk_end = (
            sections[index + 1].start_offset
            if index + 1 < len(sections)
            else len(text)
        )

        chunk_text = text[chunk_start:chunk_end]

        if not chunk_text.strip():
            continue

        page_start, page_end = get_page_range(
            text=text,
            start_offset=chunk_start,
            end_offset=chunk_end,
            page_ranges=page_ranges,
        )

        subsections = [
            ChunkStructureReference(
                identifier=subsection.identifier,
                title=subsection.title,
                start_offset=subsection.start_offset,
                end_offset=subsection.end_offset,
            )
            for subsection in section.subsections
        ]

        chunks.append(
            BuiltChunk(
                chunk_index=len(chunks),
                start_offset=chunk_start,
                end_offset=chunk_end,
                text=chunk_text,
                page_start=page_start,
                page_end=page_end,
                identifier=section.identifier,
                title=section.title,
                section_start_offset=section.start_offset,
                section_end_offset=section.end_offset,
                subsections=subsections,
            )
        )