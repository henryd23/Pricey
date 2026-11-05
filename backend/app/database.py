"""Database configuration and session management."""

import os
from pathlib import Path
from typing import Generator
from sqlmodel import SQLModel, Session, create_engine

# Resolve project root and database path
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DB_PATH = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'pricey.db'}")

# Ensure connect_args for SQLite multi-thread FastAPI support
connect_args = {"check_same_thread": False} if DB_PATH.startswith("sqlite") else {}

engine = create_engine(DB_PATH, echo=False, connect_args=connect_args)


def init_db() -> None:
    """Creates database tables if they do not exist."""
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    """Dependency for providing a transactional database session."""
    with Session(engine) as session:
        yield session

