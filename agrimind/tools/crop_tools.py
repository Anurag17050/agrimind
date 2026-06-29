"""
crop_tools.py
──────────────
Knowledge-based crop recommendation and soil advisory tools.

These tools encode agronomic knowledge for Indian farming conditions —
what to grow, when to grow it, and what the soil needs.
"""

from datetime import date

# ── Crop Knowledge Base ───────────────────────────────────────────────────────
# Each crop entry covers: ideal soil, rainfall, temp range, duration (days),
# typical yield (quintals/acre), and key care tips.
CROP_KNOWLEDGE = {
    "paddy": {
        "soil_types":       ["clay", "loamy", "alluvial"],
        "rainfall_mm":      (1000, 2000),
        "temp_range_c":     (20, 37),
        "duration_days":    (90, 150),
        "yield_q_per_acre": (15, 30),
        "states":           ["Telangana", "Andhra Pradesh", "West Bengal", "Punjab", "Odisha"],
        "care_tips": [
            "Transplant 25-day-old seedlings into well-puddled soil.",
            "Maintain 5 cm standing water during tillering.",
            "Apply nitrogen in 3 splits: basal, tillering, panicle initiation.",
            "Scout for brown plant hopper and blast disease from 30 DAT.",
        ],
        "companion_crops":  ["green manure", "moong (after harvest)"],
    },
    "cotton": {
        "soil_types":       ["black cotton", "red loamy", "alluvial"],
        "rainfall_mm":      (500, 1000),
        "temp_range_c":     (21, 35),
        "duration_days":    (160, 200),
        "yield_q_per_acre": (8, 15),
        "states":           ["Telangana", "Maharashtra", "Gujarat", "Andhra Pradesh"],
        "care_tips": [
            "Use Bt cotton varieties for bollworm resistance.",
            "Spacing: 90 × 60 cm for rainfed; 90 × 45 cm for irrigated.",
            "Avoid waterlogging — cotton roots are highly sensitive.",
            "Apply potassium at squaring stage to improve fibre quality.",
        ],
        "companion_crops":  ["groundnut (inter-row)", "cluster bean"],
    },
    "maize": {
        "soil_types":       ["sandy loam", "red", "loamy"],
        "rainfall_mm":      (500, 900),
        "temp_range_c":     (18, 32),
        "duration_days":    (80, 110),
        "yield_q_per_acre": (20, 40),
        "states":           ["Telangana", "Karnataka", "Andhra Pradesh", "Rajasthan"],
        "care_tips": [
            "Sow at 60 × 25 cm spacing for optimal plant population.",
            "Apply 120 kg N/ha in 4 splits for maximum yield.",
            "Watch for fall armyworm — apply recommended insecticide at early infestation.",
            "Harvest when husks turn brown and grains dent.",
        ],
        "companion_crops":  ["beans", "pumpkin"],
    },
    "wheat": {
        "soil_types":       ["alluvial", "clay loam", "black"],
        "rainfall_mm":      (250, 750),
        "temp_range_c":     (10, 25),
        "duration_days":    (100, 130),
        "yield_q_per_acre": (15, 25),
        "states":           ["Punjab", "Haryana", "Uttar Pradesh", "Madhya Pradesh"],
        "care_tips": [
            "Sow at 100–125 kg seed/ha. Treat seed with Vitavax for smut control.",
            "First irrigation critical at Crown Root Initiation (CRI) stage (21 DAS).",
            "Apply pre-emergence herbicide for phalaris minor control.",
            "Harvest at 20% grain moisture to minimise shattering losses.",
        ],
        "companion_crops":  ["mustard (border crop)"],
    },
    "groundnut": {
        "soil_types":       ["red", "sandy loam", "light alluvial"],
        "rainfall_mm":      (500, 1250),
        "temp_range_c":     (25, 35),
        "duration_days":    (90, 130),
        "yield_q_per_acre": (8, 12),
        "states":           ["Andhra Pradesh", "Telangana", "Gujarat", "Tamil Nadu"],
        "care_tips": [
            "Treat seed with Rhizobium culture for nitrogen fixation.",
            "Earth up at 30–35 DAS to facilitate pegging.",
            "Apply gypsum (500 kg/ha) at flower initiation for calcium.",
            "Avoid irrigation 10 days before harvest for good shell cure.",
        ],
        "companion_crops":  ["bajra", "castor (border)"],
    },
    "soybean": {
        "soil_types":       ["black", "medium black", "loamy"],
        "rainfall_mm":      (600, 1000),
        "temp_range_c":     (20, 30),
        "duration_days":    (90, 110),
        "yield_q_per_acre": (8, 15),
        "states":           ["Madhya Pradesh", "Maharashtra", "Telangana", "Rajasthan"],
        "care_tips": [
            "Use Bradyrhizobium seed inoculant — reduces nitrogen fertiliser need.",
            "Sow within first week of July for best yields.",
            "Inter-row cultivation at 30 DAS controls weeds effectively.",
            "Yellow mosaic virus (spread by whitefly) is the key threat — use resistant varieties.",
        ],
        "companion_crops":  ["pigeonpea", "maize"],
    },
    "tur": {
        "soil_types":       ["red", "black", "loamy"],
        "rainfall_mm":      (600, 1000),
        "temp_range_c":     (20, 35),
        "duration_days":    (150, 270),
        "yield_q_per_acre": (4, 8),
        "states":           ["Telangana", "Maharashtra", "Karnataka", "Uttar Pradesh"],
        "care_tips": [
            "Use short-duration varieties (ICPL 87119) for earlier return.",
            "Deep tap root — requires deep tillage before sowing.",
            "Monitor for pod borer (Helicoverpa armigera) — major yield loss pest.",
            "Harvest when 80% pods turn brown.",
        ],
        "companion_crops":  ["sorghum", "cotton (inter-row)"],
    },
}

