from weather_mcp.clients import owm


async def _resolve_coords(
    city: str | None, lat: float | None, lon: float | None
) -> tuple[float, float, str]:
    if lat is not None and lon is not None:
        return lat, lon, f"{lat},{lon}"
    if city:
        results = await owm.geocode(city)
        if not results:
            raise ValueError(f"Location not found: {city!r}")
        r = results[0]
        return r["lat"], r["lon"], r.get("name", city)
    raise ValueError("Provide either 'city' or both 'lat' and 'lon'.")


async def get_current_weather(
    city: str | None = None,
    lat: float | None = None,
    lon: float | None = None,
    units: str = "metric",
) -> dict:
    """
    Get current weather conditions for a location.

    Args:
        city: City name (e.g. "Tokyo"). Use this OR lat/lon.
        lat: Latitude. Use with lon instead of city.
        lon: Longitude. Use with lat instead of city.
        units: Unit system — "metric" (°C, m/s), "imperial" (°F, mph), or "standard" (K).

    Returns:
        Current temperature, feels-like, humidity, wind speed/direction, description, UV index, visibility.
    """
    resolved_lat, resolved_lon, location_name = await _resolve_coords(city, lat, lon)
    data = await owm.one_call(
        resolved_lat, resolved_lon, exclude="minutely,hourly,daily,alerts", units=units
    )
    current = data.get("current", {})
    unit_label = "°C" if units == "metric" else ("°F" if units == "imperial" else "K")
    speed_label = "m/s" if units == "metric" else "mph"
    return {
        "location": location_name,
        "lat": resolved_lat,
        "lon": resolved_lon,
        "timestamp": current.get("dt"),
        "temperature": f"{current.get('temp')} {unit_label}",
        "feels_like": f"{current.get('feels_like')} {unit_label}",
        "humidity": f"{current.get('humidity')}%",
        "wind_speed": f"{current.get('wind_speed')} {speed_label}",
        "wind_direction_deg": current.get("wind_deg"),
        "uv_index": current.get("uvi"),
        "visibility_m": current.get("visibility"),
        "description": current.get("weather", [{}])[0].get("description"),
        "icon": current.get("weather", [{}])[0].get("icon"),
        "units": units,
    }


async def get_forecast(
    city: str | None = None,
    lat: float | None = None,
    lon: float | None = None,
    days: int = 7,
    units: str = "metric",
) -> dict:
    """
    Get weather forecast for a location (up to 8 days daily + 48h hourly).

    Args:
        city: City name. Use this OR lat/lon.
        lat: Latitude.
        lon: Longitude.
        days: Number of daily forecast days to return (1–8). Default 7.
        units: "metric", "imperial", or "standard".

    Returns:
        Hourly forecast (next 48h) and daily forecast summaries.
    """
    resolved_lat, resolved_lon, location_name = await _resolve_coords(city, lat, lon)
    data = await owm.one_call(
        resolved_lat, resolved_lon, exclude="current,minutely,alerts", units=units
    )
    unit_label = "°C" if units == "metric" else ("°F" if units == "imperial" else "K")
    speed_label = "m/s" if units == "metric" else "mph"

    hourly = [
        {
            "timestamp": h.get("dt"),
            "temperature": f"{h.get('temp')} {unit_label}",
            "humidity": f"{h.get('humidity')}%",
            "wind_speed": f"{h.get('wind_speed')} {speed_label}",
            "pop": f"{round(h.get('pop', 0) * 100)}%",
            "description": h.get("weather", [{}])[0].get("description"),
        }
        for h in data.get("hourly", [])[:48]
    ]

    daily_raw = data.get("daily", [])[:max(1, min(days, 8))]
    daily = [
        {
            "timestamp": d.get("dt"),
            "temp_min": f"{d.get('temp', {}).get('min')} {unit_label}",
            "temp_max": f"{d.get('temp', {}).get('max')} {unit_label}",
            "humidity": f"{d.get('humidity')}%",
            "wind_speed": f"{d.get('wind_speed')} {speed_label}",
            "pop": f"{round(d.get('pop', 0) * 100)}%",
            "description": d.get("weather", [{}])[0].get("description"),
            "uv_index": d.get("uvi"),
        }
        for d in daily_raw
    ]

    return {
        "location": location_name,
        "lat": resolved_lat,
        "lon": resolved_lon,
        "units": units,
        "hourly_48h": hourly,
        "daily": daily,
    }
