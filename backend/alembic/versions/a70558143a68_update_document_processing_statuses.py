"""update document processing statuses

Revision ID: a70558143a68
Revises: aeba8151900d
Create Date: 2026-10-27 11:58:58.125165

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a70558143a68'
down_revision: Union[str, Sequence[str], None] = 'aeba8151900d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    new_values = [
        "EXTRACTION_FAILED",
        "STRUCTURE_DETECTION_FAILED",
        "CHUNKING_FAILED",
        "EMBEDDING_PIECES",
        "EMBEDDING_PIECES_FAILED",
        "EMBEDDING_FAILED",
    ]

    for value in new_values:
        op.execute(
            f"ALTER TYPE document_status "
            f"ADD VALUE IF NOT EXISTS '{value}'"
        )


def downgrade() -> None:
    # PostgreSQL does not directly support removing individual
    # enum values. Keep the values in the database on downgrade.
    pass