
from sqlalchemy.orm import Session

from app.schemas.agent_response_schema import (
    AgentResponse,
)
from app.models.document_model import Document
from app.services.conversation_service.quote_verification.evidence_verification import (
    verify_evidence_item,
)
from app.services.conversation_service.quote_verification.evidence_cordinates import (
    find_evidence_coordinates 
)
from app.schemas.evidence_verification import (
    VerifiedEvidence,
)
from app.schemas.verified_evidence import (
    EvidenceCoordinate,
    VerifiedEvidenceResult,
    VerifiedEvidenceResponse
)


def verify_agent_response_evidence(
    db: Session,
    agent_response: AgentResponse,
    selected_documents: list[Document],
) -> VerifiedEvidenceResult:
    verified_evidence: list[VerifiedEvidenceResponse] = []

    for evidence in agent_response.evidence:
        result: VerifiedEvidence | None = verify_evidence_item(
            db=db,
            evidence=evidence,
            selected_documents=selected_documents,
        )

        if result is None:
            continue

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

        verified_evidence.append(
            VerifiedEvidenceResponse(
                quote=result.quote,
                document_id=result.document_id,
                coordinates=coordinates,
            )
        )

    return VerifiedEvidenceResult(evidence=verified_evidence)
