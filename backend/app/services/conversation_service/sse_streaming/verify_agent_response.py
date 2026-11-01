import logging

from sqlalchemy.orm import Session
from uuid import UUID

from app.models.document_model import Document
from app.services.conversation_service.quote_verification.evidence_verification import (
    verify_evidence_item,
) 
from app.services.conversation_service.quote_verification.evidence_cordinates import (
    find_evidence_coordinates 
)
from app.schemas.agent_response_schema import EvidenceQuote
from app.schemas.evidence_verification import VerifiedEvidence
from app.schemas.verified_evidence import (
    EvidenceCoordinate,
    VerifiedEvidenceResponse,
)

logger = logging.getLogger(__name__)


def verify_agent_evidence_item(
    db: Session,
    evidence: EvidenceQuote,
    selected_documents: list[Document],
) -> VerifiedEvidenceResponse | None:
    result: VerifiedEvidence | None = verify_evidence_item(
        db=db,
        evidence=evidence,
        selected_documents=selected_documents,
    )

    if result is None:
        try:
            document_id = UUID(evidence.document_id)
        except (ValueError, TypeError, AttributeError):
            document_id = None

        return VerifiedEvidenceResponse(
            quote=evidence.quote,
            document_id=document_id,
            is_verified=False,
            coordinates=[],
        )


    # The quote is verified. Coordinate lookup is a separate step.
    try:
        raw_coordinates = find_evidence_coordinates(
            db=db,
            evidence=result,
        )

        coordinates = [
            EvidenceCoordinate(
                page_number=coordinate.page_number,
                x1=coordinate.x1,
                y1=coordinate.y1,
                x2=coordinate.x2,
                y2=coordinate.y2,
            )
            for coordinate in raw_coordinates
        ]

    except Exception:
        logger.exception(
            "Could not locate verified evidence in the PDF."
        )
        coordinates = []

    return VerifiedEvidenceResponse(
        quote=result.quote,
        document_id=result.document_id,
        is_verified=True,
        coordinates=coordinates,
    )