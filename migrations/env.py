import os
from logging.config import fileConfig

from sqlalchemy import create_engine, pool
from alembic import context

# Alembic Config object
config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Import all ORM models so Alembic's autogenerate can detect them.
# Base must be imported first; model imports register their tables on Base.metadata.
from infra.postgres import Base  # noqa: E402
import chat.models  # noqa: E402, F401
import spend.models  # noqa: E402, F401
import feedback.models  # noqa: E402, F401

target_metadata = Base.metadata


def _get_engine():
    """Build a SQLAlchemy engine from DATABASE_URL env var.

    Using create_engine directly (rather than engine_from_config) avoids
    ConfigParser percent-interpolation issues with special characters in URLs.
    """
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL environment variable is not set")
    return create_engine(database_url, poolclass=pool.NullPool)


def run_migrations_offline() -> None:
    """Run migrations without a live DB connection (generates SQL to stdout)."""
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL environment variable is not set")
    context.configure(
        url=database_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations against a live DB connection."""
    connectable = _get_engine()
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
