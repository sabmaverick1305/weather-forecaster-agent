from weather_mcp.clients import owm


async def get_historical_weather(
    lat: float,
    lon: float,
    date: str,
    units: str = "metric",
) -> dict:
    """
    Get historical weather summary for a specific date.

    Requires an OpenWeatherMap One Call API 3.0 subscription (includes 1000 free calls/day).
    Supports dates up to 47 years in the past.

    Args:
        lat: Latitude of the location.
        lon: Longitude of the location.
        date: Date in YYYY-MM-DD format (e.g. "2024-01-15").
        units: "metric" (°C), "imperial" (°F), or "standard" (K).

    Returns:
        Daily summary including temperature range, humidity, wind speed, precipitation,
        and cloud cover for the requested date.
    """
    try:
        data = await owm.history_day_summary(lat, lon, date, units)
    except Exception as e:
        if "401" in str(e) or "403" in str(e):
            return {
                "error": "Historical weather data requires an active OpenWeatherMap One Call 3.0 "
                "subscription. Please upgrade your plan at openweathermap.org/api."
            }
        raise

    unit_label = "°C" if units == "metric" else ("°F" if units == "imperial" else "K")
    speed_label = "m/s" if units == "metric" else "mph"
    temp = data.get("temperature", {})
    wind = data.get("wind", {})
    precip = data.get("precipitation", {})

    return {
        "lat": lat,
        "lon": lon,
        "date": date,
        "units": units,
        "temp_min": f"{temp.get('min')} {unit_label}",
        "temp_max": f"{temp.get('max')} {unit_label}",
        "temp_afternoon": f"{temp.get('afternoon')} {unit_label}",
        "temp_morning": f"{temp.get('morning')} {unit_label}",
        "temp_evening": f"{temp.get('evening')} {unit_label}",
        "temp_night": f"{temp.get('night')} {unit_label}",
        "humidity_afternoon": f"{data.get('humidity', {}).get('afternoon')}%",
        "wind_max_speed": f"{wind.get('max', {}).get('speed')} {speed_label}",
        "wind_max_direction_deg": wind.get("max", {}).get("direction"),
        "precipitation_total_mm": precip.get("total"),
        "cloud_cover_afternoon": f"{data.get('cloud_cover', {}).get('afternoon')}%",
    }
