
from app.services.document_service.extraction_service.structure_builder.canonical_text_builder import (
    PageTextRange,
)
from app.services.document_service.section_based_chunks.section_validation.serialize_data import (
    deserialize_sections,
)
from app.services.document_service.section_based_chunks.chunking.chunk_builder import (
    build_chunks,
)
from app.services.document_service.section_based_chunks.chunking.schemas import (
    BuiltChunk,
)


def run_chunking_stage(
    canonical_text: str,
    stored_structure: list[dict] | None,
    page_ranges: list[PageTextRange],
) -> list[BuiltChunk]:
    if not canonical_text or not canonical_text.strip():
        raise ValueError("Canonical text is missing or empty.")

    if not page_ranges:
        raise ValueError("Document page ranges are missing.")

    # Restore the validated structure saved during the previous stage.
    sections = deserialize_sections(stored_structure)

    # An empty structure is valid; build_chunks handles the fallback.
    chunks = build_chunks(
        text=canonical_text,
        sections=sections,
        page_ranges=page_ranges,
    )

    if not chunks:
        raise ValueError("Chunking produced no chunks.")

    return chunks
