"""Bedrock helpers — Nova Micro for agents, Claude Sonnet for judge, Titan for embeddings."""

from __future__ import annotations

import json
import logging
import os
from typing import Any

import boto3

logger = logging.getLogger(__name__)

REGION = os.environ.get("AWS_REGION", "us-east-1")

# Claude Haiku is LEGACY / Marketplace-gated on many accounts; Nova Micro is the cheap active stand-in.
HAIKU_MODEL = os.environ.get(
    "BEDROCK_HAIKU_MODEL", "amazon.nova-micro-v1:0"
)
SONNET_MODEL = os.environ.get(
    "BEDROCK_SONNET_MODEL", "amazon.nova-pro-v1:0"
)
EMBED_MODEL = os.environ.get(
    "BEDROCK_EMBED_MODEL", "amazon.titan-embed-text-v2:0"
)

_bedrock = None


def _client():
    global _bedrock
    if _bedrock is None:
        _bedrock = boto3.client("bedrock-runtime", region_name=REGION)
    return _bedrock


def _is_anthropic(model_id: str) -> bool:
    return "anthropic" in model_id


def invoke_text(
    *,
    system: str,
    user: str,
    model_id: str,
    max_tokens: int = 1024,
    temperature: float = 0.2,
) -> str:
    if _is_anthropic(model_id):
        body: dict[str, Any] = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": max_tokens,
            "temperature": temperature,
            "system": system,
            "messages": [{"role": "user", "content": user}],
        }
        response = _client().invoke_model(
            modelId=model_id,
            contentType="application/json",
            accept="application/json",
            body=json.dumps(body),
        )
        payload = json.loads(response["body"].read())
        parts = payload.get("content") or []
        return "".join(
            p.get("text", "") for p in parts if p.get("type") == "text"
        ).strip()

    # Amazon Nova Messages API
    body = {
        "system": [{"text": system}],
        "messages": [
            {"role": "user", "content": [{"text": user}]},
        ],
        "inferenceConfig": {
            "maxTokens": max_tokens,
            "temperature": temperature,
        },
    }
    response = _client().invoke_model(
        modelId=model_id,
        contentType="application/json",
        accept="application/json",
        body=json.dumps(body),
    )
    payload = json.loads(response["body"].read())
    content = (
        ((payload.get("output") or {}).get("message") or {}).get("content") or []
    )
    return "".join(part.get("text", "") for part in content).strip()


def invoke_haiku(system: str, user: str, max_tokens: int = 700) -> str:
    return invoke_text(
        system=system, user=user, model_id=HAIKU_MODEL, max_tokens=max_tokens
    )


def invoke_sonnet(system: str, user: str, max_tokens: int = 1200) -> str:
    return invoke_text(
        system=system, user=user, model_id=SONNET_MODEL, max_tokens=max_tokens
    )


def embed_text(text: str) -> list[float]:
    """Titan Text Embeddings V2 — returns dense vector for cosine RAG."""
    truncated = (text or "")[:8000]
    body: dict[str, Any] = {
        "inputText": truncated,
        "dimensions": 512,
        "normalize": True,
    }
    response = _client().invoke_model(
        modelId=EMBED_MODEL,
        contentType="application/json",
        accept="application/json",
        body=json.dumps(body),
    )
    payload = json.loads(response["body"].read())
    embedding = payload.get("embedding")
    if not embedding:
        raise RuntimeError("Titan returned empty embedding")
    return embedding
