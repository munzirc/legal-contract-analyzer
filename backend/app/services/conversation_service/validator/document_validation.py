from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.document_model import Document
from app.enums.document_status import DocumentStatus


def validate_documents(
    db: Session,
    document_ids: list[UUID],
) -> list[Document]:

    
    document_ids = list(dict.fromkeys(document_ids))

    documents = db.scalars(
        select(Document).where(
            Document.id.in_(document_ids)
        )
    ).all()

    documents_by_id = {
        document.id: document
        for document in documents
    }

    # 1. Check that every requested document exists.
    if len(documents_by_id) != len(document_ids):
        raise HTTPException(
            status_code=404,
            detail="One or more documents were not found.",
        )

    selected_documents = [
        documents_by_id[document_id]
        for document_id in document_ids
    ]

    # 2. Check status and extracted text.
    for document in selected_documents:
        if document.status != DocumentStatus.READY:
            raise HTTPException(
                status_code=409,
                detail=f"Document '{document.filename}' is not ready.",
            )

        if not document.canonical_text or not document.canonical_text.strip():
            raise HTTPException(
                status_code=409,
                detail=f"Document '{document.filename}' has no readable text.",
            )

    return selected_documents