"""Database — Production PostgreSQL connection and session management via SQLAlchemy."""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Explicitly specify psycopg2 driver
DEFAULT_PG_URL = (
    "postgresql+psycopg2://agent_admin:agent_secret_password@localhost:5432/agent_production_db"
)
DATABASE_URL = os.getenv("DATABASE_URL", DEFAULT_PG_URL)

engine = create_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    echo=False,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """FastAPI dependency that provides an isolated database session per request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()