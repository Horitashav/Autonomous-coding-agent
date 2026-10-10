"""Add optimized_code and optimization_metrics

Revision ID: 4e4fbca0e0cd
Revises: ef2ce988bd04
Create Date: 2026-10-10 16:34:19.387656

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4e4fbca0e0cd'
down_revision: Union[str, Sequence[str], None] = 'ef2ce988bd04'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
