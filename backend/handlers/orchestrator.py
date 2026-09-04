"""Orchestrator — shared-secret gate, LangGraph multi-agent pipeline, log session."""

from __future__ import annotations

import logging
import os

from shared.analysis_graph import run_analysis
from shared.http_util import json_response, parse_body
from shared.sessions import list_sessions, save_session
from shared.tickers import extract_ticker_from_query, normalize_ticker

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

DEMO_API_KEY = os.environ.get("DEMO_API_KEY", "")


def _headers(event: dict) -> dict:
    return {str(k).lower(): v for k, v in (event.get("headers") or {}).items()}


def _check_secret(event: dict) -> bool:
    if not DEMO_API_KEY:
        logger.error("DEMO_API_KEY not configured")
        return False
    headers = _headers(event)
    return headers.get("x-demo-key", "") == DEMO_API_KEY


def _http_method(event: dict) -> str:
    rc = event.get("requestContext") or {}
    http = rc.get("http") or {}
    return (http.get("method") or event.get("httpMethod") or "POST").upper()


def _path(event: dict) -> str:
    rc = event.get("requestContext") or {}
    http = rc.get("http") or {}
    return event.get("rawPath") or http.get("path") or event.get("path") or "/"


def analyze_handler(event, context):
    if _http_method(event) == "OPTIONS":
        return json_response(200, {"ok": True})

    if not _check_secret(event):
        return json_response(401, {"error": "Unauthorized"})

    try:
        body = parse_body(event)
    except Exception:
        return json_response(400, {"error": "Invalid JSON body"})

    query = (body.get("query") or "").strip()
    if not query:
        return json_response(400, {"error": "query is required"})

    ticker = normalize_ticker(body.get("ticker")) or extract_ticker_from_query(query)
    if not ticker:
        return json_response(
            400,
            {"error": "Ticker must be a Nifty 50 symbol (e.g. TCS, RELIANCE)."},
        )

    try:
        result = run_analysis(ticker=ticker, query=query)
    except Exception as exc:  # noqa: BLE001
        logger.exception("LangGraph pipeline failed: %s", exc)
        return json_response(
            502, {"error": "Analysis pipeline failed", "detail": str(exc)}
        )

    save_session(query=query, ticker=ticker, result=result)
    return json_response(200, result)


def history_handler(event, context):
    if _http_method(event) == "OPTIONS":
        return json_response(200, {"ok": True})

    if not _check_secret(event):
        return json_response(401, {"error": "Unauthorized"})

    sessions = list_sessions(limit=30)
    return json_response(200, {"sessions": sessions})


def router(event, context):
    """Function URL entrypoint — routes /analyze and /history (bypasses API GW 30s cap)."""
    method = _http_method(event)
    path = _path(event).rstrip("/") or "/"

    if method == "OPTIONS":
        return json_response(200, {"ok": True})

    if path.endswith("/history") and method == "GET":
        return history_handler(event, context)

    if path.endswith("/analyze") and method == "POST":
        return analyze_handler(event, context)

    # Function URL root: POST = analyze, GET = history
    if method == "POST":
        return analyze_handler(event, context)
    if method == "GET":
        return history_handler(event, context)

    return json_response(404, {"error": f"No route for {method} {path}"})
