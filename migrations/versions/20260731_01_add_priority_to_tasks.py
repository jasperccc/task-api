"""add priority to tasks

Revision ID: 20260731_01
Revises: 20260729_01
Create Date: 2026-07-31 10:07:16.200244

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260731_01"
down_revision: Union[str, Sequence[str], None] = "20260729_01"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "tasks",
        sa.Column(
            "priority",
            sa.Integer(),
            nullable=False,
            server_default="1",
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("tasks", "priority")
