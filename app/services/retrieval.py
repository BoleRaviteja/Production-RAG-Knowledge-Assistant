from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Chunk, Document


@dataclass
class Hit:
    chunk_id: int
    document_id: int
    filename: str
    page: int | None
    chunk_index: int
    content: str
    score: float


def search(
    db: Session,
    query_vec: list[float],
    top_k: int,
    min_similarity: float,
    document_ids: list[int] | None = None,
) -> list[Hit]:
    distance = Chunk.embedding.cosine_distance(query_vec)
    stmt = (
        select(Chunk, Document.filename, distance.label("distance"))
        .join(Document, Document.id == Chunk.document_id)
        .where(Document.status == "ready")
        .order_by(distance)
        .limit(top_k)
    )
    if document_ids:
        stmt = stmt.where(Chunk.document_id.in_(document_ids))

    hits = [
        Hit(c.id, c.document_id, fname, c.page, c.chunk_index, c.content, 1.0 - float(dist))
        for c, fname, dist in db.execute(stmt).all()
    ]
    return [h for h in hits if h.score >= min_similarity]
