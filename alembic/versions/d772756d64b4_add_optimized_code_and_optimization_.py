from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


def upgrade() -> None:
    op.add_column("messages", sa.Column("optimized_code", sa.Text(), nullable=True))
    op.add_column("messages", sa.Column("optimization_metrics", postgresql.JSONB(astext_type=sa.Text()), nullable=True))


def downgrade() -> None:
    op.drop_column("messages", "optimization_metrics")
    op.drop_column("messages", "optimized_code")