from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.enums.document_file_type import DocumentFileType
from app.enums.document_status import DocumentStatus


class DocumentListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    filename: str
    file_type: DocumentFileType
    status: DocumentStatus
    page_count: int | None
    created_at: datetime