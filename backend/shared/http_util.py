"""Shared Lambda response helpers."""

from __future__ import annotations

import json
from typing import Any


def json_response(status: int, body: dict[str, Any], *, cors: bool = False) -> dict:
    """Build an API Gateway / Function URL response.

    CORS is handled by the Function URL / HTTP API config — do not set
    Access-Control-Allow-Origin here or browsers see duplicate headers and fail.
    """
    headers = {"Content-Type": "application/json"}
    # Optional explicit CORS only when caller needs it (default off).
    if cors:
        headers.update(
            {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type,x-demo-key",
                "Access-Control-Allow-Methods": "GET,POST,OPTIONS",
            }
        )
    return {
        "statusCode": status,
        "headers": headers,
        "body": json.dumps(body),
    }


def parse_body(event: dict) -> dict:
    body = event.get("body") or "{}"
    if event.get("isBase64Encoded"):
        import base64

        body = base64.b64decode(body).decode("utf-8")
    if isinstance(body, dict):
        return body
    return json.loads(body or "{}")
