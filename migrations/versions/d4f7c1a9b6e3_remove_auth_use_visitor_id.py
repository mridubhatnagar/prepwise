"""remove_auth_use_visitor_id

Revision ID: d4f7c1a9b6e3
Revises: 2b429b67f665
Create Date: 2026-08-25 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'd4f7c1a9b6e3'
down_revision: Union[str, Sequence[str], None] = '2b429b67f665'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint('chat_sessions_user_id_fkey', 'chat_sessions', type_='foreignkey')
    op.drop_constraint('chat_messages_user_id_fkey', 'chat_messages', type_='foreignkey')
    op.drop_constraint('feedback_user_id_fkey', 'feedback', type_='foreignkey')
    op.drop_constraint('spend_logs_user_id_fkey', 'spend_logs', type_='foreignkey')

    # Single-user app being reopened for anonymous access — existing history
    # under real user_ids is wiped rather than backfilled with a visitor_id.
    op.execute('TRUNCATE TABLE feedback, chat_messages, chat_sessions CASCADE')

    op.alter_column('chat_sessions', 'user_id', new_column_name='visitor_id')
    op.alter_column('chat_messages', 'user_id', new_column_name='visitor_id')
    op.alter_column('feedback', 'user_id', new_column_name='visitor_id')
    op.alter_column('spend_logs', 'user_id', new_column_name='visitor_id')

    op.execute(
        'ALTER INDEX ix_chat_messages_user_id_message_index '
        'RENAME TO ix_chat_messages_visitor_id_message_index'
    )
    op.execute('ALTER INDEX ix_feedback_user_id RENAME TO ix_feedback_visitor_id')
    op.execute('ALTER INDEX ix_spend_logs_user_id RENAME TO ix_spend_logs_visitor_id')

    op.drop_table('allowed_users')
    op.drop_table('access_attempts')
    op.drop_table('users')


def downgrade() -> None:
    op.create_table(
        'users',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('google_auth_id', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=True),
        sa.Column('avatar_url', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('google_auth_id'),
        sa.UniqueConstraint('email'),
    )
    op.create_table(
        'allowed_users',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('scope', sa.String(), nullable=False),
        sa.Column('added_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
    )
    op.create_table(
        'access_attempts',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('attempted_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )

    op.execute(
        'ALTER INDEX ix_chat_messages_visitor_id_message_index '
        'RENAME TO ix_chat_messages_user_id_message_index'
    )
    op.execute('ALTER INDEX ix_feedback_visitor_id RENAME TO ix_feedback_user_id')
    op.execute('ALTER INDEX ix_spend_logs_visitor_id RENAME TO ix_spend_logs_user_id')

    op.alter_column('chat_sessions', 'visitor_id', new_column_name='user_id')
    op.alter_column('chat_messages', 'visitor_id', new_column_name='user_id')
    op.alter_column('feedback', 'visitor_id', new_column_name='user_id')
    op.alter_column('spend_logs', 'visitor_id', new_column_name='user_id')

    op.create_foreign_key(
        'chat_sessions_user_id_fkey', 'chat_sessions', 'users', ['user_id'], ['id'], ondelete='CASCADE'
    )
    op.create_foreign_key(
        'chat_messages_user_id_fkey', 'chat_messages', 'users', ['user_id'], ['id'], ondelete='CASCADE'
    )
    op.create_foreign_key(
        'feedback_user_id_fkey', 'feedback', 'users', ['user_id'], ['id'], ondelete='CASCADE'
    )
    op.create_foreign_key(
        'spend_logs_user_id_fkey', 'spend_logs', 'users', ['user_id'], ['id'], ondelete='SET NULL'
    )
