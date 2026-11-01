
from uuid import UUID

from pydantic import BaseModel, Field

from datetime import datetime


class CreateConversationRequest(BaseModel):
    document_ids: list[UUID] = Field(min_length=1)


class AddConversationDocumentsRequest(BaseModel):
    document_ids: list[UUID] = Field(min_length=1)


class ConversationResponse(BaseModel):
    conversation_id: UUID


class ConversationDocumentsResponse(BaseModel):
    conversation_id: UUID
    document_ids: list[UUID]


class ConversationDeleteResponse(BaseModel):
    conversation_id: UUID
    deleted: bool


class ConversationDocumentRemoveResponse(BaseModel):
    conversation_id: UUID
    document_id: UUID
    removed: bool
    
class ConversationSummaryResponse(BaseModel):
    conversation_id: UUID
    title: str | None
    created_at: datetime
    updated_at: datetime


class ConversationDetailResponse(BaseModel):
    conversation_id: UUID
    title: str | None
    created_at: datetime
    updated_at: datetime
    document_ids: list[UUID]
