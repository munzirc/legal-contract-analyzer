
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.conversation_models.conversation_model import Conversation
from app.schemas.chat import ChatResponse
from app.schemas.conversation import (
    CreateConversationRequest,
    AddConversationDocumentsRequest,
    ConversationResponse,
    ConversationDocumentsResponse,
    ConversationDeleteResponse,
    ConversationDocumentRemoveResponse,
    ConversationSummaryResponse,
    ConversationDetailResponse,
)
from app.services.conversation_service.conversation_service import (
    create_conversation,
    add_documents_to_conversation,
    remove_document_from_conversation,
    delete_conversation,
    ConversationNotFoundError,
    DocumentNotFoundError,
    DocumentNotReadyError,
    ConversationDocumentNotFoundError,
)

from app.services.conversation_service.conversation_service import (
    get_all_conversations as get_all_conversations_service,
    get_conversation_by_id as get_conversation_by_id_service,
    get_chat_history as get_chat_history_service
)


def create_conversation_controller(
    db: Session,
    request: CreateConversationRequest,
) -> ConversationResponse:
    try:
        conversation_id: UUID = create_conversation(
            db=db,
            document_ids=request.document_ids,
        )

        return ConversationResponse(conversation_id=conversation_id)

    except DocumentNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    except DocumentNotReadyError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


def add_documents_controller(
    db: Session,
    conversation_id: UUID,
    request: AddConversationDocumentsRequest,
) -> ConversationDocumentsResponse:
    try:
        added_ids: list[UUID] = add_documents_to_conversation(
            db=db,
            conversation_id=conversation_id,
            document_ids=request.document_ids,
        )

        return ConversationDocumentsResponse(
            conversation_id=conversation_id,
            document_ids=added_ids,
        )

    except ConversationNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    except DocumentNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    except DocumentNotReadyError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


def remove_document_controller(
    db: Session,
    conversation_id: UUID,
    document_id: UUID,
) -> ConversationDocumentsResponse:
    try:
        remaining_document_ids = remove_document_from_conversation(
            db=db,
            conversation_id=conversation_id,
            document_id=document_id,
        )

        return ConversationDocumentsResponse(
            conversation_id=conversation_id,
            document_ids=remaining_document_ids,
        )

    except ConversationNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    except ConversationDocumentNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


def delete_conversation_controller(
    db: Session,
    conversation_id: UUID,
) -> ConversationDeleteResponse:
    try:
        delete_conversation(
            db=db,
            conversation_id=conversation_id,
        )

        return ConversationDeleteResponse(
            conversation_id=conversation_id,
            deleted=True,
        )

    except ConversationNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc



def get_all_conversations_controller(
    db: Session,
) -> list[ConversationSummaryResponse]:
    return get_all_conversations_service(db=db)


def get_conversation_by_id_controller(
    db: Session,
    conversation_id: UUID,
) -> ConversationDetailResponse:
    try:
        return get_conversation_by_id_service(
            db=db,
            conversation_id=conversation_id,
        )
    except ConversationNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
        
def get_chat_history_controller(
    db: Session,
    conversation_id: UUID,
) -> ChatResponse:
    conversation = db.get(Conversation, conversation_id)

    if conversation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found.",
        )

    return get_chat_history_service(
        db=db,
        conversation_id=conversation_id,
    )