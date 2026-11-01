
from uuid import UUID, uuid4

from sqlalchemy import delete, select
from sqlalchemy.orm import Session, selectinload

from app.models.document_model import Document
from app.models.conversation_models.conversation_model import Conversation
from app.models.conversation_models.conversation_document_model import ConversationDocument
from app.enums.document_status import DocumentStatus
from app.exceptions.conversation_exceptions import (
    DocumentNotReadyError,
    ConversationDocumentNotFoundError,
    DocumentNotFoundError,
    ConversationNotFoundError  
)
from app.schemas.chat import (
    ChatResponse,
    ChatMessageResponse,
    EvidenceResponse,
    EvidenceRegionResponse
)
from app.models.conversation_models.chat_message_model import ChatMessage
from app.models.conversation_models.message_evidence_model import MessageEvidence


from app.schemas.conversation import ConversationSummaryResponse, ConversationDetailResponse 



def _get_ready_documents(
    db: Session,
    document_ids: list[UUID],
) -> list[Document]:
    unique_ids: list[UUID] = list(dict.fromkeys(document_ids))

    statement = select(Document).where(Document.id.in_(unique_ids))
    documents: list[Document] = list(db.scalars(statement).all())

    documents_by_id: dict[UUID, Document] = {
        document.id: document for document in documents
    }

    missing_ids: list[UUID] = [
        document_id
        for document_id in unique_ids
        if document_id not in documents_by_id
    ]

    if missing_ids:
        raise DocumentNotFoundError(
            f"Documents not found: {missing_ids}"
        )

    not_ready_ids: list[UUID] = [
        document_id
        for document_id in unique_ids
        if documents_by_id[document_id].status != DocumentStatus.READY
    ]

    if not not_ready_ids:
        return documents

    raise DocumentNotReadyError(
        f"Documents are not READY: {not_ready_ids}"
    )


def create_conversation(
    db: Session,
    document_ids: list[UUID],
) -> UUID:
    if not document_ids:
        raise ValueError("At least one document is required.")

    try:
        _get_ready_documents(db, document_ids)

        conversation_id: UUID = uuid4()

        conversation = Conversation(id=conversation_id)
        db.add(conversation)
        db.flush()

        associations: list[ConversationDocument] = [
            ConversationDocument(
                conversation_id=conversation_id,
                document_id=document_id,
            )
            for document_id in dict.fromkeys(document_ids)
        ]

        db.add_all(associations)
        db.commit()

        return conversation_id

    except Exception:
        db.rollback()
        raise


def add_documents_to_conversation(
    db: Session,
    conversation_id: UUID,
    document_ids: list[UUID],
) -> list[UUID]:
    if not document_ids:
        raise ValueError("At least one document is required.")
    
    

    try:
        conversation: Conversation | None = db.get(
            Conversation,
            conversation_id,
        )

        if conversation is None:
            raise ConversationNotFoundError(
                f"Conversation not found: {conversation_id}"
            )

        _get_ready_documents(db, document_ids)

        unique_ids: list[UUID] = list(dict.fromkeys(document_ids))

        existing_statement = select(
            ConversationDocument.document_id
        ).where(
            ConversationDocument.conversation_id == conversation_id,
            ConversationDocument.document_id.in_(unique_ids),
        )

        existing_ids: set[UUID] = set(
            db.scalars(existing_statement).all()
        )

        new_ids: list[UUID] = [
            document_id
            for document_id in unique_ids
            if document_id not in existing_ids
        ]

        associations: list[ConversationDocument] = [
            ConversationDocument(
                conversation_id=conversation_id,
                document_id=document_id,
            )
            for document_id in new_ids
        ]

        db.add_all(associations)
        db.commit()
        
        print("Conversation ID:", conversation_id)
        print("Requested IDs:", document_ids)
        print("Unique IDs:", unique_ids)
        print("Existing IDs:", existing_ids)
        print("New IDs:", new_ids)

        # Return every document currently attached to the conversation.
        statement = select(
            ConversationDocument.document_id
        ).where(
            ConversationDocument.conversation_id == conversation_id
        )

        return list(db.scalars(statement).all())

    except Exception:
        db.rollback()
        raise


