from dataclasses import dataclass
from pathlib import Path
from uuid import UUID

from sqlalchemy import select

from app.core.storage import UPLOAD_DIR
from app.db.database import SessionLocal
from app.enums.document_file_type import DocumentFileType
from app.models.document_model import Document


@dataclass(frozen=True)
class DocumentPdf:
    document_id: UUID
    file_path: Path


def get_document_pdf(document_id: UUID) -> DocumentPdf | None:
    """Return the stored PDF location for an existing document."""

    with SessionLocal() as db:
        statement = select(
            Document.id,
            Document.pdf_storage_path,
            Document.file_type,
        ).where(Document.id == document_id)

        row = db.execute(statement).one_or_none()

    if row is None:
        return None

    if row.file_type not in {
        DocumentFileType.PDF,
        DocumentFileType.DOCX,
    }:
        return None

    file_path = Path(row.pdf_storage_path).resolve()
    upload_dir = UPLOAD_DIR.resolve()

    try:
        file_path.relative_to(upload_dir)
    except ValueError:
        return None

    if not file_path.is_file():
        return None

    return DocumentPdf(
        document_id=row.id,
        file_path=file_path,
    )