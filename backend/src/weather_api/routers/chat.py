import logging
import uuid
from fastapi import APIRouter
from sse_starlette.sse import EventSourceResponse
from weather_api.models.schemas import ChatRequest
from weather_api.services.agentcore import invoke_agent_streaming

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/chat/stream")
async def chat_stream(req: ChatRequest):
    session_id = req.session_id or str(uuid.uuid4())
    logger.info("chat/stream session=%s message=%r", session_id, req.message[:80])

    async def event_generator():
        try:
            async for chunk in invoke_agent_streaming(req.message, session_id):
                yield {"data": chunk}
            yield {"data": "[DONE]"}
        except Exception as e:
            logger.error("AgentCore error session=%s: %s", session_id, e, exc_info=True)
            yield {"data": f"[ERROR] {e}"}

    return EventSourceResponse(event_generator())


@router.post("/chat")
async def chat(req: ChatRequest):
    """Non-streaming endpoint — collects full response before returning."""
    session_id = req.session_id or str(uuid.uuid4())
    parts: list[str] = []
    async for chunk in invoke_agent_streaming(req.message, session_id):
        parts.append(chunk)
    return {"text": "".join(parts), "session_id": session_id}
