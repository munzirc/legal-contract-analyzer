"""add embedding piece status and text

Revision ID: f6a971afef49
Revises: a857bda981de
Create Date: 2026-10-17 12:46:22.672598

"""
from typing import Sequence, Union
from pgvector.sqlalchemy import Vector

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f6a971afef49'
down_revision: Union[str, Sequence[str], None] = 'a857bda981de'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None



def upgrade() -> None:
    embedding_status = sa.Enum(
        "PENDING",
        "COMPLETED",
        "FAILED",
        name="embedding_status",
    )

    # Create the PostgreSQL enum type before using it.
    embedding_status.create(op.get_bind(), checkfirst=True)

    op.add_column(
        "chunk_embeddings",
        sa.Column("text", sa.Text(), nullable=False),
    )

    op.add_column(
        "chunk_embeddings",
        sa.Column(
            "status",
            embedding_status,
            nullable=False,
            server_default="PENDING",
        ),
    )

    op.add_column(
        "chunk_embeddings",
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )

    op.alter_column(
        "chunk_embeddings",
        "embedding",
        existing_type=Vector(768),
        nullable=True,
    )

    # The database default initializes existing/new rows.
    # The application model supplies its own default as well.
    op.alter_column(
        "chunk_embeddings",
        "status",
        server_default=None,
    )
    op.alter_column(
        "chunk_embeddings",
        "updated_at",
        server_default=None,
    )


def downgrade() -> None:
    op.alter_column(
        "chunk_embeddings",
        "embedding",
        existing_type=Vector(768),
        nullable=False,
    )

    op.drop_column("chunk_embeddings", "updated_at")
    op.drop_column("chunk_embeddings", "status")
    op.drop_column("chunk_embeddings", "text")

    sa.Enum(
        "PENDING",
        "COMPLETED",
        "FAILED",
        name="embedding_status",
    ).drop(op.get_bind(), checkfirst=True)
