
from app.models.document_chunk_model import DocumentChunk
from app.services.document_service.section_based_chunks.embedding.text_splitter import split_text
from app.services.document_service.section_based_chunks.embedding.schemas import EmbeddingPiece


def prepare_embedding_pieces(
    chunks: list[DocumentChunk],
) -> list[EmbeddingPiece]:
    pieces: list[EmbeddingPiece] = []

    for chunk in chunks:
        chunk_texts = split_text(chunk.text)

        for piece_index, piece_text in enumerate(chunk_texts):
            pieces.append(
                EmbeddingPiece(
                    chunk_id=chunk.id,
                    chunk_index=chunk.chunk_index,
                    piece_index=piece_index,
                    text=piece_text,
                )
            )

    return pieces
