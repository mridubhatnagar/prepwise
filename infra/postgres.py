import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from config import config

logger = logging.getLogger(__name__)
engine = create_engine(config.DATABASE_URL) if config.DATABASE_URL else None

if not engine:
    logger.warning("DATABASE_URL is not set — SQLAlchemy engine will not be initialised")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine) if engine else None


class Base(DeclarativeBase):
    pass


def get_db():
    """FastAPI dependency that yields a database session and closes it after use."""
    if SessionLocal is None:
        raise RuntimeError("Database is not configured — DATABASE_URL is not set")
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
