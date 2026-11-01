from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.document_page import DocumentPage
from app.services.document_service.extraction_service.structure_builder.canonical_text_builder import (
    PageTextRange,
)


def load_page_ranges(
    db: Session,
    document_id: UUID,
) -> list[PageTextRange]:
    pages = db.scalars(
        select(DocumentPage)
        .where(DocumentPage.document_id == document_id)
        .order_by(DocumentPage.page_number)
    ).all()

    return [
        PageTextRange(
            page_number=page.page_number,
            start_offset=page.start_offset,
            end_offset=page.end_offset,
        )
        for page in pages
    ]
