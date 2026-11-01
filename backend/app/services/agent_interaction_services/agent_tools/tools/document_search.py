
from uuid import UUID

from sqlalchemy import func, select

from app.db.database import SessionLocal
from app.models.chunk_embedding import ChunkEmbedding
from app.models.document_chunk_model import DocumentChunk
from app.services.agent_interaction_services.agent_tools.embed_query import (
    embed_query,
)
from app.schemas.search_result_schema import (
    DocumentSearchResult,
)

CHUNKS_PER_DOCUMENT = 5


def document_search(
    query: str,
    document_ids: list[UUID],
    chunks_per_document: int = CHUNKS_PER_DOCUMENT,
) -> list[DocumentSearchResult]:
    if not document_ids:
        return []

    if chunks_per_document < 1:
        raise ValueError("chunks_per_document must be at least 1.")

    query_embedding = embed_query(query)

    distance = ChunkEmbedding.embedding.cosine_distance(query_embedding)

    # Step 1: Rank embedding pieces within each chunk.
    ranked_pieces = (
        select(
            ChunkEmbedding.chunk_id.label("chunk_id"),
            ChunkEmbedding.piece_index.label("piece_index"),
            distance.label("distance"),
            func.row_number()
            .over(
                partition_by=ChunkEmbedding.chunk_id,
                order_by=distance,
            )
            .label("piece_rank"),
        )
        .join(
            DocumentChunk,
            DocumentChunk.id == ChunkEmbedding.chunk_id,
        )
        .where(DocumentChunk.document_id.in_(document_ids))
        .subquery()
    )

    # Step 2: Keep only the best-matching piece for each chunk.
    best_pieces = (
        select(
            ranked_pieces.c.chunk_id,
            ranked_pieces.c.piece_index,
            ranked_pieces.c.distance,
        )
        .where(ranked_pieces.c.piece_rank == 1)
        .subquery()
    )

    # Step 3: Rank unique chunks separately within each document.
    ranked_chunks = (
        select(
            DocumentChunk,
            best_pieces.c.piece_index,
            best_pieces.c.distance,
            func.row_number()
            .over(
                partition_by=DocumentChunk.document_id,
                order_by=best_pieces.c.distance,
            )
            .label("document_rank"),
        )
        .join(
            best_pieces,
            best_pieces.c.chunk_id == DocumentChunk.id,
        )
        .subquery()
    )

    # Step 4: Return up to the requested number of chunks per document.
    statement = (
        select(
            DocumentChunk,
            ranked_chunks.c.piece_index,
            ranked_chunks.c.distance,
        )
        .join(
            ranked_chunks,
            ranked_chunks.c.id == DocumentChunk.id,
        )
        .where(ranked_chunks.c.document_rank <= chunks_per_document)
        .order_by(
            DocumentChunk.document_id,
            ranked_chunks.c.distance,
        )
    )

    with SessionLocal() as db:
        rows = db.execute(statement).all()

    return [
        DocumentSearchResult(
            document_id=chunk.document_id,
            chunk_id=chunk.id,
            text=chunk.text,
            page_start=chunk.page_start,
            page_end=chunk.page_end,
            start_offset=chunk.start_offset,
            end_offset=chunk.end_offset,
            section_identifier=chunk.section_identifier,
            section_title=chunk.section_title,
            piece_index=piece_index,
            similarity=1 - distance_value,
        )
        for chunk, piece_index, distance_value in rows
    ]