def remove_document_from_conversation(
    db: Session,
    conversation_id: UUID,
    document_id: UUID,
) -> list[UUID]:
    try:
        conversation: Conversation | None = db.get(
            Conversation,
            conversation_id,
        )

        if conversation is None:
            raise ConversationNotFoundError(
                f"Conversation not found: {conversation_id}"
            )

        association: ConversationDocument | None = db.get(
            ConversationDocument,
            (conversation_id, document_id),
        )

        if association is None:
            raise ConversationDocumentNotFoundError(
                "This document is not associated with the conversation."
            )

        db.delete(association)
        db.commit()

        statement = select(
            ConversationDocument.document_id
        ).where(
            ConversationDocument.conversation_id == conversation_id
        )

        return list(db.scalars(statement).all())

    except Exception:
        db.rollback()
        raise


def delete_conversation(
    db: Session,
    conversation_id: UUID,
) -> None:
    try:
        conversation: Conversation | None = db.get(
            Conversation,
            conversation_id,
        )

        if conversation is None:
            raise ConversationNotFoundError(
                f"Conversation not found: {conversation_id}"
            )

        # Remove associations explicitly.
        association_statement = delete(ConversationDocument).where(
            ConversationDocument.conversation_id == conversation_id
        )
        db.execute(association_statement)

        db.delete(conversation)
        db.commit()

    except Exception:
        db.rollback()
        raise

def get_all_conversations(
    db: Session,
) -> list[ConversationSummaryResponse]:
    conversations: list[Conversation] = list(
        db.scalars(
            select(Conversation).order_by(
                Conversation.updated_at.desc()
            )
        ).all()
    )

    if not conversations:
        return []


    return [
        ConversationSummaryResponse(
            conversation_id=conversation.id,
            title=conversation.title,
            created_at=conversation.created_at,
            updated_at=conversation.updated_at,
        )
        for conversation in conversations
    ]


def get_conversation_by_id(
    db: Session,
    conversation_id: UUID,
) -> ConversationDetailResponse:
    conversation: Conversation | None = db.get(
        Conversation,
        conversation_id,
    )

    if conversation is None:
        raise ConversationNotFoundError(
            f"Conversation not found: {conversation_id}"
        )

    association_statement = select(
        ConversationDocument.document_id
    ).where(
        ConversationDocument.conversation_id == conversation_id
    )

    document_ids: list[UUID] = list(
        db.scalars(association_statement).all()
    )

    return ConversationDetailResponse(
        conversation_id=conversation.id,
        title=conversation.title,
        created_at=conversation.created_at,
        updated_at=conversation.updated_at,
        document_ids=document_ids,
    )
    


def get_chat_history(
    db: Session,
    conversation_id: UUID,
) -> ChatResponse:

    # Fetch document IDs associated with this conversation.
    document_ids = list(db.scalars(
        select(ConversationDocument.document_id)
        .where(
            ConversationDocument.conversation_id == conversation_id
        )
    ).all())

    statement = (
        select(ChatMessage)
        .where(ChatMessage.conversation_id == conversation_id)
        .options(
            selectinload(ChatMessage.evidences).selectinload(
                MessageEvidence.regions
            )
        )
        .order_by(
            ChatMessage.created_at.asc(),
            ChatMessage.id.asc(),
        )
    )

    messages = db.scalars(statement).all()

    return ChatResponse(
        conversation_id=conversation_id,
        document_ids=document_ids,
        messages=[
            ChatMessageResponse(
                id=message.id,
                role=message.role.value,
                content=message.content,
                created_at=message.created_at,
                evidence=[
                    EvidenceResponse(
                        id=evidence.id,
                        document_id=evidence.document_id,
                        quote=evidence.quote,
                        is_verified=evidence.is_verified,
                        regions=[
                            EvidenceRegionResponse(
                                page_number=region.page_number,
                                x1=region.x1,
                                y1=region.y1,
                                x2=region.x2,
                                y2=region.y2,
                            )
                            for region in evidence.regions
                        ],
                    )
                    for evidence in message.evidences
                ],
            )
            for message in messages
        ],
    )