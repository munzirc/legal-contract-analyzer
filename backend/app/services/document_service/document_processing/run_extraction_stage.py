
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.document_model import Document
from app.services.document_service.extraction_service.extract_document import (
    extract_document,
)
from app.services.document_service.extraction_service.structure_builder.canonical_text_builder import (
    build_canonical_text,
)
from app.services.document_service.extraction_service.structure_builder.save_document_pages import (
    save_document_pages,
)


def run_extraction_stage(
    db: Session,
    document_id: UUID,
) -> None:
    document = db.get(Document, document_id)

    if document is None:
        raise ValueError(f"Document not found: {document_id}")

    pdf_storage_path = document.pdf_storage_path

    if not pdf_storage_path:
        raise ValueError("Document PDF storage path is missing.")

    extracted_document = extract_document(pdf_storage_path)
    canonical_document = build_canonical_text(extracted_document)

    if not canonical_document.text.strip():
        raise ValueError("Canonical text is empty.")

    document.canonical_text = canonical_document.text

    save_document_pages(
        db=db,
        document_id=document_id,
        canonical_document=canonical_document,
    )

    db.flush()
