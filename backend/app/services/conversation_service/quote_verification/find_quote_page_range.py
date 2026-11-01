from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.document_page import DocumentPage

def get_quote_page_range(
    db: Session,
    document_id: UUID,
    start_offset: int,
    end_offset: int,
) -> tuple[int | None, int | None]:
    statement = (
        select(DocumentPage.page_number)
        .where(
            DocumentPage.document_id == document_id,
            DocumentPage.start_offset < end_offset,
            DocumentPage.end_offset > start_offset,
        )
        .order_by(DocumentPage.page_number)
    )

    page_numbers = list(db.scalars(statement).all())

    if not page_numbers:
        return None, None

    return page_numbers[0], page_numbers[-1]