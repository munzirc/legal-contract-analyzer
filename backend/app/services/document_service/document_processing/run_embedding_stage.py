
import uuid

from sqlalchemy.orm import Session

from app.services.document_service.section_based_chunks.embedding.generate_and_save_embeddings import (
    generate_and_save_embeddings,
)


def run_embedding_stage(
    db: Session,
    document_id: uuid.UUID,
) -> int:
    return generate_and_save_embeddings(
        db=db,
        document_id=document_id,
    )
