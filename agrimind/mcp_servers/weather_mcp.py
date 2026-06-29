"""
weather_mcp.py — AgriMind Weather MCP Server
──────────────────────────────────────────────
A standalone MCP server that exposes weather data as an MCP tool.
ADK's weather_agent connects to this server via MCPToolset.

This demonstrates the MCP (Model Context Protocol) concept from the course:
  ✅ External data exposed as a standardised MCP tool
  ✅ Agent connects via StdioServerParameters (subprocess transport)
  ✅ Clean separation — server runs independently of the agent

Run standalone to test:
  python agrimind/mcp_servers/weather_mcp.py

ADK connects to it automatically when weather_agent is invoked.
"""

import requests
from mcp.server.fastmcp import FastMCP

# ── Create the MCP server ─────────────────────────────────────────────────────
mcp = FastMCP(
    name="agrimind-weather-mcp",
    instructions=(
        "Provides real-time weather forecasts for Indian farming locations "
        "using the Open-Meteo API. Use get_weather_forecast to get current "
        "conditions and multi-day forecasts for any Indian city or district."
    ),
)

# ── Location lookup table ─────────────────────────────────────────────────────
INDIA_LOCATIONS = {
    "hyderabad":  (17.3850, 78.4867), "warangal":   (17.9784, 79.5941),
    "nizamabad":  (18.6725, 78.0941), "karimnagar":  (18.4386, 79.1288),
    "nalgonda":   (17.0575, 79.2690), "adilabad":    (19.6641, 78.5320),
    "khammam":    (17.2473, 80.1514), "nagpur":      (21.1458, 79.0882),
    "pune":       (18.5204, 73.8567), "nashik":      (19.9975, 73.7898),
    "mumbai":     (19.0760, 72.8777), "delhi":       (28.7041, 77.1025),
    "lucknow":    (26.8467, 80.9462), "kanpur":      (26.4499, 80.3319),
    "varanasi":   (25.3176, 82.9739), "patna":       (25.5941, 85.1376),
    "jaipur":     (26.9124, 75.7873), "ahmedabad":   (23.0225, 72.5714),
    "bhopal":     (23.2599, 77.4126), "indore":      (22.7196, 75.8577),
    "bangalore":  (12.9716, 77.5946), "mysore":      (12.2958, 76.6394),
    "chennai":    (13.0827, 80.2707), "coimbatore":  (11.0168, 76.9558),
    "kolkata":    (22.5726, 88.3639), "bhubaneswar": (20.2961, 85.8245),
    "raipur":     (21.2514, 81.6296), "amritsar":    (31.6340, 74.8723),
    "ludhiana":   (30.9010, 75.8573), "chandigarh":  (30.7333, 76.7794),
    "default":    (17.3850, 78.4867),
}


def _resolve_location(location: str) -> tuple[float, float]:
    return INDIA_LOCATIONS.get(location.lower().strip(), INDIA_LOCATIONS["default"])


def _weather_code_to_text(code: int) -> str:
    mapping = {
        0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
        45: "Foggy", 51: "Light drizzle", 53: "Moderate drizzle", 55: "Heavy drizzle",
        61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
        80: "Slight showers", 81: "Moderate showers", 82: "Violent showers",
        95: "Thunderstorm",
    }
    return mapping.get(code, f"Code {code}")


def _farming_notes(current: dict, daily: list) -> list[str]:
    notes = []
    total_rain = sum(d.get("rain_mm", 0) for d in daily)
    max_temp = max((d.get("max_temp_c", 0) for d in daily), default=0)
    if total_rain > 50:
        notes.append("Heavy rainfall expected — avoid sowing; clear field drainage.")
    elif total_rain < 5:
        notes.append("Dry week ahead — irrigate crops in sensitive growth stages.")
    else:
        notes.append("Moderate rainfall — good conditions for most field operations.")
    if max_temp > 40:
        notes.append("Extreme heat alert: above 40°C — shade sensitive seedlings.")
    elif max_temp < 15:
        notes.append("Cool temperatures — ideal for rabi crops like wheat and mustard.")
    if current.get("humidity_pct", 0) > 80:
        notes.append("High humidity — watch for fungal diseases; consider preventive spraying.")
    return notes or ["Weather conditions look stable for farming this week."]


# ── MCP Tool ──────────────────────────────────────────────────────────────────
@mcp.tool()
def get_weather_forecast(location: str, days: int = 7) -> dict:
    """
    Get real-time weather forecast for an Indian farming location.

    Fetches live data from Open-Meteo API (free, no key needed) and returns
    current conditions plus a multi-day forecast with farming-specific notes.

    Args:
        location: City or district name (e.g. "Hyderabad", "Warangal", "Pune").
        days:     Forecast days to return, 1–16. Default is 7.

    Returns:
        Dict with current weather, daily forecast, and farming advice notes.
    """
    days = max(1, min(days, 16))
    lat, lon = _resolve_location(location)

    try:
        resp = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude":      lat,
                "longitude":     lon,
                "current":       "temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m,weather_code",
                "daily":         "temperature_2m_max,temperature_2m_min,precipitation_sum,weather_code",
                "timezone":      "Asia/Kolkata",
                "forecast_days": days,
            },
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()

        cur = data.get("current", {})
        day = data.get("daily", {})

        current = {
            "temperature_c": cur.get("temperature_2m"),
            "humidity_pct":  cur.get("relative_humidity_2m"),
            "rain_mm":       cur.get("precipitation", 0),
            "wind_kph":      cur.get("wind_speed_10m"),
            "condition":     _weather_code_to_text(cur.get("weather_code", 0)),
        }

        dates     = day.get("time", [])
        daily_forecast = [
            {
                "date":       dates[i],
                "max_temp_c": day["temperature_2m_max"][i],
                "min_temp_c": day["temperature_2m_min"][i],
                "rain_mm":    day["precipitation_sum"][i],
                "condition":  _weather_code_to_text(day["weather_code"][i]),
            }
            for i in range(len(dates))
        ]

        return {
            "location":        location.title(),
            "current":         current,
            "daily_forecast":  daily_forecast,
            "farming_notes":   _farming_notes(current, daily_forecast),
            "source":          "Open-Meteo API (real-time) via AgriMind Weather MCP",
        }

    except requests.RequestException as e:
        return {"error": str(e), "message": f"Could not fetch weather for {location}."}


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    mcp.run()
