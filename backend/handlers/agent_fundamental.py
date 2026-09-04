"""Agent 3 — Fundamental analysis from yfinance .info with longer cache."""

from __future__ import annotations

import json
import logging
from typing import Any

from shared.bedrock import invoke_haiku
from shared.cache import (
    FUNDAMENTAL_TTL_SEC,
    get_cached,
    get_stale,
    put_cached,
)
from shared.yfinance_client import fetch_info

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

SYSTEM = (
    "You are a fundamental analyst for Nifty 50 swing trades. "
    "Given fundamentals, write 2-3 concise sentences on valuation and balance-sheet quality. "
    "Do not invent numbers. No markdown."
)

KEYS = (
    "trailingPE",
    "forwardPE",
    "trailingEps",
    "returnOnEquity",
    "debtToEquity",
    "marketCap",
    "sector",
    "industry",
    "profitMargins",
    "revenueGrowth",
)


def _extract(info: dict[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for key in KEYS:
        val = info.get(key)
        if val is not None:
            out[key] = val
    out["shortName"] = info.get("shortName") or info.get("longName")
    return out


def analyze(ticker: str, query: str) -> dict[str, Any]:
    cached = get_cached(ticker, "fundamental")
    if cached:
        return cached

    try:
        info = fetch_info(ticker)
        fundamentals = _extract(info)
        summary = invoke_haiku(
            SYSTEM,
            f"Ticker: {ticker}\nUser query: {query}\nFundamentals JSON:\n{json.dumps(fundamentals, default=str)}",
        )
        result = {
            "ticker": ticker,
            "fundamentals": fundamentals,
            "summary": summary,
        }
        put_cached(ticker, "fundamental", result, ttl_seconds=FUNDAMENTAL_TTL_SEC)
        return result
    except Exception as exc:  # noqa: BLE001
        logger.exception("fundamental analysis failed for %s: %s", ticker, exc)
        stale = get_stale(ticker, "fundamental")
        if stale:
            return {**stale, "stale": True}
        return {
            "ticker": ticker,
            "fundamentals": {},
            "summary": "Fundamental data unavailable due to market data provider limits.",
            "error": str(exc),
        }


def handler(event, context):
    body = event if isinstance(event, dict) and "ticker" in event else json.loads(event.get("body") or "{}")
    return analyze(body["ticker"], body.get("query", ""))
