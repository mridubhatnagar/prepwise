"""add_chat_sessions_and_feedback

Revision ID: a1b2c3d4e5f6
Revises: 543083756c00
Create Date: 2026-03-17 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = '543083756c00'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'chat_sessions',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_chat_sessions_user_id', 'chat_sessions', ['user_id'], unique=False)

    op.add_column(
        'chat_messages',
        sa.Column('session_id', sa.UUID(), nullable=True),
    )
    op.create_foreign_key(
        'fk_chat_messages_session_id',
        'chat_messages',
        'chat_sessions',
        ['session_id'],
        ['id'],
        ondelete='CASCADE',
    )

    op.drop_index('ix_chat_messages_user_id', table_name='chat_messages', if_exists=True)
    op.create_index(
        'ix_chat_messages_user_id_message_index',
        'chat_messages',
        ['user_id', 'message_index'],
        unique=False,
    )

    op.create_table(
        'feedback',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('message_id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('rating', sa.String(10), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['message_id'], ['chat_messages.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('message_id'),
    )
    op.create_index('ix_feedback_user_id', 'feedback', ['user_id'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_feedback_user_id', table_name='feedback')
    op.drop_table('feedback')

    op.drop_constraint('fk_chat_messages_session_id', 'chat_messages', type_='foreignkey')
    op.drop_index('ix_chat_messages_user_id_message_index', table_name='chat_messages')
    op.drop_column('chat_messages', 'session_id')
    op.create_index('ix_chat_messages_user_id', 'chat_messages', ['user_id'], unique=False)

    op.drop_index('ix_chat_sessions_user_id', table_name='chat_sessions')
    op.drop_table('chat_sessions')
