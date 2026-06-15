import os
import logging
from strands import Agent
from strands.models import BedrockModel
from strands.tools.mcp import MCPClient
from mcp.client.streamable_http import streamablehttp_client
from weather_agent.prompts import SYSTEM_PROMPT

logger = logging.getLogger(__name__)

MCP_SERVER_URL = os.environ.get("MCP_SERVER_URL", "http://localhost:8000/mcp")
BEDROCK_MODEL_ID = os.environ.get("BEDROCK_MODEL_ID", "us.anthropic.claude-sonnet-4-6")
AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")


def create_agent() -> Agent:
    # Pass MCPClient as a ToolProvider so Agent manages the connection lifecycle.
    # Do NOT extract tools into a list — the connection would be closed before tool calls.
    mcp_client = MCPClient(lambda: streamablehttp_client(MCP_SERVER_URL))
    model = BedrockModel(
        model_id=BEDROCK_MODEL_ID,
        region_name=AWS_REGION,
    )
    return Agent(
        model=model,
        tools=[mcp_client],
        system_prompt=SYSTEM_PROMPT,
    )
