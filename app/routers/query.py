import logging
import re
import time

from fastapi import APIRouter, HTTPException

from app.config import settings
from app.deps import CurrentUser, DbSession
from app.schemas import QueryRequest, QueryResponse, Source
from app.services.embeddings import EmbeddingError, embed_texts
from app.services.llm import NO_ANSWER, LLMError, generate_answer
from app.services.retrieval import search

router = APIRouter(tags=["query"])
logger = logging.getLogger(__name__)


@router.post("/query", response_model=QueryResponse)
def ask(req: QueryRequest, user: CurrentUser, db: DbSession):
    """Embed question -> vector search -> grounded LLM answer with citations."""
    start = time.perf_counter()
    try:
        qvec = embed_texts([req.question])[0]
        hits = search(
            db, qvec, req.top_k or settings.top_k, settings.min_similarity, req.document_ids
        )
        if not hits:  # nothing relevant: skip the LLM entirely (cheaper + can't hallucinate)
            answer, model = NO_ANSWER, "none"
        else:
            answer, model = generate_answer(req.question, hits), settings.llm_model
    except (EmbeddingError, LLMError) as exc:
        logger.error("upstream_ai_error", extra={"error": str(exc)})
        raise HTTPException(502, "AI provider error, please retry") from exc

    cited = {int(n) for n in re.findall(r"\[(\d+)\]", answer)}
    sources = [
        Source(
            id=i,
            document_id=h.document_id,
            filename=h.filename,
            page=h.page,
            chunk_index=h.chunk_index,
            score=round(h.score, 4),
            snippet=h.content[:400],
            cited=i in cited,
        )
        for i, h in enumerate(hits, 1)
    ]
    latency = int((time.perf_counter() - start) * 1000)
    logger.info(
        "query_answered",
        extra={"user_id": user.id, "hits": len(hits), "latency_ms": latency, "model": model},
    )
    return QueryResponse(answer=answer, sources=sources, model=model, latency_ms=latency)
