"""
context_manager.py
───────────────────
Context Engineering for AgriMind.

Builds a compact farm context string from a farmer's stored profile
and injects it into every conversation turn. This means:
  - Agents always know the farmer's location, soil, crops without asking
  - No redundant memory tool calls every turn
  - Responses are immediately personalised from message #1

ADK Course concept demonstrated: Context Engineering
"""

from agrimind.memory.farm_memory import get_farm_profile


def build_farm_context(farmer_id: str) -> str:
    """
    Build a compact farm context string from the farmer's stored profile.

    This string gets prepended to every user message so all agents
    have the farmer's key details without needing to call get_farm_profile.

    Args:
        farmer_id: The farmer's unique ID.

    Returns:
        A compact context string, or empty string if no profile found.
    """
    profile = get_farm_profile(farmer_id)

    if profile.get("status") == "not_found":
        return ""

    name     = profile.get("farmer_name", "Unknown")
    location = profile.get("location", "Unknown")
    soil     = profile.get("soil_type", "Unknown")
    size     = profile.get("farm_size_acres", "?")
    crops    = ", ".join(profile.get("current_crops", []))
    water    = profile.get("water_source", "rainfed")
    history  = profile.get("query_history", [])
    last_q   = history[-1] if history else None

    context = (
        f"[FARMER CONTEXT — inject silently, do not repeat to farmer]\n"
        f"Name: {name} | Location: {location} | Soil: {soil} soil\n"
        f"Farm: {size} acres | Crops: {crops} | Water: {water}\n"
    )

    if last_q:
        context += (
            f"Last interaction ({last_q['date']}): "
            f"{last_q['topic']} — {last_q['question'][:80]}\n"
        )

    context += "[Use this context to personalise your response immediately]\n\n"

    return context


def inject_context(farmer_id: str, user_message: str) -> str:
    """
    Prepend farm context to a user message before sending to the agent.

    Args:
        farmer_id:    The farmer's unique ID.
        user_message: The raw message from the farmer.

    Returns:
        The message with farm context prepended (if profile exists).
    """
    context = build_farm_context(farmer_id)
    if context:
        return context + user_message
    return user_message
