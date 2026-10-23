from collections.abc import Iterator

from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import settings

engine = create_engine(settings.database_url, pool_pre_ping=True, pool_size=5, max_overflow=10)
SessionLocal = sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


def get_db() -> Iterator[Session]:
    with SessionLocal() as session:
        yield session


def init_db() -> None:
    """Create the pgvector extension + tables. The advisory lock makes this safe
    when several replicas start at the same time."""
    from app import models  # noqa: F401  (register tables)

    with engine.begin() as conn:
        conn.execute(text("SELECT pg_advisory_xact_lock(727274)"))
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        Base.metadata.create_all(conn)
