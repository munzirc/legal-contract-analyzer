
import uuid

from sqlalchemy import delete
from sqlalchemy.orm import Session

from app.models.document_chunk_model import DocumentChunk
from app.services.document_service.section_based_chunks.chunking.schemas import BuiltChunk


def save_chunks(
    db: Session,
    document_id: uuid.UUID,
    chunks: list[BuiltChunk],
) -> None:
    
    if not chunks:
        raise ValueError("Cannot save an empty chunk list.")
    
    # Remove previous chunks and their dependent records.
    db.execute(
        delete(DocumentChunk).where(
            DocumentChunk.document_id == document_id
        )
    )


    records = [
        DocumentChunk(
            document_id=document_id,
            chunk_index=chunk.chunk_index,
            section_identifier=chunk.identifier,
            section_title=chunk.title,
            section_start_offset=chunk.section_start_offset,
            section_end_offset=chunk.section_end_offset,
            subsections=[
                {
                    "identifier": subsection.identifier,
                    "title": subsection.title,
                    "start_offset": subsection.start_offset,
                    "end_offset": subsection.end_offset,
                }
                for subsection in chunk.subsections
            ],
            text=chunk.text,
            start_offset=chunk.start_offset,
            end_offset=chunk.end_offset,
            page_start=chunk.page_start,
            page_end=chunk.page_end,
        )
        for chunk in chunks
    ]

    db.add_all(records)
    db.flush()
