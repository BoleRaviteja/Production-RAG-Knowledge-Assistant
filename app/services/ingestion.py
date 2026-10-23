import io
import logging

from pypdf import PdfReader

from app.config import settings
from app.db import SessionLocal
from app.models import Chunk, Document
from app.services.chunking import chunk_text
from app.services.embeddings import embed_texts

logger = logging.getLogger(__name__)


def extract_pages(data: bytes, ext: str) -> list[tuple[int | None, str]]:
    """Return [(page_number | None, text)]. Page numbers are 1-based."""
    if ext == ".pdf":
        reader = PdfReader(io.BytesIO(data))
        return [(i + 1, _clean(p.extract_text() or "")) for i, p in enumerate(reader.pages)]
    return [(None, _clean(data.decode("utf-8", errors="replace")))]


def _clean(text: str) -> str:
    return text.replace("\x00", "")  # Postgres text columns reject NUL bytes


def process_document(doc_id: int, data: bytes, ext: str) -> None:
    """Background job: parse -> chunk (per page) -> embed -> store."""
    with SessionLocal() as db:
        doc = db.get(Document, doc_id)
        if doc is None:
            return
        try:
            doc.status = "processing"
            db.commit()

            pieces = [
                (page, chunk)
                for page, text in extract_pages(data, ext)
                for chunk in chunk_text(text, settings.chunk_size, settings.chunk_overlap)
            ]
            if not pieces:
                raise ValueError(
                    "No extractable text found (scanned PDFs need OCR, not supported)."
                )

            vectors = embed_texts([c for _, c in pieces])
            db.add_all(
                Chunk(document_id=doc_id, chunk_index=i, page=page, content=content, embedding=vec)
                for i, ((page, content), vec) in enumerate(zip(pieces, vectors, strict=True))
            )
            doc.status = "ready"
            doc.num_chunks = len(pieces)
            db.commit()
            logger.info("document_ingested", extra={"document_id": doc_id, "chunks": len(pieces)})
        except Exception as exc:
            db.rollback()
            logger.exception("document_ingestion_failed", extra={"document_id": doc_id})
            doc = db.get(Document, doc_id)
            if doc:
                doc.status = "failed"
                doc.error = str(exc)[:500]
                db.commit()
