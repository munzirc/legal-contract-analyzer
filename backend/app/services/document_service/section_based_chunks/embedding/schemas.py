import uuid
from dataclasses import dataclass
from app.models.chunk_embedding import EmbeddingStatus


@dataclass
class EmbeddingPiece:
    chunk_id: uuid.UUID
    chunk_index: int
    piece_index: int
    text: str



@dataclass
class EmbeddingPieceRecord:
    chunk_id: uuid.UUID
    piece_index: int
    text: str
    status: EmbeddingStatus = EmbeddingStatus.PENDING
    embedding: list[float] | None = None  