SOIL_TYPE_INFO = {
    "black": {
        "also_known_as": "Regur / cotton soil",
        "nutrient_status": "Rich in calcium, magnesium; low in nitrogen and phosphorus",
        "water_retention": "Very high — waterlogging risk in rainy season",
        "best_crops": ["cotton", "soybean", "tur", "wheat", "sunflower"],
        "amendments": ["Add phosphorus (SSP) and zinc sulphate. Avoid over-irrigation."],
    },
    "red": {
        "also_known_as": "Red laterite soil",
        "nutrient_status": "Low in nitrogen, phosphorus, organic matter; rich in iron",
        "water_retention": "Low — needs frequent irrigation or mulching",
        "best_crops": ["groundnut", "maize", "jowar", "bajra", "tur"],
        "amendments": ["Add FYM or vermicompost. Lime if pH < 6. Apply potassium."],
    },
    "alluvial": {
        "also_known_as": "Domat / river deposit soil",
        "nutrient_status": "Fertile — good nitrogen and phosphorus; varies by region",
        "water_retention": "Moderate to good",
        "best_crops": ["wheat", "paddy", "maize", "vegetables", "sugarcane"],
        "amendments": ["Balanced NPK. Maintain organic matter with FYM."],
    },
    "loamy": {
        "also_known_as": "Sandy loam / medium soil",
        "nutrient_status": "Moderate — balanced texture",
        "water_retention": "Good",
        "best_crops": ["most crops", "paddy", "cotton", "vegetables"],
        "amendments": ["Regular FYM application. Monitor micronutrients (zinc, boron)."],
    },
    "sandy": {
        "also_known_as": "Light soil",
        "nutrient_status": "Low — nutrients leach quickly",
        "water_retention": "Very low — frequent irrigation needed",
        "best_crops": ["groundnut", "bajra", "watermelon", "vegetables"],
        "amendments": ["Heavy organic matter addition. Drip irrigation recommended."],
    },
}


