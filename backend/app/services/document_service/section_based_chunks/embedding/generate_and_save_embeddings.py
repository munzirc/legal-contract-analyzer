
import time
import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session


from app.models.document_chunk_model import DocumentChunk
from app.models.document_model import Document
from app.models.chunk_embedding import ChunkEmbedding, EmbeddingStatus
from app.services.document_service.section_based_chunks.embedding.embedding_service import (
    embed_text,
)
from app.enums.document_status import DocumentStatus


EMBEDDING_REQUEST_DELAY_SECONDS = 0.1


def generate_and_save_embeddings(
    db: Session,
    document_id: uuid.UUID,
) -> int:
    document = db.get(Document, document_id)

    if document is None:
        raise ValueError("Document not found.")

    if document.status not in (
        DocumentStatus.EMBEDDING,
        DocumentStatus.EMBEDDING_FAILED,
    ):
        raise ValueError(
            f"Cannot generate embeddings for document "
            f"in status {document.status}."
        )

    pieces = db.execute(
        select(ChunkEmbedding.id, ChunkEmbedding.text)
        .join(
            DocumentChunk,
            DocumentChunk.id == ChunkEmbedding.chunk_id,
        )
        .where(
            DocumentChunk.document_id == document_id,
            ChunkEmbedding.status.in_(
                [EmbeddingStatus.PENDING, EmbeddingStatus.FAILED]
            ),
        )
        .order_by(
            DocumentChunk.chunk_index,
            ChunkEmbedding.piece_index,
        )
    ).all()

    db.commit()

    completed_count = 0

    for index, piece in enumerate(pieces):
        piece_id = piece.id

        try:
            # Call the embedding API without an open DB transaction.
            vector = embed_text(piece.text)

            record = db.execute(
                select(ChunkEmbedding)
                .where(ChunkEmbedding.id == piece_id)
                .with_for_update()
            ).scalar_one_or_none()

            if record is None:
                raise RuntimeError(
                    f"Embedding piece {piece_id} no longer exists."
                )

            record.embedding = vector
            record.status = EmbeddingStatus.COMPLETED
            record.updated_at = datetime.now(timezone.utc)

            # Persist each successful vector independently.
            db.commit()
            completed_count += 1

        except Exception:
            db.rollback()

            record = db.execute(
                select(ChunkEmbedding)
                .where(ChunkEmbedding.id == piece_id)
                .with_for_update()
            ).scalar_one_or_none()

            if record is not None:
                record.status = EmbeddingStatus.FAILED
                record.updated_at = datetime.now(timezone.utc)
                db.commit()

            raise

        if index < len(pieces) - 1:
            time.sleep(EMBEDDING_REQUEST_DELAY_SECONDS)

    return completed_count
