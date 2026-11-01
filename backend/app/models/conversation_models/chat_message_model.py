
import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Enum as SQLAlchemyEnum, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.enums.chat_role import ChatRole

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.conversation_models.message_evidence_model import MessageEvidence


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    conversation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("conversations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    role: Mapped[ChatRole] = mapped_column(
        SQLAlchemyEnum(ChatRole, name="chat_role"),
        nullable=False,
    )

    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    
    
    evidences: Mapped[list["MessageEvidence"]] = relationship(
        back_populates="message",
        cascade="all, delete-orphan",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
