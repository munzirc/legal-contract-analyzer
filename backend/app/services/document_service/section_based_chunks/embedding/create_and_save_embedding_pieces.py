
from dataclasses import asdict

from sqlalchemy import delete
from sqlalchemy.orm import Session

from app.models.chunk_embedding import ChunkEmbedding
from app.models.document_chunk_model import DocumentChunk
from app.services.document_service.section_based_chunks.embedding.prepare_embedding_pieces import (
    prepare_embedding_pieces,
)
from app.services.document_service.section_based_chunks.embedding.schemas import (
    EmbeddingPieceRecord,
)


def create_and_save_embedding_pieces(
    db: Session,
    chunks: list[DocumentChunk],
) -> int:
    if not chunks:
        raise ValueError(
            "Cannot create embedding pieces without chunks."
        )

    # Prepare all pieces before modifying the database.
    pieces = prepare_embedding_pieces(chunks)

    if not pieces:
        raise ValueError("No embedding pieces were created.")

    piece_records = [
        EmbeddingPieceRecord(
            chunk_id=piece.chunk_id,
            piece_index=piece.piece_index,
            text=piece.text,
        )
        for piece in pieces
    ]

    records = [asdict(record) for record in piece_records]

    chunk_ids = [chunk.id for chunk in chunks]

    db.execute(
        delete(ChunkEmbedding).where(
            ChunkEmbedding.chunk_id.in_(chunk_ids)
        )
    )

    db.add_all(
        ChunkEmbedding(**record)
        for record in records
    )

    db.flush()

    return len(records)
