import uuid

from sqlalchemy.orm import Session

from app.enums.document_status import DocumentStatus
from app.models.document_model import Document


def update_document_status(
    db: Session,
    document_id: uuid.UUID,
    status: DocumentStatus,
) -> None:
    document = db.get(Document, document_id)

    if document is None:
        raise ValueError(f"Document not found: {document_id}")

    document.status = status