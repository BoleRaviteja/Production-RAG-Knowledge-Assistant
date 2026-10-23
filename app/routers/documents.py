from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, HTTPException, UploadFile, status
from sqlalchemy import select

from app.config import settings
from app.deps import AdminUser, CurrentUser, DbSession
from app.models import Document
from app.schemas import DocumentOut
from app.services.ingestion import process_document

router = APIRouter(prefix="/documents", tags=["documents"])
ALLOWED_EXT = {".pdf", ".txt", ".md"}


@router.post("", response_model=DocumentOut, status_code=status.HTTP_202_ACCEPTED)
def upload_document(file: UploadFile, background: BackgroundTasks, admin: AdminUser, db: DbSession):
    """Upload a PDF/TXT/MD file. Chunking + embedding run in the background;
    poll GET /documents/{id} until status == 'ready'."""
    name = Path(file.filename or "").name
    ext = Path(name).suffix.lower()
    if ext not in ALLOWED_EXT:
        raise HTTPException(415, f"Unsupported file type. Allowed: {sorted(ALLOWED_EXT)}")

    limit = settings.max_upload_mb * 1024 * 1024
    data = file.file.read(limit + 1)
    if not data:
        raise HTTPException(400, "Empty file")
    if len(data) > limit:
        raise HTTPException(413, f"File larger than {settings.max_upload_mb} MB")

    doc = Document(
        filename=name,
        content_type=file.content_type,
        size_bytes=len(data),
        status="pending",
        uploaded_by=admin.id,
    )
    db.add(doc)
    db.commit()
    background.add_task(process_document, doc.id, data, ext)
    return doc


@router.get("", response_model=list[DocumentOut])
def list_documents(_: CurrentUser, db: DbSession):
    return db.scalars(select(Document).order_by(Document.created_at.desc())).all()


@router.get("/{doc_id}", response_model=DocumentOut)
def get_document(doc_id: int, _: CurrentUser, db: DbSession):
    doc = db.get(Document, doc_id)
    if doc is None:
        raise HTTPException(404, "Document not found")
    return doc


@router.delete("/{doc_id}", status_code=204)
def delete_document(doc_id: int, _: AdminUser, db: DbSession):
    doc = db.get(Document, doc_id)
    if doc is None:
        raise HTTPException(404, "Document not found")
    db.delete(doc)
    db.commit()
