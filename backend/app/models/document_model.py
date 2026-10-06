import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Integer, String, Enum, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.enums.document_status import DocumentStatus
from app.enums.document_file_type import DocumentFileType


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    filename: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    file_type: Mapped[DocumentFileType] = mapped_column(
        Enum(
            DocumentFileType,
            name="document_file_type",
            native_enum=True
        ),
        nullable=False
    )
    
    original_storage_path: Mapped[str] = mapped_column(
        String,
        nullable=False
    )

    pdf_storage_path: Mapped[str] = mapped_column(
        String,
        nullable=False
    )
    
    canonical_text: Mapped[str] = mapped_column(
        Text,
        nullable=True
    )

    status: Mapped[DocumentStatus] = mapped_column(
        Enum(
            DocumentStatus,
            name="document_status",
            native_enum=True
        ),
        nullable=False
    )

    page_count: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )