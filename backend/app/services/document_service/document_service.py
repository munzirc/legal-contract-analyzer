from pathlib import Path
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.document_model import Document

def get_documents(db: Session) -> list[Document]:
    statement = select(Document).order_by(
        Document.created_at.desc()
    )

    return list(db.scalars(statement).all())


def delete_document(
    document_id: UUID,
    db: Session
) -> bool:

    statement = select(Document).where(
        Document.id == document_id
    )

    document = db.scalar(statement)

    if document is None:
        return False

    original_storage_path = document.original_storage_path
    pdf_storage_path = document.pdf_storage_path

    try:
        db.delete(document)
        db.commit()

    except Exception:
        db.rollback()
        raise

    # Delete the physical files after the database transaction succeeds.
    storage_paths = {
        original_storage_path,
        pdf_storage_path,
    }

    for storage_path in storage_paths:
        try:
            Path(storage_path).unlink(missing_ok=True)
        except OSError as error:
            print(
                f"Failed to delete document file "
                f"{storage_path}: {error}"
            )

    return True