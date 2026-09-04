"""Orchestrator — shared-secret gate, invoke 3 agents + judge, log session."""

from __future__ import annotations

import json
import logging
import os
from concurrent.futures import ThreadPoolExecutor

import boto3

from shared.http_util import json_response, parse_body
from shared.sessions import list_sessions, save_session
from shared.tickers import extract_ticker_from_query, normalize_ticker

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

DEMO_API_KEY = os.environ.get("DEMO_API_KEY", "")

_lambda = boto3.client("lambda")


def _agent_fn(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(f"Missing env var {name}")
    return value


def _headers(event: dict) -> dict:
    return {str(k).lower(): v for k, v in (event.get("headers") or {}).items()}


def _check_secret(event: dict) -> bool:
    if not DEMO_API_KEY:
        logger.error("DEMO_API_KEY not configured")
        return False
    headers = _headers(event)
    return headers.get("x-demo-key", "") == DEMO_API_KEY


def _invoke(function_name: str, payload: dict) -> dict:
    resp = _lambda.invoke(
        FunctionName=function_name,
        InvocationType="RequestResponse",
        Payload=json.dumps(payload).encode("utf-8"),
    )
    raw = resp["Payload"].read()
    if resp.get("FunctionError"):
        logger.error("invoke error from %s: %s", function_name, raw)
        raise RuntimeError(f"Agent {function_name} failed")
    return json.loads(raw)


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

    agent_payload = {"ticker": ticker, "query": query}

    try:
        # Run specialists in parallel to stay under gateway/client timeouts
        news_fn = _agent_fn("AGENT_NEWS_FUNCTION")
        tech_fn = _agent_fn("AGENT_TECHNICAL_FUNCTION")
        fund_fn = _agent_fn("AGENT_FUNDAMENTAL_FUNCTION")
        judge_fn = _agent_fn("AGENT_JUDGE_FUNCTION")

        with ThreadPoolExecutor(max_workers=3) as pool:
            news_f = pool.submit(_invoke, news_fn, agent_payload)
            tech_f = pool.submit(_invoke, tech_fn, agent_payload)
            fund_f = pool.submit(_invoke, fund_fn, agent_payload)
            news = news_f.result()
            technical = tech_f.result()
            fundamental = fund_f.result()

        result = _invoke(
            judge_fn,
            {
                **agent_payload,
                "news": news,
                "technical": technical,
                "fundamental": fundamental,
            },
        )
    except Exception as exc:  # noqa: BLE001
        logger.exception("pipeline failed: %s", exc)
        return json_response(
            502, {"error": "Analysis pipeline failed", "detail": str(exc)}
        )

    result["ticker"] = ticker
    result["query"] = query
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
