"""
weather_tools.py
─────────────────
Fetches real-time weather and 7-day forecast using the Open-Meteo API.
Open-Meteo is completely free and requires no API key — perfect for demos.
API docs: https://open-meteo.com/en/docs
"""

import requests

# ── Geocoding: city name → (lat, lon) ─────────────────────────────────────────
# A small lookup table covering major Indian farming regions.
# In Phase 4 we'll extend this with a real geocoding API call.
INDIA_LOCATIONS = {
    "hyderabad":    (17.3850,  78.4867),
    "warangal":     (17.9784,  79.5941),
    "nizamabad":    (18.6725,  78.0941),
    "karimnagar":   (18.4386,  79.1288),
    "nalgonda":     (17.0575,  79.2690),
    "adilabad":     (19.6641,  78.5320),
    "khammam":      (17.2473,  80.1514),
    "nagpur":       (21.1458,  79.0882),
    "pune":         (18.5204,  73.8567),
    "nashik":       (19.9975,  73.7898),
    "aurangabad":   (19.8762,  75.3433),
    "mumbai":       (19.0760,  72.8777),
    "delhi":        (28.7041,  77.1025),
    "lucknow":      (26.8467,  80.9462),
    "kanpur":       (26.4499,  80.3319),
    "varanasi":     (25.3176,  82.9739),
    "patna":        (25.5941,  85.1376),
    "jaipur":       (26.9124,  75.7873),
    "ahmedabad":    (23.0225,  72.5714),
    "bhopal":       (23.2599,  77.4126),
    "indore":       (22.7196,  75.8577),
    "bangalore":    (12.9716,  77.5946),
    "mysore":       (12.2958,  76.6394),
    "chennai":      (13.0827,  80.2707),
    "coimbatore":   (11.0168,  76.9558),
    "madurai":      (9.9252,   78.1198),
    "kolkata":      (22.5726,  88.3639),
    "bhubaneswar":  (20.2961,  85.8245),
    "raipur":       (21.2514,  81.6296),
    "amritsar":     (31.6340,  74.8723),
    "ludhiana":     (30.9010,  75.8573),
    "chandigarh":   (30.7333,  76.7794),
    "dehradun":     (30.3165,  78.0322),
    "shimla":       (31.1048,  77.1734),
    "srinagar":     (34.0837,  74.7973),
    "guwahati":     (26.1445,  91.7362),
    "default":      (17.3850,  78.4867),  # Hyderabad as fallback
}


def _resolve_location(location: str) -> tuple[float, float]:
    """Return (lat, lon) for a given city name."""
    key = location.lower().strip()
    return INDIA_LOCATIONS.get(key, INDIA_LOCATIONS["default"])


def get_weather_forecast(location: str, days: int = 7) -> dict:
    """
    Fetch a real weather forecast for the given farming location.

    This tool calls the Open-Meteo API (free, no key needed) and returns
    current conditions plus a multi-day forecast — critical for planting
    and harvest decisions.

    Args:
        location: City or district name (e.g. "Hyderabad", "Warangal").
        days:     Number of forecast days to return (1–16). Default 7.

    Returns:
        A dict with keys:
          - location      : Resolved city name
          - current       : {temperature_c, humidity_pct, rain_mm,
                             wind_kph, condition}
          - daily_forecast: List of {date, max_temp_c, min_temp_c,
                             rain_mm, condition}
          - farming_notes : Plain-language advice derived from the forecast
          - source        : "Open-Meteo API (real-time)"
    """
    days = max(1, min(days, 16))
    lat, lon = _resolve_location(location)

    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude":               lat,
        "longitude":              lon,
        "current":                "temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m,weather_code",
        "daily":                  "temperature_2m_max,temperature_2m_min,precipitation_sum,weather_code",
        "timezone":               "Asia/Kolkata",
        "forecast_days":          days,
    }

    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        current_raw = data.get("current", {})
        daily_raw   = data.get("daily", {})

        current = {
            "temperature_c": current_raw.get("temperature_2m"),
            "humidity_pct":  current_raw.get("relative_humidity_2m"),
            "rain_mm":       current_raw.get("precipitation", 0),
            "wind_kph":      current_raw.get("wind_speed_10m"),
            "condition":     _weather_code_to_text(current_raw.get("weather_code", 0)),
        }

        dates       = daily_raw.get("time", [])
        max_temps   = daily_raw.get("temperature_2m_max", [])
        min_temps   = daily_raw.get("temperature_2m_min", [])
        rain_sums   = daily_raw.get("precipitation_sum", [])
        codes       = daily_raw.get("weather_code", [])

        daily_forecast = [
            {
                "date":        dates[i],
                "max_temp_c":  max_temps[i],
                "min_temp_c":  min_temps[i],
                "rain_mm":     rain_sums[i],
                "condition":   _weather_code_to_text(codes[i]),
            }
            for i in range(len(dates))
        ]

        farming_notes = _derive_farming_notes(current, daily_forecast)

        return {
            "location":       location.title(),
            "current":        current,
            "daily_forecast": daily_forecast,
            "farming_notes":  farming_notes,
            "source":         "Open-Meteo API (real-time)",
        }

    except requests.RequestException as e:
        return {
            "error":   str(e),
            "message": f"Could not fetch weather for {location}. Please check internet connection.",
        }


def _weather_code_to_text(code: int) -> str:
    """Convert WMO weather code to a human-readable description."""
    mapping = {
        0:  "Clear sky",
        1:  "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
        45: "Foggy", 48: "Icy fog",
        51: "Light drizzle", 53: "Moderate drizzle", 55: "Heavy drizzle",
        61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
        71: "Slight snowfall", 73: "Moderate snowfall", 75: "Heavy snowfall",
        80: "Slight showers", 81: "Moderate showers", 82: "Violent showers",
        95: "Thunderstorm", 96: "Thunderstorm with hail",
    }
    return mapping.get(code, f"Weather code {code}")


def _derive_farming_notes(current: dict, daily: list) -> list[str]:
    """Generate plain-language farming notes from weather data."""
    notes = []
    total_rain = sum(d.get("rain_mm", 0) for d in daily)
    max_temp   = max((d.get("max_temp_c", 0) for d in daily), default=0)

    if total_rain > 50:
        notes.append("Heavy rainfall expected this week — avoid sowing; ensure field drainage is clear.")
    elif total_rain < 5:
        notes.append("Dry week ahead — irrigate if crops are in sensitive growth stages.")
    else:
        notes.append("Moderate rainfall expected — good conditions for most field operations.")

    if max_temp and max_temp > 40:
        notes.append("Extreme heat alert: temperatures above 40°C expected — shade sensitive seedlings.")
    elif max_temp and max_temp < 15:
        notes.append("Cool temperatures ahead — ideal for rabi crops like wheat and mustard.")

    if current.get("humidity_pct", 0) > 80:
        notes.append("High humidity — watch for fungal diseases; consider preventive spraying.")

    return notes if notes else ["Weather conditions look stable for farming this week."]
