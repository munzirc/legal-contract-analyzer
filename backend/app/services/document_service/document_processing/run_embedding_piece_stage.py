
import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.document_chunk_model import DocumentChunk
from app.services.document_service.section_based_chunks.embedding.create_and_save_embedding_pieces import (
    create_and_save_embedding_pieces,
)


def run_embedding_piece_stage(
    db: Session,
    document_id: uuid.UUID,
) -> int:
    chunks = db.scalars(
        select(DocumentChunk)
        .where(DocumentChunk.document_id == document_id)
        .order_by(DocumentChunk.chunk_index)
    ).all()

    if not chunks:
        raise ValueError(
            f"No saved chunks found for document {document_id}."
        )

    return create_and_save_embedding_pieces(
        db=db,
        chunks=list(chunks),
    )
