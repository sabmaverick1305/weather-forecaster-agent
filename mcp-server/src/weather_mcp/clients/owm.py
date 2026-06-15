import os
import time
import asyncio
from typing import Any
import httpx
from cachetools import TTLCache

_BASE = "https://api.openweathermap.org"
_API_KEY = os.environ.get("OWM_API_KEY", "")

# Cache: weather data for 10 min, geocode for 24h
_weather_cache: TTLCache = TTLCache(maxsize=256, ttl=600)
_geo_cache: TTLCache = TTLCache(maxsize=512, ttl=86400)

# Rate-limit guard: max 900 calls per day
_daily_counter = {"count": 0, "reset_at": time.time() + 86400}
_DAILY_LIMIT = 900

_client: httpx.AsyncClient | None = None


def _get_client() -> httpx.AsyncClient:
    global _client
    if _client is None or _client.is_closed:
        _client = httpx.AsyncClient(base_url=_BASE, timeout=10.0)
    return _client


def _check_rate_limit() -> None:
    now = time.time()
    if now >= _daily_counter["reset_at"]:
        _daily_counter["count"] = 0
        _daily_counter["reset_at"] = now + 86400
    if _daily_counter["count"] >= _DAILY_LIMIT:
        raise RuntimeError(
            f"OpenWeatherMap daily call limit reached ({_DAILY_LIMIT} calls). "
            "Resets at midnight UTC."
        )
    _daily_counter["count"] += 1


async def get(path: str, params: dict[str, Any], cache: TTLCache | None = None) -> dict:
    key = (path, tuple(sorted(params.items())))
    if cache is not None and key in cache:
        return cache[key]

    _check_rate_limit()
    params = {**params, "appid": _API_KEY}
    response = await _get_client().get(path, params=params)
    response.raise_for_status()
    data = response.json()

    if cache is not None:
        cache[key] = data
    return data


async def geocode(city: str, country_code: str | None = None, limit: int = 5) -> list[dict]:
    q = f"{city},{country_code}" if country_code else city
    params: dict[str, Any] = {"q": q, "limit": limit}
    key = ("geo", tuple(sorted(params.items())))
    if key in _geo_cache:
        return _geo_cache[key]
    _check_rate_limit()
    params["appid"] = _API_KEY
    response = await _get_client().get("/geo/1.0/direct", params=params)
    response.raise_for_status()
    data = response.json()
    _geo_cache[key] = data
    return data


async def reverse_geocode(lat: float, lon: float, limit: int = 1) -> list[dict]:
    params: dict[str, Any] = {"lat": lat, "lon": lon, "limit": limit}
    key = ("revgeo", tuple(sorted(params.items())))
    if key in _geo_cache:
        return _geo_cache[key]
    _check_rate_limit()
    params["appid"] = _API_KEY
    response = await _get_client().get("/geo/1.0/reverse", params=params)
    response.raise_for_status()
    data = response.json()
    _geo_cache[key] = data
    return data


async def one_call(lat: float, lon: float, exclude: str = "", units: str = "metric") -> dict:
    params: dict[str, Any] = {"lat": lat, "lon": lon, "units": units}
    if exclude:
        params["exclude"] = exclude
    return await get("/data/3.0/onecall", params, cache=_weather_cache)


async def history_day_summary(lat: float, lon: float, date: str, units: str = "metric") -> dict:
    """date must be YYYY-MM-DD."""
    params: dict[str, Any] = {"lat": lat, "lon": lon, "date": date, "units": units}
    return await get("/data/3.0/onecall/day_summary", params, cache=_weather_cache)
