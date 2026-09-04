"""DynamoDB AnalysisCache — technical 24h TTL, fundamental 7d TTL."""

from __future__ import annotations

import json
import logging
import os
import time
from typing import Any

import boto3

logger = logging.getLogger(__name__)

TABLE = os.environ.get("ANALYSIS_CACHE_TABLE", "AnalysisCache")
TECHNICAL_TTL_SEC = 24 * 60 * 60
FUNDAMENTAL_TTL_SEC = 7 * 24 * 60 * 60

_dynamo = None


def _table():
    global _dynamo
    if _dynamo is None:
        _dynamo = boto3.resource("dynamodb").Table(TABLE)
    return _dynamo


def get_cached(ticker: str, analysis_type: str) -> dict[str, Any] | None:
    try:
        resp = _table().get_item(
            Key={"ticker": ticker, "analysisType": analysis_type}
        )
    except Exception as exc:  # noqa: BLE001
        logger.warning("cache get failed: %s", exc)
        return None

    item = resp.get("Item")
    if not item:
        return None

    expires = int(item.get("expiresAt", 0))
    if expires and expires < int(time.time()):
        return None

    payload = item.get("payload")
    if isinstance(payload, str):
        return json.loads(payload)
    return payload  # type: ignore[return-value]


def put_cached(
    ticker: str,
    analysis_type: str,
    payload: dict[str, Any],
    *,
    ttl_seconds: int,
) -> None:
    expires_at = int(time.time()) + ttl_seconds
    try:
        _table().put_item(
            Item={
                "ticker": ticker,
                "analysisType": analysis_type,
                "payload": json.dumps(payload),
                "expiresAt": expires_at,
            }
        )
    except Exception as exc:  # noqa: BLE001
        logger.warning("cache put failed: %s", exc)


def get_stale(ticker: str, analysis_type: str) -> dict[str, Any] | None:
    """Return cached payload even if TTL expired — graceful yfinance fallback."""
    try:
        resp = _table().get_item(
            Key={"ticker": ticker, "analysisType": analysis_type}
        )
    except Exception as exc:  # noqa: BLE001
        logger.warning("stale cache get failed: %s", exc)
        return None
    item = resp.get("Item")
    if not item:
        return None
    payload = item.get("payload")
    if isinstance(payload, str):
        return json.loads(payload)
    return payload  # type: ignore[return-value]
