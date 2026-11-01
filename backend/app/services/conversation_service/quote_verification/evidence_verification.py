
from dataclasses import dataclass
from pathlib import Path
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.document_model import Document
from app.models.document_chunk_model import DocumentChunk
from app.schemas.agent_response_schema import EvidenceQuote
from app.schemas.evidence_verification import VerifiedEvidence
from app.models.document_page import DocumentPage
from app.services.conversation_service.quote_verification.find_agent_quote import (
    find_quote_occurrences,
)
from app.services.conversation_service.quote_verification.quote_normalization import (
    normalize_agent_quote,
)
from app.services.conversation_service.quote_verification.find_quote_page_range import get_quote_page_range


@dataclass(frozen=True)
class ChunkInterval:
    chunk_id: UUID
    start: int
    end: int
    page_start: int | None
    page_end: int | None


def verify_evidence_item(
    db: Session,
    evidence: EvidenceQuote,
    selected_documents: list[Document],
) -> VerifiedEvidence | None:
    """
    Verify an agent quote against its selected document and chunk IDs.

    Returned offsets refer directly to the original canonical_text.
    Returns the first occurrence fully covered by the supplied chunks,
    or None if no occurrence passes verification.
    """

    # 1. Validate the selected document.
    try:
        document_id = UUID(str(evidence.document_id))
    except (ValueError, TypeError, AttributeError):
        return None

    document_by_id = {
        document.id: document
        for document in selected_documents
    }
    document = document_by_id.get(document_id)

    if document is None:
        return None

    canonical_text: str | None = document.canonical_text

    if not canonical_text:
        return None

    # 2. Validate and deduplicate chunk IDs.
    try:
        chunk_ids = list(
            dict.fromkeys(
                UUID(str(chunk_id))
                for chunk_id in evidence.chunk_ids
            )
        )
    except (ValueError, TypeError, AttributeError):
        return None

    if not chunk_ids:
        return None

    # Only accept chunks belonging to the selected document.
    statement = select(DocumentChunk).where(
        DocumentChunk.id.in_(chunk_ids),
        DocumentChunk.document_id == document_id,
    )
    chunks = list(db.scalars(statement).all())

    # Every supplied chunk must exist and belong to this document.
    if len(chunks) != len(chunk_ids):
        return None

    # 3. Normalize the agent quote and locate it in canonical text.
    quote = normalize_agent_quote(evidence.quote)

    if not quote:
        return None

    occurrences = find_quote_occurrences(
        canonical_text=canonical_text,
        quote=quote,
    )

    if not occurrences:
        return None

    # 4. Build valid chunk intervals.
    chunk_intervals = [
        ChunkInterval(
            chunk_id=chunk.id,
            start=chunk.start_offset,
            end=chunk.end_offset,
            page_start=chunk.page_start,
            page_end=chunk.page_end,
        )
        for chunk in chunks
        if chunk.start_offset < chunk.end_offset
    ]

    chunk_intervals.sort(
        key=lambda interval: (interval.start, interval.end)
    )

        # 5. Accept only occurrences fully covered by supplied chunks.
    for occurrence in occurrences:
        start = occurrence.start_offset
        end = occurrence.end_offset

        cursor = start
        supporting_chunks: list[ChunkInterval] = []

        for interval in chunk_intervals:
            if interval.end <= cursor:
                continue

            if interval.start > cursor:
                break

            supporting_chunks.append(interval)
            cursor = max(cursor, interval.end)

            if cursor >= end:
                break

        # Reject if the supplied chunks don't cover the entire occurrence.
        if cursor < end:
            continue

        # 6. Determine the actual PDF page range using stored page offsets.
        page_statement = (
            select(DocumentPage.page_number)
            .where(
                DocumentPage.document_id == document.id,
                DocumentPage.start_offset < end,
                DocumentPage.end_offset > start,
            )
            .order_by(DocumentPage.page_number)
        )

        page_numbers = list(db.scalars(page_statement).all())

        return VerifiedEvidence(
            document_id=document.id,
            pdf_storage_path=Path(document.pdf_storage_path),
            quote=canonical_text[start:end],
            canonical_start_offset=start,
            canonical_end_offset=end,
            page_start=page_numbers[0] if page_numbers else None,
            page_end=page_numbers[-1] if page_numbers else None,
            chunk_ids=[
                interval.chunk_id
                for interval in supporting_chunks
            ],
        )

    return None