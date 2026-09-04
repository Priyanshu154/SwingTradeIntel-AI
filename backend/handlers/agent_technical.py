"""Agent 2 — Technical analysis (RSI, MACD, EMA) via pandas layer + yfinance."""

from __future__ import annotations

import json
import logging
from typing import Any

import pandas as pd

from shared.bedrock import invoke_haiku
from shared.cache import (
    TECHNICAL_TTL_SEC,
    get_cached,
    get_stale,
    put_cached,
)
from shared.yfinance_client import fetch_history

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

SYSTEM = (
    "You are a swing-trading technical analyst for Nifty 50 stocks. "
    "Given indicator values, write 2-3 concise sentences on momentum and trend. "
    "Do not invent numbers not provided. No markdown."
)


def _rsi(series: pd.Series, period: int = 14) -> float:
    delta = series.diff()
    gain = delta.clip(lower=0).rolling(period).mean()
    loss = (-delta.clip(upper=0)).rolling(period).mean()
    rs = gain / loss.replace(0, pd.NA)
    rsi = 100 - (100 / (1 + rs))
    val = rsi.iloc[-1]
    return float(val) if pd.notna(val) else 50.0


def _ema(series: pd.Series, span: int) -> float:
    return float(series.ewm(span=span, adjust=False).mean().iloc[-1])


def _macd(series: pd.Series) -> dict[str, float]:
    ema12 = series.ewm(span=12, adjust=False).mean()
    ema26 = series.ewm(span=26, adjust=False).mean()
    macd_line = ema12 - ema26
    signal = macd_line.ewm(span=9, adjust=False).mean()
    hist = macd_line - signal
    return {
        "macd": float(macd_line.iloc[-1]),
        "signal": float(signal.iloc[-1]),
        "histogram": float(hist.iloc[-1]),
    }


def compute_indicators(hist: pd.DataFrame) -> dict[str, Any]:
    close = hist["Close"]
    macd = _macd(close)
    return {
        "last_close": float(close.iloc[-1]),
        "rsi_14": round(_rsi(close, 14), 2),
        "ema_20": round(_ema(close, 20), 2),
        "ema_50": round(_ema(close, 50), 2),
        "macd": round(macd["macd"], 4),
        "macd_signal": round(macd["signal"], 4),
        "macd_histogram": round(macd["histogram"], 4),
    }


def analyze(ticker: str, query: str) -> dict[str, Any]:
    cached = get_cached(ticker, "technical")
    if cached:
        return cached

    try:
        hist = fetch_history(ticker, period="6mo")
        indicators = compute_indicators(hist)
        summary = invoke_haiku(
            SYSTEM,
            f"Ticker: {ticker}\nUser query: {query}\nIndicators JSON:\n{json.dumps(indicators)}",
        )
        result = {"ticker": ticker, "indicators": indicators, "summary": summary}
        put_cached(ticker, "technical", result, ttl_seconds=TECHNICAL_TTL_SEC)
        return result
    except Exception as exc:  # noqa: BLE001
        logger.exception("technical analysis failed for %s: %s", ticker, exc)
        stale = get_stale(ticker, "technical")
        if stale:
            stale = {**stale, "stale": True}
            return stale
        return {
            "ticker": ticker,
            "indicators": {},
            "summary": "Technical data unavailable due to market data provider limits.",
            "error": str(exc),
        }


def handler(event, context):
    body = event if isinstance(event, dict) and "ticker" in event else json.loads(event.get("body") or "{}")
    ticker = body["ticker"]
    query = body.get("query", "")
    return analyze(ticker, query)
