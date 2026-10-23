import os

# Must be set before the app is imported.
os.environ.setdefault("DATABASE_URL", "postgresql+psycopg://rag:rag@localhost:5432/rag_test")
os.environ["EMBEDDING_PROVIDER"] = "fake"
os.environ["LLM_PROVIDER"] = "mock"
os.environ["JWT_SECRET"] = "test-secret"

import pytest  # noqa: E402
from sqlalchemy import text  # noqa: E402


@pytest.fixture(scope="session")
def client():
    from fastapi.testclient import TestClient

    from app.db import engine
    from app.main import app

    try:
        with engine.connect():
            pass
    except Exception:
        pytest.skip("PostgreSQL (pgvector) not reachable - run `make test` or start the db")

    with TestClient(app) as c:  # runs lifespan -> init_db
        with engine.begin() as conn:
            conn.execute(text("TRUNCATE users, documents, chunks RESTART IDENTITY CASCADE"))
        yield c
