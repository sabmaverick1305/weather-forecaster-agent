import logging
import os
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=os.environ.get("LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)

from bedrock_agentcore.runtime import BedrockAgentCoreApp
from weather_agent.agent import create_agent

app = BedrockAgentCoreApp()


@app.entrypoint
async def invoke(payload: dict, context) -> str:
    prompt = payload.get("prompt", "")
    session_id = payload.get("session_id", "default")

    if not prompt:
        return "Please provide a weather question."

    logger.info("Received prompt for session=%s prompt=%r", session_id, prompt[:80])

    try:
        agent = create_agent()
        logger.info("Agent created, invoking...")
        result = agent(prompt)
        logger.info("Agent response ready, session=%s", session_id)
        return str(result)
    except Exception as e:
        logger.error("Agent error session=%s: %s", session_id, e, exc_info=True)
        return f"[AGENT_ERROR] {type(e).__name__}: {e}"


if __name__ == "__main__":
    app.run()
