import logging
import time
import uuid
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text

from app.config import settings
from app.db import engine, init_db
from app.logging_config import setup_logging
from app.routers import auth, documents, query

setup_logging(settings.log_level)
logger = logging.getLogger("app")
STATIC = Path(__file__).parent / "static"


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    logger.info("startup", extra={"environment": settings.environment})
    yield


app = FastAPI(title=settings.app_name, version="1.0.0", lifespan=lifespan)


@app.middleware("http")
async def access_log(request: Request, call_next):
    rid = request.headers.get("x-request-id") or uuid.uuid4().hex
    start = time.perf_counter()
    try:
        response = await call_next(request)
    except Exception:
        logger.exception("unhandled_error", extra={"request_id": rid, "path": request.url.path})
        raise
    response.headers["x-request-id"] = rid
    if request.url.path not in ("/health", "/ready"):  # keep probe noise out of logs
        logger.info(
            "request",
            extra={
                "request_id": rid,
                "method": request.method,
                "path": request.url.path,
                "status": response.status_code,
                "duration_ms": int((time.perf_counter() - start) * 1000),
            },
        )
    return response


@app.get("/health", tags=["ops"])
def health():
    """Liveness probe."""
    return {"status": "ok"}


@app.get("/ready", tags=["ops"])
def ready():
    """Readiness probe - verifies the DB is reachable."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception as exc:
        raise HTTPException(503, "database unavailable") from exc
    return {"status": "ready"}


app.include_router(auth.router, prefix="/api/v1")
app.include_router(documents.router, prefix="/api/v1")
app.include_router(query.router, prefix="/api/v1")
app.mount("/static", StaticFiles(directory=STATIC), name="static")


@app.get("/", include_in_schema=False)
def ui():
    return FileResponse(STATIC / "index.html")
