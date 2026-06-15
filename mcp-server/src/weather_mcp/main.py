import os
from dotenv import load_dotenv

load_dotenv()

from fastmcp import FastMCP
from weather_mcp.tools.weather import get_current_weather, get_forecast
from weather_mcp.tools.location import geocode, reverse_geocode
from weather_mcp.tools.alerts import get_severe_weather_alerts
from weather_mcp.tools.history import get_historical_weather

mcp = FastMCP(
    "WeatherMCPServer",
    host="0.0.0.0",
    port=8000,
    stateless_http=True,
)

mcp.tool()(get_current_weather)
mcp.tool()(get_forecast)
mcp.tool()(geocode)
mcp.tool()(reverse_geocode)
mcp.tool()(get_severe_weather_alerts)
mcp.tool()(get_historical_weather)


@mcp.custom_route("/health", methods=["GET"])
async def health(_request):
    from starlette.responses import JSONResponse
    return JSONResponse({"status": "ok", "tools": 6})


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
