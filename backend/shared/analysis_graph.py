"""LangGraph multi-agent pipeline: parallel specialists → judge synthesis."""

from __future__ import annotations

import json
import logging
import os
from typing import Any, TypedDict

import boto3
from langgraph.graph import END, START, StateGraph

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

_lambda = boto3.client("lambda")
_compiled = None


class AnalysisState(TypedDict, total=False):
    ticker: str
    query: str
    news: dict[str, Any]
    technical: dict[str, Any]
    fundamental: dict[str, Any]
    result: dict[str, Any]


def _agent_fn(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(f"Missing env var {name}")
    return value


def _invoke(function_name: str, payload: dict[str, Any]) -> dict[str, Any]:
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


def _base_payload(state: AnalysisState) -> dict[str, str]:
    return {"ticker": state["ticker"], "query": state.get("query") or ""}


def news_agent(state: AnalysisState) -> dict[str, Any]:
    return {"news": _invoke(_agent_fn("AGENT_NEWS_FUNCTION"), _base_payload(state))}


def technical_agent(state: AnalysisState) -> dict[str, Any]:
    return {
        "technical": _invoke(
            _agent_fn("AGENT_TECHNICAL_FUNCTION"), _base_payload(state)
        )
    }


def fundamental_agent(state: AnalysisState) -> dict[str, Any]:
    return {
        "fundamental": _invoke(
            _agent_fn("AGENT_FUNDAMENTAL_FUNCTION"), _base_payload(state)
        )
    }


def judge_agent(state: AnalysisState) -> dict[str, Any]:
    payload = {
        **_base_payload(state),
        "news": state.get("news") or {},
        "technical": state.get("technical") or {},
        "fundamental": state.get("fundamental") or {},
    }
    return {"result": _invoke(_agent_fn("AGENT_JUDGE_FUNCTION"), payload)}


def build_analysis_graph():
    """Compile News ∥ Technical ∥ Fundamental → Judge."""
    graph = StateGraph(AnalysisState)
    graph.add_node("news_agent", news_agent)
    graph.add_node("technical_agent", technical_agent)
    graph.add_node("fundamental_agent", fundamental_agent)
    graph.add_node("judge_agent", judge_agent)

    # Fan-out: START triggers all three specialists in parallel
    graph.add_edge(START, "news_agent")
    graph.add_edge(START, "technical_agent")
    graph.add_edge(START, "fundamental_agent")
    # Fan-in: judge waits until every specialist finishes
    graph.add_edge(
        ["news_agent", "technical_agent", "fundamental_agent"],
        "judge_agent",
    )
    graph.add_edge("judge_agent", END)

    return graph.compile()


def get_graph():
    global _compiled
    if _compiled is None:
        _compiled = build_analysis_graph()
    return _compiled


def run_analysis(*, ticker: str, query: str) -> dict[str, Any]:
    """Execute the multi-agent graph; returns the judge verdict plus ticker/query."""
    final_state = get_graph().invoke({"ticker": ticker, "query": query})
    result = dict(final_state.get("result") or {})
    result["ticker"] = ticker
    result["query"] = query
    return result
