"""add project status and updated timestamp

Revision ID: 0bec46c95433
Revises: 6a1e4b8ada24
Create Date: 2026-08-13 00:18:12.674917

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.

revision: str = "0bec46c95433"
down_revision: Union[str, Sequence[str], None] = "6a1e4b8ada24"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    # Add columns as nullable first so existing rows are safe.
    op.add_column(
        "projects",
        sa.Column(
            "status",
            sa.String(length=50),
            nullable=True,
        ),
    )

    op.add_column(
        "projects",
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
    )

    # Populate existing projects.
    op.execute(
        "UPDATE projects SET status = 'active' WHERE status IS NULL"
    )

    op.execute(
        "UPDATE projects SET updated_at = created_at WHERE updated_at IS NULL"
    )

    # Make the columns required after existing rows are populated.
    op.alter_column(
        "projects",
        "status",
        existing_type=sa.String(length=50),
        nullable=False,
    )

    op.alter_column(
        "projects",
        "updated_at",
        existing_type=sa.DateTime(timezone=True),
        nullable=False,
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_column("projects", "updated_at")
    op.drop_column("projects", "status")