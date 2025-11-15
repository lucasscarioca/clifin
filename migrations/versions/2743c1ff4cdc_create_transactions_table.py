"""create transactions table

Revision ID: 2743c1ff4cdc
Revises:
Create Date: 2025-11-01 11:28:23.660555

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "2743c1ff4cdc"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "transactions",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("amount", sa.Float(), nullable=False),
        sa.Column("category", sa.String(), nullable=False),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("date", sa.String(), nullable=False),
        sa.Column(
            "created_at",
            sa.String(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("transactions")
