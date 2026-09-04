"""Judge Agent — Claude Sonnet synthesizes the three specialist outputs into strict JSON."""

from __future__ import annotations

import json
import logging
import re
from typing import Any

from shared.bedrock import invoke_sonnet

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

SYSTEM = """You are the final judge for a Nifty 50 swing-trade research desk.
Reconcile news, technical, and fundamental agent outputs into ONE JSON object.
Return ONLY valid JSON (no markdown fences, no commentary) with exactly these keys:
{
  "trade_verdict": "BUY" | "SELL" | "HOLD",
  "market_sentiment": "Bullish" | "Bearish" | "Neutral",
  "confidence_score": <integer 0-100>,
  "suggested_holding_period": <short string>,
  "risk_level": "Low" | "Medium" | "High",
  "technical_analysis": <string>,
  "news_analysis": <string>,
  "fundamental_analysis": <string>,
  "final_thesis": <string>
}
Be conservative: if signals conflict, prefer HOLD and Neutral with moderate confidence.
"""


def _extract_json(text: str) -> dict[str, Any]:
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{[\s\S]*\}", text)
        if not match:
            raise
        return json.loads(match.group(0))


def judge(
    *,
    ticker: str,
    query: str,
    news: dict[str, Any],
    technical: dict[str, Any],
    fundamental: dict[str, Any],
) -> dict[str, Any]:
    user = json.dumps(
        {
            "ticker": ticker,
            "query": query,
            "news_agent": news,
            "technical_agent": technical,
            "fundamental_agent": fundamental,
        },
        default=str,
    )
    raw = invoke_sonnet(SYSTEM, user, max_tokens=1200)
    try:
        result = _extract_json(raw)
    except Exception as exc:  # noqa: BLE001
        logger.exception("judge JSON parse failed: %s | raw=%s", exc, raw[:500])
        result = {
            "trade_verdict": "HOLD",
            "market_sentiment": "Neutral",
            "confidence_score": 50,
            "suggested_holding_period": "Wait for confirmation",
            "risk_level": "Medium",
            "technical_analysis": technical.get("summary", ""),
            "news_analysis": news.get("summary", ""),
            "fundamental_analysis": fundamental.get("summary", ""),
            "final_thesis": "Signals could not be fully reconciled; defaulting to a neutral hold stance.",
        }

    # Clamp / normalize
    verdict = str(result.get("trade_verdict", "HOLD")).upper()
    if verdict not in {"BUY", "SELL", "HOLD"}:
        verdict = "HOLD"
    sentiment = str(result.get("market_sentiment", "Neutral")).title()
    if sentiment not in {"Bullish", "Bearish", "Neutral"}:
        sentiment = "Neutral"
    try:
        confidence = int(result.get("confidence_score", 50))
    except (TypeError, ValueError):
        confidence = 50
    confidence = max(0, min(100, confidence))

    return {
        "trade_verdict": verdict,
        "market_sentiment": sentiment,
        "confidence_score": confidence,
        "suggested_holding_period": str(
            result.get("suggested_holding_period") or "Wait for confirmation"
        ),
        "risk_level": str(result.get("risk_level") or "Medium"),
        "technical_analysis": str(
            result.get("technical_analysis") or technical.get("summary") or ""
        ),
        "news_analysis": str(result.get("news_analysis") or news.get("summary") or ""),
        "fundamental_analysis": str(
            result.get("fundamental_analysis") or fundamental.get("summary") or ""
        ),
        "final_thesis": str(result.get("final_thesis") or ""),
    }


def handler(event, context):
    body = event if isinstance(event, dict) and "ticker" in event else json.loads(event.get("body") or "{}")
    return judge(
        ticker=body["ticker"],
        query=body.get("query", ""),
        news=body.get("news") or {},
        technical=body.get("technical") or {},
        fundamental=body.get("fundamental") or {},
    )
