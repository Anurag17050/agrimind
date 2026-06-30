"""
market_tools.py
────────────────
Provides commodity price data and market trend analysis for Indian crops.

Note on data: The government portal (agmarknet.gov.in) doesn't offer a free
real-time JSON API, so Phase 1 uses a curated knowledge base of typical
Minimum Support Prices (MSPs) and seasonal patterns. In Phase 3 we will
wire this to a live data MCP server.

MSP source: Govt of India, Cabinet Committee on Economic Affairs (CCEA)
2024-25 season rates.
"""

from datetime import date

# ── Minimum Support Prices (₹ per quintal) — CCEA 2024-25 ───────────────────
MSP_2024_25 = {
    # Kharif crops (sown June-July, harvested Oct-Nov)
    "paddy":          2300,
    "rice":           2300,
    "jowar":          3371,
    "bajra":          2625,
    "maize":          2090,
    "cotton":         7121,   # medium staple (per quintal)
    "groundnut":      6783,
    "soybean":        4892,
    "sunflower":      7280,
    "turmeric":       9000,   # indicative (not MSP)
    "chillies":       12000,  # indicative
    "moong":          8682,
    "urad":           7400,
    "tur":            7550,
    # Rabi crops (sown Nov-Dec, harvested Mar-Apr)
    "wheat":          2275,
    "barley":         1735,
    "gram":           5440,
    "lentil":         6425,
    "mustard":        5950,
    "safflower":      5800,
}

# ── Typical market premium / discount over MSP ────────────────────────────────
# Methodology: these percentages are illustrative estimates derived from
# observed APMC mandi price patterns relative to MSP for 2023-24/2024-25,
# NOT a live feed. They model the general direction (which crops typically
# trade above/below MSP and by roughly how much) so the agent can give
# directionally correct sell/hold advice in this demo. A production version
# would replace this with a live Agmarknet/eNAM mandi price API call per
# state/district, since real premiums vary day-to-day and by location.
# Positive = market usually pays above MSP; Negative = below MSP risk
MARKET_PREMIUM_PCT = {
    "paddy":     -5,   "rice":     5,   "jowar":   10,
    "bajra":      5,   "maize":   15,   "cotton":  20,
    "groundnut": 25,   "soybean": 10,   "sunflower": 5,
    "wheat":     10,   "gram":    30,   "lentil":  35,
    "mustard":   20,   "tur":     40,   "moong":   45,
    "urad":      30,   "turmeric": 80,  "chillies": 60,
}

# ── Seasonal sowing calendar ───────────────────────────────────────────────────
SEASON_CALENDAR = {
    "kharif":  {"sow_months": [6, 7],    "harvest_months": [10, 11, 12]},
    "rabi":    {"sow_months": [10, 11],  "harvest_months": [3,  4]},
    "zaid":    {"sow_months": [2, 3],    "harvest_months": [5,  6]},
}

CROP_TO_SEASON = {
    "paddy": "kharif", "rice": "kharif", "jowar": "kharif",
    "bajra": "kharif", "maize": "kharif", "cotton": "kharif",
    "groundnut": "kharif", "soybean": "kharif", "sunflower": "kharif",
    "moong": "kharif", "urad": "kharif", "tur": "kharif",
    "turmeric": "kharif", "chillies": "kharif",
    "wheat": "rabi", "barley": "rabi", "gram": "rabi",
    "lentil": "rabi", "mustard": "rabi", "safflower": "rabi",
}


def get_commodity_price(crop_name: str, state: str = "Telangana") -> dict:
    """
    Return MSP, estimated market price, and trading advice for a crop.

    Args:
        crop_name : Name of the crop (e.g. "cotton", "paddy", "wheat").
        state     : Indian state for regional price context.

    Returns:
        A dict with:
          - crop            : Normalised crop name
          - msp_per_quintal : Government Minimum Support Price (₹)
          - est_market_price: Estimated current market price (₹)
          - season          : Kharif / Rabi / Zaid
          - timing_advice   : Whether it's a good time to sell/hold
          - trend           : "bullish" | "bearish" | "stable"
          - recommendation  : Plain-language advice for the farmer
          - source          : Data provenance note
    """
    crop = crop_name.lower().strip()

    if crop not in MSP_2024_25:
        # Fuzzy match — try to find the closest crop name
        matches = [c for c in MSP_2024_25 if crop in c or c in crop]
        if matches:
            crop = matches[0]
        else:
            return {
                "error":       f"Crop '{crop_name}' not found in database.",
                "known_crops": sorted(MSP_2024_25.keys()),
                "suggestion":  "Try one of the known crops listed above.",
            }

    msp      = MSP_2024_25[crop]
    premium  = MARKET_PREMIUM_PCT.get(crop, 0)
    est_mkt  = int(msp * (1 + premium / 100))
    season   = CROP_TO_SEASON.get(crop, "unknown")

    # Seasonal timing advice
    today         = date.today()
    current_month = today.month
    cal           = SEASON_CALENDAR.get(season, {})
    harvest_months = cal.get("harvest_months", [])

    if current_month in harvest_months:
        timing_advice = "Peak harvest season — market competition is high; consider storing 30% for later sale."
    elif current_month in [(m % 12) + 1 for m in [max(harvest_months, default=6) + x for x in range(1, 3)]]:
        timing_advice = "Post-harvest period — prices typically rise 10-15% over the next 60 days."
    else:
        timing_advice = "Off-season for this crop — stored stock is likely fetching a good premium now."

    trend = "bullish" if premium > 20 else ("bearish" if premium < -5 else "stable")

    recommendation = (
        f"Current estimated market rate for {crop.title()} in {state} is "
        f"₹{est_mkt:,}/quintal vs. MSP of ₹{msp:,}/quintal "
        f"({'+' if premium >= 0 else ''}{premium}% above MSP). "
        f"{timing_advice}"
    )

    return {
        "crop":             crop.title(),
        "state":            state,
        "msp_per_quintal":  msp,
        "est_market_price": est_mkt,
        "premium_over_msp": f"{'+' if premium >= 0 else ''}{premium}%",
        "season":           season.title(),
        "timing_advice":    timing_advice,
        "trend":            trend,
        "recommendation":   recommendation,
        "source":           "CCEA MSP 2024-25 + seasonal market analysis",
    }
