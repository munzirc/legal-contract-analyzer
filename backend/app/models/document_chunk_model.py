import uuid
from datetime import datetime, timezone

from pgvector.sqlalchemy import Vector
from sqlalchemy import DateTime, ForeignKey, Integer, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False
    )

    chunk_index: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    section_number: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    section_title: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    text: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    start_offset: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    end_offset: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    page_start: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    page_end: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    embedding: Mapped[list[float] | None] = mapped_column(
        Vector(),
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    __table_args__ = (
        UniqueConstraint(
            "document_id",
            "chunk_index",
            name="uq_document_chunk_index"
        ),
    )