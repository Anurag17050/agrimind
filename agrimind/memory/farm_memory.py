"""
farm_memory.py
───────────────
Long-term memory for AgriMind — stores and retrieves farmer profiles.

Each farmer gets a JSON file in data/farm_profiles/ that persists between
sessions. This is the "Long-term Memory" concept from the ADK course.

The memory includes:
  - Farm location and soil type
  - Crops currently being grown
  - Past questions and advice given
  - Seasonal history (what was grown, what the outcomes were)
"""

import json
import os
from datetime import date, datetime
from pathlib import Path

# ── Storage path ───────────────────────────────────────────────────────────────
# Resolves to agrimind/data/farm_profiles/ relative to the project root
_PROJECT_ROOT  = Path(__file__).resolve().parent.parent.parent
PROFILES_DIR   = _PROJECT_ROOT / "data" / "farm_profiles"
PROFILES_DIR.mkdir(parents=True, exist_ok=True)


def _profile_path(farmer_id: str) -> Path:
    safe_id = "".join(c for c in farmer_id if c.isalnum() or c in "-_")
    return PROFILES_DIR / f"{safe_id}.json"


# ── Core memory tools (exposed as ADK agent tools) ────────────────────────────

def save_farm_profile(
    farmer_id:    str,
    farmer_name:  str,
    location:     str,
    soil_type:    str,
    farm_size_acres: float,
    current_crops:   list[str],
    water_source: str = "rainfed",
) -> dict:
    """
    Create or update a farmer's long-term profile in memory.

    Call this at the start of a new farmer's first session, or whenever
    their farm details change (new crop, relocated, etc.).

    Args:
        farmer_id:       Unique ID for this farmer (e.g. "farmer_001").
        farmer_name:     Farmer's name.
        location:        City/district (e.g. "Warangal").
        soil_type:       Soil type — "black", "red", "alluvial", "loamy".
        farm_size_acres: Total farm area in acres.
        current_crops:   List of crops currently being grown.
        water_source:    "rainfed" | "canal" | "borewell" | "drip".

    Returns:
        Confirmation dict with the saved profile.
    """
    path = _profile_path(farmer_id)

    # Load existing profile if it exists (preserve history)
    if path.exists():
        with open(path) as f:
            profile = json.load(f)
    else:
        profile = {
            "farmer_id":      farmer_id,
            "created_at":     datetime.now().isoformat(),
            "query_history":  [],
            "season_history": [],
        }

    profile.update({
        "farmer_name":    farmer_name,
        "location":       location,
        "soil_type":      soil_type,
        "farm_size_acres": farm_size_acres,
        "current_crops":  current_crops,
        "water_source":   water_source,
        "updated_at":     datetime.now().isoformat(),
    })

    with open(path, "w") as f:
        json.dump(profile, f, indent=2, default=str)

    return {
        "status":     "saved",
        "farmer_id":  farmer_id,
        "farmer_name": farmer_name,
        "location":   location,
        "message":    f"Profile for {farmer_name} saved. AgriMind will remember your farm details in future sessions.",
    }


def get_farm_profile(farmer_id: str) -> dict:
    """
    Retrieve a farmer's stored profile and history.

    Args:
        farmer_id: The farmer's unique ID.

    Returns:
        The full profile dict, or a 'not_found' response.
    """
    path = _profile_path(farmer_id)
    if not path.exists():
        return {
            "status":     "not_found",
            "farmer_id":  farmer_id,
            "message":    "No profile found. Please provide your farm details so AgriMind can remember you.",
        }

    with open(path) as f:
        return json.load(f)


def log_advice_given(
    farmer_id: str,
    question:  str,
    advice:    str,
    topic:     str,
) -> dict:
    """
    Append a question-answer pair to the farmer's history log.

    This builds the long-term memory of what advice was given,
    so AgriMind doesn't repeat itself and can track outcomes.

    Args:
        farmer_id: The farmer's unique ID.
        question:  What the farmer asked.
        advice:    The advice given (summary).
        topic:     Category — "weather" | "crop" | "market" | "disease".

    Returns:
        Confirmation of the logged entry.
    """
    path = _profile_path(farmer_id)
    if not path.exists():
        return {"status": "error", "message": f"No profile found for {farmer_id}."}

    with open(path) as f:
        profile = json.load(f)

    entry = {
        "date":     date.today().isoformat(),
        "topic":    topic,
        "question": question[:200],   # truncate long questions
        "advice":   advice[:500],     # truncate long advice
    }

    profile.setdefault("query_history", []).append(entry)

    # Keep only last 50 entries to avoid unbounded growth
    profile["query_history"] = profile["query_history"][-50:]

    with open(path, "w") as f:
        json.dump(profile, f, indent=2, default=str)

    return {"status": "logged", "topic": topic, "date": entry["date"]}


def get_recent_advice(farmer_id: str, last_n: int = 5) -> dict:
    """
    Retrieve the most recent advice given to a farmer.

    Useful for the orchestrator to provide context-aware responses
    (e.g. "Following up on the cotton advice we gave last week...").

    Args:
        farmer_id: The farmer's unique ID.
        last_n:    Number of recent entries to return (default 5).

    Returns:
        List of recent question-advice pairs with dates.
    """
    profile = get_farm_profile(farmer_id)
    if profile.get("status") == "not_found":
        return profile

    history = profile.get("query_history", [])
    recent  = history[-last_n:] if history else []

    return {
        "farmer_id":    farmer_id,
        "farmer_name":  profile.get("farmer_name", "Unknown"),
        "recent_advice": recent,
        "total_interactions": len(history),
    }
