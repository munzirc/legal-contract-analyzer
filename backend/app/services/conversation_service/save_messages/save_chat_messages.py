
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.conversation_models.chat_message_model import (
    ChatMessage,
    ChatRole,
)
from app.models.conversation_models.message_evidence_model import MessageEvidence
from app.models.conversation_models.evidence_region_model import EvidenceRegion
from app.schemas.verified_evidence import VerifiedEvidenceResult


def persist_chat_turn(
    db: Session,
    conversation_id: UUID,
    user_question: str,
    assistant_answer: str,
    verified_result: VerifiedEvidenceResult,
) -> tuple[ChatMessage, ChatMessage]:
    user_message = ChatMessage(
        conversation_id=conversation_id,
        role=ChatRole.USER,
        content=user_question,
    )

    assistant_message = ChatMessage(
        conversation_id=conversation_id,
        role=ChatRole.ASSISTANT,
        content=assistant_answer,
        evidences=[
            MessageEvidence(
                document_id=item.document_id,
                quote=item.quote,
                is_verified=True,
                regions=[
                    EvidenceRegion(
                        page_number=coordinate.page_number,
                        x1=coordinate.x1,
                        y1=coordinate.y1,
                        x2=coordinate.x2,
                        y2=coordinate.y2,
                    )
                    for coordinate in item.coordinates
                ],
            )
            for item in verified_result.evidence
        ],
    )

    try:
        db.add_all([user_message, assistant_message])
        db.commit()

        db.refresh(user_message)
        db.refresh(assistant_message)

        return user_message, assistant_message

    except Exception:
        db.rollback()
        raise
