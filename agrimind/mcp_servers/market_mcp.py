"""
market_mcp.py — AgriMind Market Data MCP Server
─────────────────────────────────────────────────
A standalone MCP server exposing commodity price data as an MCP tool.
ADK's market_agent connects to this server via MCPToolset.

Demonstrates:
  ✅ Custom MCP server with FastMCP
  ✅ Domain knowledge (MSP 2024-25) exposed as standardised MCP tool
  ✅ Clean separation between data layer and agent layer
"""

from datetime import date
from mcp.server.fastmcp import FastMCP

mcp = FastMCP(
    name="agrimind-market-mcp",
    instructions=(
        "Provides Minimum Support Prices (MSP) and market price estimates "
        "for Indian agricultural commodities. Use get_commodity_price to get "
        "current prices, market trends, and sell/hold recommendations."
    ),
)

# ── MSP 2024-25 data ──────────────────────────────────────────────────────────
MSP_2024_25 = {
    "paddy": 2300, "rice": 2300, "jowar": 3371, "bajra": 2625,
    "maize": 2090, "cotton": 7121, "groundnut": 6783, "soybean": 4892,
    "sunflower": 7280, "turmeric": 9000, "chillies": 12000,
    "moong": 8682, "urad": 7400, "tur": 7550,
    "wheat": 2275, "barley": 1735, "gram": 5440, "lentil": 6425,
    "mustard": 5950, "safflower": 5800,
}

MARKET_PREMIUM_PCT = {
    "paddy": -5, "rice": 5, "jowar": 10, "bajra": 5, "maize": 15,
    "cotton": 20, "groundnut": 25, "soybean": 10, "sunflower": 5,
    "wheat": 10, "gram": 30, "lentil": 35, "mustard": 20,
    "tur": 40, "moong": 45, "urad": 30, "turmeric": 80, "chillies": 60,
}

CROP_TO_SEASON = {
    "paddy": "kharif", "rice": "kharif", "jowar": "kharif", "bajra": "kharif",
    "maize": "kharif", "cotton": "kharif", "groundnut": "kharif",
    "soybean": "kharif", "sunflower": "kharif", "moong": "kharif",
    "urad": "kharif", "tur": "kharif", "turmeric": "kharif", "chillies": "kharif",
    "wheat": "rabi", "barley": "rabi", "gram": "rabi",
    "lentil": "rabi", "mustard": "rabi", "safflower": "rabi",
}

SEASON_CALENDAR = {
    "kharif": {"harvest_months": [10, 11, 12]},
    "rabi":   {"harvest_months": [3, 4]},
}


@mcp.tool()
def get_commodity_price(crop_name: str, state: str = "Telangana") -> dict:
    """
    Get MSP, estimated market price, and sell/hold recommendation for a crop.

    Uses CCEA MSP 2024-25 data plus seasonal market analysis to give
    farmers actionable price intelligence.

    Args:
        crop_name: Crop name e.g. "cotton", "paddy", "wheat", "tur", "soybean".
        state:     Indian state for regional context. Default: "Telangana".

    Returns:
        Dict with MSP, estimated market price, premium over MSP,
        seasonal timing advice, trend, and plain-language recommendation.
    """
    crop = crop_name.lower().strip()

    if crop not in MSP_2024_25:
        matches = [c for c in MSP_2024_25 if crop in c or c in crop]
        if matches:
            crop = matches[0]
        else:
            return {
                "error":       f"Crop '{crop_name}' not in database.",
                "known_crops": sorted(MSP_2024_25.keys()),
            }

    msp     = MSP_2024_25[crop]
    premium = MARKET_PREMIUM_PCT.get(crop, 0)
    est_mkt = int(msp * (1 + premium / 100))
    season  = CROP_TO_SEASON.get(crop, "unknown")

    current_month  = date.today().month
    harvest_months = SEASON_CALENDAR.get(season, {}).get("harvest_months", [])

    if current_month in harvest_months:
        timing = "Peak harvest season — prices are competitive; consider storing 30% for 60 days."
    else:
        timing = "Off-peak — stored stock is likely fetching a good premium now."

    trend = "bullish" if premium > 20 else ("bearish" if premium < -5 else "stable")

    return {
        "crop":             crop.title(),
        "state":            state,
        "msp_per_quintal":  msp,
        "est_market_price": est_mkt,
        "premium_over_msp": f"{'+' if premium >= 0 else ''}{premium}%",
        "season":           season.title(),
        "timing_advice":    timing,
        "trend":            trend,
        "recommendation": (
            f"{crop.title()} estimated at ₹{est_mkt:,}/quintal "
            f"({'+' if premium >= 0 else ''}{premium}% above MSP of ₹{msp:,}). "
            f"Trend: {trend}. {timing}"
        ),
        "source": "CCEA MSP 2024-25 + seasonal analysis via AgriMind Market MCP",
    }


if __name__ == "__main__":
    mcp.run()
