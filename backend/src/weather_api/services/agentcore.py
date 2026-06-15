import json
import os
import re
import uuid
import logging
from typing import AsyncIterator

import boto3
import httpx

_THINKING_RE = re.compile(r"<thinking>.*?</thinking>", re.DOTALL)

logger = logging.getLogger(__name__)

AGENT_RUNTIME_ARN = os.environ.get("AGENT_RUNTIME_ARN", "")
AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")
LOCAL_AGENT_URL = os.environ.get("LOCAL_AGENT_URL", "")

_bedrock_client = None


def _get_bedrock_client():
    global _bedrock_client
    if _bedrock_client is None:
        _bedrock_client = boto3.client("bedrock-agentcore", region_name=AWS_REGION)
    return _bedrock_client


def _normalize_session_id(session_id: str | None) -> str:
    raw = session_id or str(uuid.uuid4())
    # AgentCore requires runtimeSessionId >= 33 chars; derive a stable UUID from short IDs.
    if len(raw) < 33:
        return str(uuid.uuid5(uuid.NAMESPACE_DNS, raw))
    return raw


async def invoke_agent_streaming(message: str, session_id: str | None) -> AsyncIterator[str]:
    session_id = _normalize_session_id(session_id)
    payload = json.dumps({"prompt": message, "session_id": session_id})

    if LOCAL_AGENT_URL:
        async for chunk in _invoke_local(payload, session_id):
            yield chunk
        return

    try:
        async for chunk in _invoke_agentcore(payload, session_id):
            yield chunk
    except Exception as first_err:
        # Warm container may have stale config — retry once with a fresh session ID.
        logger.warning(
            "AgentCore error on session=%s (%s), retrying with fresh session",
            session_id, type(first_err).__name__,
        )
        fresh_session = str(uuid.uuid4())
        fresh_payload = json.dumps({"prompt": message, "session_id": fresh_session})
        async for chunk in _invoke_agentcore(fresh_payload, fresh_session):
            yield chunk


async def _invoke_local(payload: str, session_id: str) -> AsyncIterator[str]:
    """Call the agent container directly (local dev mode)."""
    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(
            LOCAL_AGENT_URL,
            content=payload.encode(),
            headers={"Content-Type": "application/json"},
        )
        response.raise_for_status()
        data = response.json()
        text = data if isinstance(data, str) else data.get("response", str(data))
        yield _THINKING_RE.sub("", text).strip()


async def _invoke_agentcore(payload: str, session_id: str) -> AsyncIterator[str]:
    client = _get_bedrock_client()
    logger.info("Invoking AgentCore arn=%s session=%s", AGENT_RUNTIME_ARN[:60], session_id)
    response = client.invoke_agent_runtime(
        agentRuntimeArn=AGENT_RUNTIME_ARN,
        runtimeSessionId=session_id,
        payload=payload.encode(),
        contentType="application/json",
        accept="application/json",
    )

    streaming_body = response.get("response")
    if streaming_body is None:
        logger.error("No streaming body in AgentCore response")
        return

    raw = streaming_body.read().decode("utf-8")
    if not raw:
        return

    try:
        data = json.loads(raw)
        text = data if isinstance(data, str) else data.get("response", str(data))
    except json.JSONDecodeError:
        text = raw

    text = _THINKING_RE.sub("", text).strip()
    logger.info("AgentCore response length=%d session=%s", len(text), session_id)

    # Agent container returned an error string rather than crashing with 500
    if text.startswith("[AGENT_ERROR]"):
        logger.error("Agent returned error session=%s: %s", session_id, text)
        raise RuntimeError(text[len("[AGENT_ERROR]"):].strip())

    yield text
