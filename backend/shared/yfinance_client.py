"""yfinance wrapper with retry/backoff — Yahoo rate-limits under bursty access."""

from __future__ import annotations

import logging
import time
from typing import Any, Callable, TypeVar

import yfinance as yf

logger = logging.getLogger(__name__)

T = TypeVar("T")

MAX_RETRIES = 4
BASE_DELAY_SEC = 1.5


def with_retry(fn: Callable[[], T], *, label: str = "yfinance") -> T:
    last_exc: Exception | None = None
    for attempt in range(MAX_RETRIES):
        try:
            return fn()
        except Exception as exc:  # noqa: BLE001 — surface Yahoo/network flakiness
            last_exc = exc
            delay = BASE_DELAY_SEC * (2**attempt)
            logger.warning(
                "%s failed (attempt %s/%s): %s — sleeping %.1fs",
                label,
                attempt + 1,
                MAX_RETRIES,
                exc,
                delay,
            )
            time.sleep(delay)
    assert last_exc is not None
    raise last_exc


def fetch_history(ticker: str, period: str = "6mo") -> Any:
    def _call():
        t = yf.Ticker(ticker)
        hist = t.history(period=period)
        if hist is None or hist.empty:
            raise ValueError(f"Empty history for {ticker}")
        return hist

    return with_retry(_call, label=f"history:{ticker}")


def fetch_info(ticker: str) -> dict[str, Any]:
    def _call():
        info = yf.Ticker(ticker).info or {}
        if not info:
            raise ValueError(f"Empty info for {ticker}")
        return info

    return with_retry(_call, label=f"info:{ticker}")


def fetch_news(ticker: str) -> list[dict[str, Any]]:
    def _call():
        raw = yf.Ticker(ticker).news or []
        return list(raw)

    return with_retry(_call, label=f"news:{ticker}")
