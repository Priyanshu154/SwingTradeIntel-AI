"""ChatSessions DynamoDB — demo polish for sidebar history (userId fixed to 'demo')."""

from __future__ import annotations

import logging
import os
import time
import uuid
from decimal import Decimal
from typing import Any

import boto3

logger = logging.getLogger(__name__)

TABLE = os.environ.get("CHAT_SESSIONS_TABLE", "ChatSessions")
DEMO_USER = "demo"

_dynamo = None


def _table():
    global _dynamo
    if _dynamo is None:
        _dynamo = boto3.resource("dynamodb").Table(TABLE)
    return _dynamo


def _to_dynamo(value: Any) -> Any:
    if isinstance(value, float):
        return Decimal(str(value))
    if isinstance(value, dict):
        return {k: _to_dynamo(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_to_dynamo(v) for v in value]
    return value


def save_session(
    *,
    query: str,
    ticker: str,
    result: dict[str, Any],
    session_id: str | None = None,
) -> str:
    sid = session_id or str(uuid.uuid4())
    ts = int(time.time() * 1000)
    sk = f"{sid}#{ts}"
    item = {
        "userId": DEMO_USER,
        "sessionId#timestamp": sk,
        "sessionId": sid,
        "timestamp": ts,
        "query": query,
        "ticker": ticker,
        "trade_verdict": result.get("trade_verdict"),
        "market_sentiment": result.get("market_sentiment"),
        "confidence_score": result.get("confidence_score"),
        "suggested_holding_period": result.get("suggested_holding_period"),
        "result": _to_dynamo(result),
    }
    try:
        _table().put_item(Item=item)
    except Exception as exc:  # noqa: BLE001
        logger.warning("chat session save failed: %s", exc)
    return sid


def list_sessions(limit: int = 20) -> list[dict[str, Any]]:
    try:
        resp = _table().query(
            KeyConditionExpression="userId = :u",
            ExpressionAttributeValues={":u": DEMO_USER},
            ScanIndexForward=False,
            Limit=limit,
        )
    except Exception as exc:  # noqa: BLE001
        logger.warning("chat session list failed: %s", exc)
        return []

    items = []
    for raw in resp.get("Items", []):
        result = raw.get("result") or {}
        if hasattr(result, "items"):
            # Convert Decimals back for JSON
            result = {
                k: (
                    int(v)
                    if isinstance(v, Decimal) and v % 1 == 0
                    else float(v)
                    if isinstance(v, Decimal)
                    else v
                )
                for k, v in result.items()
            }
        items.append(
            {
                "sessionId": raw.get("sessionId"),
                "timestamp": int(raw.get("timestamp", 0)),
                "query": raw.get("query"),
                "ticker": raw.get("ticker"),
                "trade_verdict": raw.get("trade_verdict"),
                "market_sentiment": raw.get("market_sentiment"),
                "confidence_score": int(raw["confidence_score"])
                if raw.get("confidence_score") is not None
                else None,
                "suggested_holding_period": raw.get("suggested_holding_period"),
                "result": result,
            }
        )
    items.sort(key=lambda row: row["timestamp"], reverse=True)
    return items[:limit]
