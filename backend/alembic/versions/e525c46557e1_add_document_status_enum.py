"""add document status enum

Revision ID: e525c46557e1
Revises: 4aa6c65760de
Create Date: 2026-10-03 12:12:34.757663

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e525c46557e1'
down_revision: Union[str, Sequence[str], None] = '4aa6c65760de'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    document_status = sa.Enum(
        "UPLOADED",
        "EXTRACTING",
        "VALIDATING",
        "CHUNKING",
        "EMBEDDING",
        "READY",
        "REJECTED",
        "FAILED",
        name="document_status",
    )

    document_status.create(op.get_bind(), checkfirst=True)
    op.alter_column(
        "documents",
        "status",
        existing_type=sa.String(length=30),
        type_=document_status,
        existing_nullable=False,
        postgresql_using="status::document_status",
    )


def downgrade() -> None:
    op.alter_column(
        "documents",
        "status",
        existing_type=sa.Enum(
            "UPLOADED",
            "EXTRACTING",
            "VALIDATING",
            "CHUNKING",
            "EMBEDDING",
            "READY",
            "REJECTED",
            "FAILED",
            name="document_status",
        ),
        type_=sa.String(length=30),
        existing_nullable=False,
    )

    sa.Enum(
        "UPLOADED",
        "EXTRACTING",
        "VALIDATING",
        "CHUNKING",
        "EMBEDDING",
        "READY",
        "REJECTED",
        "FAILED",
        name="document_status",
    ).drop(op.get_bind(), checkfirst=True)
