from weather_mcp.clients import owm


async def geocode(city: str, country_code: str | None = None) -> list[dict]:
    """
    Convert a city name to geographic coordinates.

    Args:
        city: City name (e.g. "London", "New York")
        country_code: Optional ISO 3166 country code (e.g. "US", "GB") to narrow results

    Returns:
        List of matching locations with name, lat, lon, country, and state fields.
    """
    results = await owm.geocode(city, country_code)
    return [
        {
            "name": r.get("name"),
            "lat": r.get("lat"),
            "lon": r.get("lon"),
            "country": r.get("country"),
            "state": r.get("state"),
        }
        for r in results
    ]


async def reverse_geocode(lat: float, lon: float) -> list[dict]:
    """
    Convert geographic coordinates to a location name.

    Args:
        lat: Latitude (-90 to 90)
        lon: Longitude (-180 to 180)

    Returns:
        List of location names for the given coordinates.
    """
    results = await owm.reverse_geocode(lat, lon)
    return [
        {
            "name": r.get("name"),
            "lat": r.get("lat"),
            "lon": r.get("lon"),
            "country": r.get("country"),
            "state": r.get("state"),
        }
        for r in results
    ]
