from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.conversation_models.conversation_model import Conversation
from app.models.conversation_models.conversation_document_model import ConversationDocument
from app.exceptions.conversation_exceptions import (
    ConversationNotFoundError,
    ConversationHasNoDocumentsError,
    DocumentNotReadyError,
    DocumentNotFoundError
)
from app.models.document_model import Document
from app.enums.document_status import DocumentStatus


def validate_conversation(
    db: Session,
    conversation_id: UUID,
) -> tuple[Conversation, list[Document]]:
    conversation: Conversation | None = db.get(
        Conversation,
        conversation_id,
    )

    if conversation is None:
        raise ConversationNotFoundError(
            f"Conversation {conversation_id} not found."
        )

    statement = (
        select(Document)
        .join(
            ConversationDocument,
            ConversationDocument.document_id == Document.id,
        )
        .where(
            ConversationDocument.conversation_id == conversation.id,
        )
        .order_by(Document.created_at, Document.id)
    )

    documents: list[Document] = list(
        db.scalars(statement).all()
    )

    if not documents:
        raise ConversationHasNoDocumentsError(
            "This conversation has no associated documents."
        )

    for document in documents:
        if document.status != DocumentStatus.READY:
            raise DocumentNotReadyError(
                f"Document '{document.filename}' is not ready."
            )

    return conversation, documents

def generate_conversation_title(message: str) -> str:
    title = " ".join(message.split()).strip()

    max_length = 80

    if len(title) > max_length:
        title = title[:max_length - 3].rstrip() + "..."

    return title or "New Conversation"

def create_or_validate_conversation(
    db: Session,
    conversation_id: UUID | None,
    document_ids: list[UUID],
    message: str,
) -> tuple[Conversation, list[Document]]:

    # Existing conversation
    if conversation_id is not None:
        return validate_conversation(
            db=db,
            conversation_id=conversation_id,
        )

    # New conversation
    if not document_ids:
        raise ConversationHasNoDocumentsError(
            "Please select at least one processed contract before starting a conversation."
        )

    # Remove duplicate IDs while preserving their order.
    unique_document_ids = list(dict.fromkeys(document_ids))

    statement = (
        select(Document)
        .where(Document.id.in_(unique_document_ids))
        .order_by(Document.created_at, Document.id)
    )

    documents = list(db.scalars(statement).all())

    # Ensure every requested document exists.
    retrieved_ids = {document.id for document in documents}
    missing_ids = set(unique_document_ids) - retrieved_ids

    if missing_ids:
        raise DocumentNotFoundError(
            "One or more selected documents could not be found."
        )

    # Ensure all documents are ready.
    for document in documents:
        if document.status != DocumentStatus.READY:
            raise DocumentNotReadyError(
                f"Document '{document.filename}' is not ready."
            )

    try:
        conversation = Conversation(
            title=generate_conversation_title(message),
        )

        db.add(conversation)
        db.flush()

        associations = [
            ConversationDocument(
                conversation_id=conversation.id,
                document_id=document.id,
            )
            for document in documents
        ]

        db.add_all(associations)
        db.commit()
        db.refresh(conversation)

        return conversation, documents

    except Exception:
        db.rollback()
        raise