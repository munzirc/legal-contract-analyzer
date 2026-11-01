from app.services.document_service.extraction_service.structure_builder.section_builder import DocumentRegion
from app.services.document_service.extraction_service.structure_builder.canonical_text_builder import PageTextRange 
from app.services.document_service.chunking_service.chunk_data_types import BuiltChunk
from app.services.document_service.chunking_service.build_unstructured_region_chunks import build_unstructured_region_chunks
from app.services.document_service.chunking_service.build_structured_region_chunks import build_structured_region_chunks
from app.services.document_service.chunking_service.build_single_region_chunk import build_single_region_chunk

DEFAULT_TEXT_LIMIT = 2400
DEFAULT_OVERLAP_RATIO = 0.15


def build_chunks(
    text: str,
    regions: list[DocumentRegion],
    page_ranges: list[PageTextRange],
) -> list[BuiltChunk]:
    
    chunks: list[BuiltChunk] = []

    for index, region in enumerate(regions):
        
        region_text = text[
            region.start_offset:region.end_offset
        ]

        if not region_text.strip():
            continue
        
        if index == 0:
            region_chunks = [
                build_single_region_chunk(
                    text=text,
                    region=region,
                    page_ranges=page_ranges,
                    chunk_index=len(chunks),
                )
            ]
            chunks.extend(region_chunks)
            continue
            
        if not region.sections:
            # Regions without sections use character-based chunking.
            region_chunks = build_unstructured_region_chunks(
                text=text,
                region=region,
                page_ranges=page_ranges,
                start_chunk_index=len(chunks),
                max_length=DEFAULT_TEXT_LIMIT,
                overlap_ratio=DEFAULT_OVERLAP_RATIO,
            )
        else:
            # Regions with sections use section-based chunking.
            region_chunks = build_structured_region_chunks(
                text=text,
                region=region,
                page_ranges=page_ranges,
                start_chunk_index=len(chunks),
            )

        chunks.extend(region_chunks)


    return chunks