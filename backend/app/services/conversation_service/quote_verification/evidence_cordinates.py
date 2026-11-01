from dataclasses import dataclass
from pathlib import Path

import pymupdf
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.document_page import DocumentPage
from app.schemas.evidence_verification import VerifiedEvidence


@dataclass(frozen=True)
class EvidenceCoordinate:
    page_number: int
    x1: float
    y1: float
    x2: float
    y2: float


def find_evidence_coordinates(
    db: Session,
    evidence: VerifiedEvidence,
) -> list[EvidenceCoordinate]:
    """
    Split verified evidence by canonical page ranges, search each
    corresponding PDF page, and return the matching PDF coordinates.

    Returns an empty list if the complete quote cannot be located.
    Does not save EvidenceRegion records.
    """

    if (
        not evidence.quote
        or evidence.canonical_start_offset < 0
        or evidence.canonical_end_offset <= evidence.canonical_start_offset
    ):
        return []

    # 1. Fetch the canonical text ranges for this document.
    page_ranges: list[DocumentPage] = list(
        db.scalars(
            select(DocumentPage)
            .where(DocumentPage.document_id == evidence.document_id)
            .order_by(DocumentPage.page_number)
        ).all()
    )
    

    if not page_ranges:
        return []

    # 2. Open the original PDF.
    pdf_path: Path = evidence.pdf_storage_path
    coordinates: list[EvidenceCoordinate] = []

    try:
        with pymupdf.open(pdf_path) as pdf:
            # 3. Split the evidence into page-specific quote segments.
            for page_range in page_ranges:
                start_offset = max(
                    evidence.canonical_start_offset,
                    page_range.start_offset,
                )
                end_offset = min(
                    evidence.canonical_end_offset,
                    page_range.end_offset,
                )

                # No overlap between this page and the evidence.
                if start_offset >= end_offset:
                    continue

                # Convert absolute canonical offsets to quote-relative offsets.
                quote_start = (
                    start_offset - evidence.canonical_start_offset
                )
                quote_end = (
                    end_offset - evidence.canonical_start_offset
                )

                page_quote = evidence.quote[quote_start:quote_end].strip()

                if not page_quote:
                    continue

                # 4. Search the matching physical PDF page.
                # Database page numbers are 1-based; PyMuPDF indices are 0-based.
                pdf_index = page_range.page_number - 1

                if pdf_index < 0 or pdf_index >= len(pdf):
                    return []

                page = pdf[pdf_index]
                
                rectangles = page.search_for(page_quote)
                
                # Require a match for every non-empty page segment.
                # Never return misleading partial coordinates.
                if not rectangles:
                    return []

                # 5. Convert all matching rectangles into coordinate records.
                for rect in rectangles:
                    coordinates.append(
                        EvidenceCoordinate(
                            page_number=page_range.page_number,
                            x1=float(rect.x0),
                            y1=float(rect.y0),
                            x2=float(rect.x1),
                            y2=float(rect.y1),
                        )
                    )

    except (OSError, ValueError, RuntimeError):
        return []

    return coordinates