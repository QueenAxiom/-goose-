"""10-day forecasts from Open-Meteo (free, no key) for the cities Alan follows."""
import json
import time
import urllib.parse
import urllib.request

CITIES = {
    "Calgary": (51.0447, -114.0719),
    "Shenzhen": (22.5431, 114.0579),
}
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
DAILY_FIELDS = "weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max"
FORECAST_DAYS = 10
CACHE_SECONDS = 1800
FETCH_TIMEOUT_SECONDS = 15
# WMO weather codes grouped to a plain-English label.
WMO_LABELS = {
    0: "Clear", 1: "Mostly clear", 2: "Partly cloudy", 3: "Overcast", 45: "Fog", 48: "Fog",
    51: "Drizzle", 53: "Drizzle", 55: "Drizzle", 56: "Freezing drizzle", 57: "Freezing drizzle",
    61: "Rain", 63: "Rain", 65: "Heavy rain", 66: "Freezing rain", 67: "Freezing rain",
    71: "Snow", 73: "Snow", 75: "Heavy snow", 77: "Snow grains",
    80: "Showers", 81: "Showers", 82: "Heavy showers", 85: "Snow showers", 86: "Snow showers",
    95: "Thunderstorm", 96: "Thunderstorm, hail", 99: "Thunderstorm, hail",
}

_cache = {}


def parse_forecast(payload: dict) -> list:
    """Open-Meteo daily arrays -> [{date, summary, high, low, rain_chance}] for each day."""
    daily = payload["daily"]
    days = []
    for i, date in enumerate(daily["time"]):
        days.append({
            "date": date,
            "summary": WMO_LABELS.get(daily["weather_code"][i], "Unknown"),
            "high": daily["temperature_2m_max"][i],
            "low": daily["temperature_2m_min"][i],
            "rain_chance": daily["precipitation_probability_max"][i],
        })
    return days[:FORECAST_DAYS]


def fetch_city(name: str, now: float = None) -> list:
    lat, lon = CITIES[name]
    now = time.time() if now is None else now
    cached = _cache.get(name)
    if cached and now - cached["at"] < CACHE_SECONDS:
        return cached["days"]
    query = urllib.parse.urlencode({"latitude": lat, "longitude": lon, "daily": DAILY_FIELDS,
                                    "timezone": "auto", "forecast_days": FORECAST_DAYS})
    req = urllib.request.Request(f"{FORECAST_URL}?{query}", headers={"User-Agent": "AxiomMissionControl/1.0"})
    with urllib.request.urlopen(req, timeout=FETCH_TIMEOUT_SECONDS) as resp:
        days = parse_forecast(json.loads(resp.read().decode("utf-8")))
    _cache[name] = {"at": now, "days": days}
    return days


def fetch_all() -> dict:
    """One failing city must not hide the others: errors are reported per city."""
    out = {}
    for name in CITIES:
        try:
            out[name] = {"days": fetch_city(name)}
        except (OSError, ValueError, KeyError):
            out[name] = {"days": [], "error": "forecast unavailable"}
    return out
