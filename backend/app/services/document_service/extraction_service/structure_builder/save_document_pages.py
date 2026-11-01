
from uuid import UUID

from sqlalchemy import delete
from sqlalchemy.orm import Session

from app.models.document_page import DocumentPage
from app.services.document_service.extraction_service.structure_builder.canonical_text_builder import (
    CanonicalDocument,
)


def save_document_pages(
    db: Session,
    document_id: UUID,
    canonical_document: CanonicalDocument,
) -> None:
    # Remove page ranges from any previous extraction attempt.
    db.execute(
        delete(DocumentPage).where(
            DocumentPage.document_id == document_id
        )
    )

    page_records = [
        DocumentPage(
            document_id=document_id,
            page_number=page_range.page_number,
            start_offset=page_range.start_offset,
            end_offset=page_range.end_offset,
        )
        for page_range in canonical_document.page_ranges
    ]

    db.add_all(page_records)