def get_crop_recommendation(
    location: str,
    soil_type: str,
    season: str = "kharif",
    water_availability: str = "rainfed",
) -> dict:
    """
    Recommend the best crops for a farmer based on their local conditions.

    Args:
        location:           District/city name (e.g. "Warangal").
        soil_type:          Soil type — "black", "red", "alluvial", "loamy", "sandy".
        season:             "kharif" (June-Nov) | "rabi" (Nov-Apr) | "zaid" (Feb-May).
        water_availability: "rainfed" | "irrigated" | "limited".

    Returns:
        Dict with recommended crops, yield estimates, and care priorities.
    """
    soil  = soil_type.lower().strip()
    seas  = season.lower().strip()
    water = water_availability.lower().strip()

    SEASON_CROPS = {
        "kharif": ["paddy", "cotton", "maize", "groundnut", "soybean", "tur"],
        "rabi":   ["wheat", "gram", "mustard", "lentil", "safflower"],
        "zaid":   ["maize", "moong", "watermelon", "vegetables"],
    }
    candidate_names = SEASON_CROPS.get(seas, SEASON_CROPS["kharif"])

    # Filter by soil compatibility
    recommendations = []
    for crop_name in candidate_names:
        info = CROP_KNOWLEDGE.get(crop_name)
        if not info:
            continue
        soil_match = any(soil in st for st in info["soil_types"])
        if not soil_match:
            continue

        # Adjust yield for irrigation
        low_y, high_y = info["yield_q_per_acre"]
        if water == "irrigated":
            high_y = int(high_y * 1.3)
        elif water == "limited":
            high_y = int(high_y * 0.8)

        recommendations.append({
            "crop":             crop_name.title(),
            "expected_yield":   f"{low_y}–{high_y} quintals/acre",
            "duration_days":    f"{info['duration_days'][0]}–{info['duration_days'][1]} days",
            "top_care_tip":     info["care_tips"][0],
            "companion_crops":  info["companion_crops"],
        })

    if not recommendations:
        recommendations = [{
            "crop":           "Soybean (default)",
            "expected_yield": "8–15 quintals/acre",
            "note":           "Versatile crop for most soil types in kharif season.",
        }]

    return {
        "location":           location.title(),
        "soil_type":          soil.title(),
        "season":             seas.title(),
        "water_availability": water.title(),
        "recommended_crops":  recommendations[:4],  # top 4 matches
        "planting_window":    _get_planting_window(seas),
        "source":             "ICAR agronomic guidelines + MSP data",
    }


def get_soil_advice(soil_type: str) -> dict:
    """
    Return detailed soil improvement advice for a given soil type.

    Args:
        soil_type: One of "black", "red", "alluvial", "loamy", "sandy".

    Returns:
        Dict with soil characteristics, best crops, and amendment advice.
    """
    soil = soil_type.lower().strip()
    # Handle common aliases
    aliases = {
        "cotton soil": "black", "regur": "black",
        "laterite": "red",
        "sandy loam": "loamy", "medium": "loamy",
    }
    soil = aliases.get(soil, soil)

    info = SOIL_TYPE_INFO.get(soil)
    if not info:
        return {
            "error":       f"Soil type '{soil_type}' not recognised.",
            "known_types": list(SOIL_TYPE_INFO.keys()),
        }

    return {
        "soil_type":         soil.title(),
        "also_known_as":     info["also_known_as"],
        "nutrient_status":   info["nutrient_status"],
        "water_retention":   info["water_retention"],
        "best_suited_crops": info["best_crops"],
        "improvement_steps": info["amendments"],
        "source":            "ICAR soil management guidelines",
    }


def _get_planting_window(season: str) -> str:
    windows = {
        "kharif": "June 1 – July 31 (sow after first monsoon rains)",
        "rabi":   "October 15 – November 30 (after kharif harvest)",
        "zaid":   "February 15 – March 31 (short summer season)",
    }
    return windows.get(season, "Consult local agriculture office for timing.")
