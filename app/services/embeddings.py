import hashlib
import math
import re

import httpx

from app.config import settings

BATCH = 64


class EmbeddingError(RuntimeError):
    pass


def embed_texts(texts: list[str]) -> list[list[float]]:
    if not texts:
        return []
    if settings.embedding_provider == "fake":
        return [_fake_embed(t) for t in texts]
    return _openai_embed(texts)


def _openai_embed(texts: list[str]) -> list[list[float]]:
    if not settings.openai_api_key:
        raise EmbeddingError("OPENAI_API_KEY is not set")
    out: list[list[float]] = []
    with httpx.Client(timeout=60) as client:
        for i in range(0, len(texts), BATCH):
            batch = texts[i : i + BATCH]
            resp = client.post(
                f"{settings.openai_base_url}/embeddings",
                headers={"Authorization": f"Bearer {settings.openai_api_key}"},
                json={"model": settings.embedding_model, "input": batch},
            )
            if resp.status_code != 200:
                raise EmbeddingError(f"Embedding API error {resp.status_code}: {resp.text[:200]}")
            data = sorted(resp.json()["data"], key=lambda d: d["index"])
            out.extend(d["embedding"] for d in data)
    return out


def _fake_embed(text: str) -> list[float]:
    """Deterministic hashing-trick embedding. NOT semantic - for tests/offline demos only."""
    dim = settings.embedding_dim
    vec = [0.0] * dim
    for token in re.findall(r"\w+", text.lower()):
        h = int(hashlib.md5(token.encode()).hexdigest(), 16)
        vec[h % dim] += 1.0 if (h >> 64) & 1 else -1.0
    norm = math.sqrt(sum(v * v for v in vec)) or 1.0
    return [v / norm for v in vec]
