"""
guardrails.py
──────────────
Input validation and safety guardrails for AgriMind.

These guardrails implement the "Security features" concept from the ADK course.
They ensure AgriMind:
  1. Only answers questions relevant to farming
  2. Never gives dangerous advice (e.g. recommending banned pesticides)
  3. Sanitises inputs to prevent injection attacks
  4. Adds appropriate safety disclaimers where needed
"""

import re

# ── Banned substances (legally prohibited in India) ───────────────────────────
BANNED_PESTICIDES = [
    "endosulfan", "monocrotophos", "methyl parathion", "phorate",
    "carbaryl", "lindane", "ddt", "aldrin", "dieldrin", "heptachlor",
    "chlordane", "toxaphene", "mirex",
]

# ── Off-topic detection — these topics are outside AgriMind's scope ───────────
OFF_TOPIC_KEYWORDS = [
    "politics", "cricket", "movie", "film", "actor", "stock market",
    "bitcoin", "crypto", "relationship", "recipe", "cook",
    "travel", "tourism", "hotel", "flight",
]

# ── Sensitive advice requiring a professional disclaimer ─────────────────────
DISCLAIMER_TOPICS = [
    "pesticide", "insecticide", "fungicide", "herbicide", "chemical",
    "dose", "dosage", "spray", "fertiliser", "fertilizer",
]


def validate_query(query: str) -> dict:
    """
    Validate an incoming farmer query before processing.

    Checks for:
      - Empty or too-short queries
      - Off-topic content
      - Requests for banned substances
      - Inputs that are too long (potential injection)

    Args:
        query: The raw text input from the farmer.

    Returns:
        {
          "is_valid"  : bool,
          "clean_query": str  (sanitised version),
          "warning"   : str | None,
          "block_reason": str | None  (set if is_valid is False),
        }
    """
    if not query or len(query.strip()) < 5:
        return {
            "is_valid":     False,
            "clean_query":  "",
            "warning":      None,
            "block_reason": "Query is too short. Please describe your farming question in more detail.",
        }

    if len(query) > 2000:
        return {
            "is_valid":     False,
            "clean_query":  "",
            "warning":      None,
            "block_reason": "Query is too long (max 2000 characters). Please ask one question at a time.",
        }

    # Sanitise: strip HTML/script-like patterns
    clean = re.sub(r"<[^>]+>", "", query)          # strip HTML tags
    clean = re.sub(r"[;{}\\]", "", clean)           # strip injection chars
    clean = clean.strip()

    query_lower = clean.lower()

    # Check for banned pesticides
    for substance in BANNED_PESTICIDES:
        if substance in query_lower:
            return {
                "is_valid":     False,
                "clean_query":  clean,
                "warning":      None,
                "block_reason": (
                    f"'{substance.title()}' is legally banned in India under the "
                    f"Insecticides Act. AgriMind cannot provide advice on prohibited substances. "
                    f"Please contact your local agriculture office for legal alternatives."
                ),
            }

    # Check for off-topic content
    for kw in OFF_TOPIC_KEYWORDS:
        if kw in query_lower:
            return {
                "is_valid":     False,
                "clean_query":  clean,
                "warning":      None,
                "block_reason": (
                    f"AgriMind specialises in farming advice only. "
                    f"Your question appears to be about '{kw}' which is outside my scope. "
                    f"Please ask about crops, weather, soil, pest management, or market prices."
                ),
            }

    # Add disclaimer for chemical-related queries
    warning = None
    for topic in DISCLAIMER_TOPICS:
        if topic in query_lower:
            warning = (
                "⚠️  Pesticide/fertiliser advice from AgriMind is for guidance only. "
                "Always read product labels, follow prescribed doses, and consult your "
                "local Krishi Vigyan Kendra (KVK) before application."
            )
            break

    return {
        "is_valid":     True,
        "clean_query":  clean,
        "warning":      warning,
        "block_reason": None,
    }


def add_safety_footer(response: str, topic: str) -> str:
    """
    Append a context-appropriate safety note to agent responses.

    Args:
        response: The agent's generated response text.
        topic:    Topic category ("weather"|"crop"|"market"|"disease"|"general").

    Returns:
        Response with an appended safety note.
    """
    footers = {
        "disease": (
            "\n\n---\n📋 *Always confirm identification with a local expert before "
            "applying any pesticide. Misidentification can waste money and harm crops.*"
        ),
        "market": (
            "\n\n---\n📋 *Market prices fluctuate daily. Verify at your nearest APMC mandi "
            "before making selling decisions.*"
        ),
        "crop": (
            "\n\n---\n📋 *Local conditions vary. Check with your Krishi Vigyan Kendra "
            "for variety recommendations specific to your block.*"
        ),
        "weather": (
            "\n\n---\n📋 *Weather forecasts are probabilistic. Always check the IMD "
            "(imd.gov.in) app for the latest updates before critical field operations.*"
        ),
    }
    return response + footers.get(topic, "")
