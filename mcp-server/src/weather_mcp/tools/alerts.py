from weather_mcp.clients import owm


async def get_severe_weather_alerts(lat: float, lon: float) -> list[dict]:
    """
    Get active severe weather alerts for a location.

    Args:
        lat: Latitude of the location.
        lon: Longitude of the location.

    Returns:
        List of active weather alerts. Each alert includes event type, sender, start/end
        timestamps, and a full description. Returns an empty list when no alerts are active.
    """
    data = await owm.one_call(lat, lon, exclude="current,minutely,hourly,daily")
    alerts = data.get("alerts", [])
    return [
        {
            "event": a.get("event"),
            "sender": a.get("sender_name"),
            "start": a.get("start"),
            "end": a.get("end"),
            "description": a.get("description"),
            "tags": a.get("tags", []),
        }
        for a in alerts
    ]
