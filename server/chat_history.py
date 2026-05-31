import os
import uuid
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any

from botocore.exceptions import ClientError
from fastapi import HTTPException, status

from db import dynamodb_table

CHAT_TABLE_NAME = os.getenv("CHAT_DYNAMODB_TABLE", "conversations")


def _normalize_item(item: dict[str, Any]) -> dict[str, Any]:
    normalized = {}
    for key, value in item.items():
        if isinstance(value, Decimal):
            normalized[key] = int(value) if value % 1 == 0 else float(value)
        else:
            normalized[key] = value
    return normalized


def _chat_table():
    return dynamodb_table(CHAT_TABLE_NAME)


def save_conversation(
    user_email: str,
    user_query: str,
    ai_response: str,
    *,
    verdict: str,
    confidence: int,
    holding_period: str,
) -> dict[str, Any]:
    conversation_id = str(uuid.uuid4())
    created_at = datetime.now(timezone.utc).isoformat()

    item = {
        "user_email": user_email.lower(),
        "conversation_id": conversation_id,
        "user_query": user_query,
        "ai_response": ai_response,
        "verdict": verdict,
        "confidence": confidence,
        "holding_period": holding_period,
        "created_at": created_at,
    }

    try:
        _chat_table().put_item(Item=item)
    except ClientError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Unable to save conversation",
        ) from exc

    return item


def list_conversations(user_email: str, *, limit: int = 100) -> list[dict[str, Any]]:
    try:
        result = _chat_table().query(
            KeyConditionExpression="user_email = :email",
            ExpressionAttributeValues={":email": user_email.lower()},
            ScanIndexForward=True,
            Limit=limit,
        )
    except ClientError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Unable to load conversation history",
        ) from exc

    items = [_normalize_item(item) for item in result.get("Items", [])]
    items.sort(key=lambda item: item.get("created_at", ""))
    return items
