"""Agent 1 — News RAG: S3 JSON corpus + Titan embed + cosine top-k + Haiku."""

from __future__ import annotations

import json
import logging
import os
from typing import Any

import boto3

from shared.bedrock import embed_text, invoke_haiku
from shared.embeddings import top_k_similar

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

NEWS_BUCKET = os.environ.get("NEWS_BUCKET", "")
TOP_K = int(os.environ.get("NEWS_TOP_K", "5"))

SYSTEM = (
    "You are a market-news sentiment analyst for Nifty 50 swing trades. "
    "Using only the provided articles, summarize sentiment in 2-3 sentences. "
    "If articles are thin or missing, say so and lean neutral. No markdown."
)

_s3 = None


def _s3_client():
    global _s3
    if _s3 is None:
        _s3 = boto3.client("s3")
    return _s3


def load_articles(ticker: str) -> list[dict[str, Any]]:
    if not NEWS_BUCKET:
        return []
    key = f"news/{ticker}.json"
    try:
        obj = _s3_client().get_object(Bucket=NEWS_BUCKET, Key=key)
        data = json.loads(obj["Body"].read().decode("utf-8"))
        if isinstance(data, list):
            return data
        return data.get("articles") or []
    except Exception as exc:  # noqa: BLE001 — missing key or transient S3 errors
        logger.warning("failed to load news for %s: %s", ticker, exc)
        return []


def analyze(ticker: str, query: str) -> dict[str, Any]:
    articles = load_articles(ticker)
    if not articles:
        return {
            "ticker": ticker,
            "summary": (
                "No recent embedded news corpus found for this ticker. "
                "Sentiment treated as neutral pending the next weekly ingestion."
            ),
            "articles_used": [],
            "top_k": 0,
        }

    try:
        q_emb = embed_text(query or ticker)
        selected = top_k_similar(q_emb, articles, k=TOP_K)
    except Exception as exc:  # noqa: BLE001
        logger.exception("embedding/RAG failed: %s", exc)
        selected = articles[:TOP_K]

    compact = [
        {
            "headline": a.get("headline"),
            "summary": a.get("summary"),
            "published_date": a.get("published_date"),
        }
        for a in selected
    ]
    summary = invoke_haiku(
        SYSTEM,
        f"Ticker: {ticker}\nUser query: {query}\nTop articles:\n{json.dumps(compact, default=str)}",
    )
    return {
        "ticker": ticker,
        "summary": summary,
        "articles_used": compact,
        "top_k": len(compact),
    }


def handler(event, context):
    body = event if isinstance(event, dict) and "ticker" in event else json.loads(event.get("body") or "{}")
    return analyze(body["ticker"], body.get("query", ""))
