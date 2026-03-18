"""fix_messagerole_enum_to_uppercase

Revision ID: 2b429b67f665
Revises: a1b2c3d4e5f6
Create Date: 2026-03-18 17:38:54.778077

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2b429b67f665'
down_revision: Union[str, Sequence[str], None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TYPE messagerole RENAME VALUE 'user' TO 'USER'")
    op.execute("ALTER TYPE messagerole RENAME VALUE 'assistant' TO 'ASSISTANT'")


def downgrade() -> None:
    op.execute("ALTER TYPE messagerole RENAME VALUE 'USER' TO 'user'")
    op.execute("ALTER TYPE messagerole RENAME VALUE 'ASSISTANT' TO 'assistant'")
