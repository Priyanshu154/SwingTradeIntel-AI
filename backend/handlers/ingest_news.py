"""Weekly news ingestion — sequential yfinance pull + Titan embed → S3 JSON."""

from __future__ import annotations

import json
import logging
import os
import time
from datetime import datetime, timezone
from typing import Any

import boto3

from shared.bedrock import embed_text
from shared.tickers import NIFTY_50
from shared.yfinance_client import fetch_news

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

NEWS_BUCKET = os.environ["NEWS_BUCKET"]
PER_TICKER_DELAY_SEC = float(os.environ.get("INGEST_DELAY_SEC", "2.0"))

_s3 = boto3.client("s3")


def _article_text(item: dict[str, Any]) -> tuple[str, str, str]:
    """Normalize yfinance news shapes across versions."""
    content = item.get("content") if isinstance(item.get("content"), dict) else {}
    headline = (
        item.get("title")
        or content.get("title")
        or item.get("headline")
        or ""
    )
    summary = (
        item.get("summary")
        or content.get("summary")
        or content.get("description")
        or headline
    )
    published = (
        item.get("providerPublishTime")
        or content.get("pubDate")
        or item.get("published_date")
        or ""
    )
    if isinstance(published, (int, float)):
        published = datetime.fromtimestamp(published, tz=timezone.utc).isoformat()
    return str(headline), str(summary), str(published)


def ingest_ticker(ticker: str) -> int:
    raw_news = fetch_news(ticker)
    articles: list[dict[str, Any]] = []
    for item in raw_news[:20]:
        headline, summary, published = _article_text(item)
        if not headline and not summary:
            continue
        text = f"{headline}\n{summary}".strip()
        try:
            embedding = embed_text(text)
        except Exception as exc:  # noqa: BLE001
            logger.warning("embed failed for %s article: %s", ticker, exc)
            continue
        articles.append(
            {
                "headline": headline,
                "summary": summary,
                "published_date": published,
                "embedding": embedding,
            }
        )

    key = f"news/{ticker}.json"
    _s3.put_object(
        Bucket=NEWS_BUCKET,
        Key=key,
        Body=json.dumps(articles).encode("utf-8"),
        ContentType="application/json",
    )
    logger.info("wrote %s articles for %s", len(articles), ticker)
    return len(articles)


def handler(event, context):
    tickers = event.get("tickers") if isinstance(event, dict) else None
    universe = tickers or NIFTY_50
    totals = {"tickers": 0, "articles": 0, "errors": []}

    for i, ticker in enumerate(universe):
        try:
            count = ingest_ticker(ticker)
            totals["tickers"] += 1
            totals["articles"] += count
        except Exception as exc:  # noqa: BLE001
            logger.exception("ingest failed for %s", ticker)
            totals["errors"].append({"ticker": ticker, "error": str(exc)})
        if i < len(universe) - 1:
            time.sleep(PER_TICKER_DELAY_SEC)

    return totals
