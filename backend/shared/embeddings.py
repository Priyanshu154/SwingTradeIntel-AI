"""Hand-rolled vector math — no managed vector DB for this demo scale."""

from __future__ import annotations

import math


def cosine_similarity(a: list[float], b: list[float]) -> float:
    if not a or not b or len(a) != len(b):
        return -1.0
    dot = 0.0
    na = 0.0
    nb = 0.0
    for x, y in zip(a, b):
        dot += x * y
        na += x * x
        nb += y * y
    denom = math.sqrt(na) * math.sqrt(nb)
    if denom == 0:
        return -1.0
    return dot / denom


def top_k_similar(
    query_embedding: list[float],
    articles: list[dict],
    k: int = 5,
) -> list[dict]:
    scored: list[tuple[float, dict]] = []
    for article in articles:
        emb = article.get("embedding") or []
        score = cosine_similarity(query_embedding, emb)
        scored.append((score, article))
    scored.sort(key=lambda pair: pair[0], reverse=True)
    return [item for _, item in scored[:k]]
