"""Add optimized code and optimization metrics to messages."""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "d772756d64b4"
down_revision: Union[str, Sequence[str], None] = "4e4fbca0e0cd"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("messages", sa.Column("optimized_code", sa.Text(), nullable=True))
    op.add_column(
        "messages",
        sa.Column("optimization_metrics", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("messages", "optimization_metrics")
    op.drop_column("messages", "optimized_code")