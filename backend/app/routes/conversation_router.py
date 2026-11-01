
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.chat import ChatResponse
from app.schemas.conversation import  (
    CreateConversationRequest,
    AddConversationDocumentsRequest,
    ConversationResponse,
    ConversationDocumentsResponse,
    ConversationDeleteResponse,
    ConversationDocumentRemoveResponse,
    ConversationDetailResponse,
    ConversationSummaryResponse
)
from app.controllers.conversation_controller import (
    create_conversation_controller,
    add_documents_controller,
    remove_document_controller,
    delete_conversation_controller,
    get_all_conversations_controller,
    get_conversation_by_id_controller,
    get_chat_history_controller
)

router = APIRouter(
    prefix="/api/conversations",
    tags=["Conversations"],
)


@router.post(
    "",
    response_model=ConversationResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_conversation_route(
    request: CreateConversationRequest,
    db: Session = Depends(get_db),
) -> ConversationResponse:
    return create_conversation_controller(db, request)


@router.post(
    "/{conversation_id}/documents",
    response_model=ConversationDocumentsResponse,
    status_code=status.HTTP_200_OK,
)
def add_documents_route(
    conversation_id: UUID,
    request: AddConversationDocumentsRequest,
    db: Session = Depends(get_db),
) -> ConversationDocumentsResponse:
    return add_documents_controller(db, conversation_id, request)


@router.delete(
    "/{conversation_id}/document/{document_id}",
    response_model=ConversationDocumentsResponse,
)
def remove_document_route(
    conversation_id: UUID,
    document_id: UUID,
    db: Session = Depends(get_db),
) -> ConversationDocumentsResponse:
    return remove_document_controller(
        db,
        conversation_id,
        document_id,
    )


@router.delete(
    "/{conversation_id}",
    response_model=ConversationDeleteResponse,
)
def delete_conversation_route(
    conversation_id: UUID,
    db: Session = Depends(get_db),
) -> ConversationDeleteResponse:
    return delete_conversation_controller(db, conversation_id)


@router.get(
    "",
    response_model=list[ConversationSummaryResponse],
)
def get_all_conversations(
    db: Session = Depends(get_db),
) -> list[ConversationSummaryResponse]:
    return get_all_conversations_controller(db=db)


@router.get(
    "/{conversation_id}",
    response_model=ConversationDetailResponse,
)
def get_conversation_by_id(
    conversation_id: UUID,
    db: Session = Depends(get_db),
) -> ConversationDetailResponse:
    return get_conversation_by_id_controller(
        db=db,
        conversation_id=conversation_id,
    )
    
@router.get(
    "/{conversation_id}/messages",
    response_model=ChatResponse,
)
def get_chat_history(
    conversation_id: UUID,
    db: Session = Depends(get_db),
) -> ChatResponse:
    return get_chat_history_controller(
        db=db,
        conversation_id=conversation_id,
    )