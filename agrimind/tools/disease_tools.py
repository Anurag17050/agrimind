"""
disease_tools.py
─────────────────
Pest and disease identification and management advisory for Indian crops.

Knowledge base covers the most economically damaging threats in Indian
agriculture, based on ICAR and NCIPM (National Centre for Integrated Pest
Management) guidelines.
"""

# ── Disease / Pest Knowledge Base ─────────────────────────────────────────────
PEST_DISEASE_DB = {
    # ── Fungal diseases ──────────────────────────────────────────────────────
    "blast": {
        "type":         "Fungal disease",
        "pathogen":     "Magnaporthe oryzae",
        "affects":      ["paddy", "rice"],
        "symptoms": [
            "Diamond-shaped grey lesions with brown borders on leaves",
            "Neck rot — panicle neck turns brown and collapses (most damaging)",
            "Node blast causes stem breakage",
        ],
        "conditions":   "Favoured by cool nights (20-24°C), high humidity, excess nitrogen",
        "management": [
            "Spray Tricyclazole 75 WP @ 0.6 g/litre at boot leaf stage",
            "Avoid excess nitrogen at tillering",
            "Grow resistant varieties (MTU 1010, Swarna Sub1)",
            "Silicon application strengthens cell walls against penetration",
        ],
        "economic_loss": "Up to 70% yield loss in severe neck blast",
        "scouting_tip":  "Check flag leaf and neck 5–10 days before heading",
    },
    "yellow_mosaic": {
        "type":         "Viral disease",
        "pathogen":     "Yellow Mosaic Virus (YMV) via whitefly",
        "affects":      ["soybean", "moong", "urad"],
        "symptoms": [
            "Bright yellow patches (mosaic) on leaves",
            "Leaves become completely yellow and curl downward",
            "Stunted plant growth; poor pod development",
        ],
        "conditions":   "Whitefly population explodes in hot, dry weather",
        "management": [
            "Grow resistant varieties: JS 20-29, NRC 86 for soybean",
            "Control whitefly with Imidacloprid 70 WS @ 7 g/kg seed (seed treatment)",
            "Remove and burn infected plants early to reduce spread",
            "Spray reflective mulch strips to repel whiteflies",
        ],
        "economic_loss": "30–100% yield loss if infection occurs at seedling stage",
        "scouting_tip":  "Inspect undersides of leaves for whitefly colonies from 15 DAS",
    },
    "boll_worm": {
        "type":         "Insect pest",
        "pathogen":     "Helicoverpa armigera (American bollworm)",
        "affects":      ["cotton", "tur", "chickpea", "tomato"],
        "symptoms": [
            "Circular holes in cotton bolls, each with frass (excreta) entry",
            "Larvae feed inside bolls — only exit damage is visible",
            "Premature boll shedding; reduced fibre quality",
        ],
        "conditions":   "Peak attack during boll formation; monsoon break favours build-up",
        "management": [
            "Deploy pheromone traps (5/acre) from 45 DAG — monitor weekly",
            "Spray Chlorantraniliprole 18.5 SC @ 0.3 ml/litre at first instar",
            "Use NPV (Nuclear Polyhedrosis Virus) @ 250 LE/ha as bio-control",
            "Bt cotton reduces damage but supplementary sprays still needed",
        ],
        "economic_loss": "20–50% loss if unmanaged; Helicoverpa is most costly pest in India",
        "scouting_tip":  "Check 20 bolls per acre; act if >10% show entry holes",
    },
    "fall_armyworm": {
        "type":         "Insect pest",
        "pathogen":     "Spodoptera frugiperda",
        "affects":      ["maize", "sorghum", "wheat"],
        "symptoms": [
            "Ragged window-pane feeding on young leaves",
            "Frass (sawdust-like excreta) in the whorl",
            "Caterpillar head capsule has inverted Y mark",
        ],
        "conditions":   "Attacks from seedling to tassel stage; worst in warm humid weather",
        "management": [
            "Apply sand + neem seed powder (10:1) into whorl at first sign",
            "Spray Emamectin benzoate 5 SG @ 0.4 g/litre — most effective",
            "Release egg parasitoid Telenomus remus for bio-control",
            "Early sowing avoids peak population pressure",
        ],
        "economic_loss": "Can cause 20–60% yield loss in maize if unmanaged",
        "scouting_tip":  "Check 20 plants at whorl stage; act if >5% show feeding damage",
    },
    "powdery_mildew": {
        "type":         "Fungal disease",
        "pathogen":     "Erysiphe cichoracearum / Podosphaera spp.",
        "affects":      ["wheat", "gram", "peas", "grapes"],
        "symptoms": [
            "White powdery coating on upper leaf surface",
            "Affected leaves turn yellow then brown",
            "Severe infection stunts plant; reduces grain filling",
        ],
        "conditions":   "Cool, dry days with high humidity nights; no free water needed for spores",
        "management": [
            "Spray Hexaconazole 5 EC @ 1 ml/litre at first sign",
            "Sulphur dust (20 kg/ha) is an effective, cheap option",
            "Grow resistant wheat varieties (HD 2967, GW 496)",
            "Avoid excessive nitrogen which promotes tender growth",
        ],
        "economic_loss": "10–40% loss in susceptible varieties",
        "scouting_tip":  "Start monitoring from tillering stage in wheat",
    },
    "stem_borer": {
        "type":         "Insect pest",
        "pathogen":     "Chilo suppressalis / Scirpophaga incertulas",
        "affects":      ["paddy", "rice", "maize"],
        "symptoms": [
            "Dead heart — central shoot dies at vegetative stage",
            "White ear — panicle is empty and white at reproductive stage",
            "Circular holes at stem base with frass",
        ],
        "conditions":   "Peak activity at 15–30 DAS and at panicle initiation",
        "management": [
            "Apply Carbofuran 3G @ 10 kg/ha at 15 and 40 DAS",
            "Release Trichogramma japanicum egg parasitoids (1 lakh/acre)",
            "Remove and destroy stubble after harvest to break pest cycle",
            "Avoid high nitrogen which makes plants attractive to borers",
        ],
        "economic_loss": "15–50% loss in paddy if both dead heart and white ear occur",
        "scouting_tip":  "Pull test — dead heart shoots come out easily with distinct smell",
    },
    "leaf_curl": {
        "type":         "Viral disease",
        "pathogen":     "Cotton Leaf Curl Virus (CLCuV) via whitefly",
        "affects":      ["cotton"],
        "symptoms": [
            "Leaves curl upward (cup-shaped) with vein thickening",
            "Leaf enations (outgrowths) on underside",
            "Stunted growth; bract thickening on bolls",
        ],
        "conditions":   "Transmitted by Bemisia tabaci whitefly; spreads rapidly in hot weather",
        "management": [
            "Grow CLCuV-resistant varieties (MNH-786, VH-289)",
            "Spray Thiamethoxam 25 WG @ 0.5 g/litre for whitefly control",
            "Remove diseased plants within 45 DAS to limit spread",
            "Maintain field hygiene — remove weed hosts",
        ],
        "economic_loss": "Complete crop failure in severe cases",
        "scouting_tip":  "Monitor field borders first — whitefly enters from edges",
    },
}

# ── Symptom keywords → disease mapping for fuzzy identification ───────────────
SYMPTOM_KEYWORDS = {
    "yellow leaves": ["yellow_mosaic", "blast"],
    "white powder":  ["powdery_mildew"],
    "holes in boll": ["boll_worm"],
    "holes in maize": ["fall_armyworm"],
    "dead shoot":    ["stem_borer"],
    "frass":         ["stem_borer", "fall_armyworm", "boll_worm"],
    "curl":          ["leaf_curl", "yellow_mosaic"],
    "lesion":        ["blast", "powdery_mildew"],
    "mosaic":        ["yellow_mosaic"],
    "neck rot":      ["blast"],
    "bollworm":      ["boll_worm"],
    "armyworm":      ["fall_armyworm"],
}


def identify_pest_or_disease(
    crop: str,
    symptoms: str,
    location: str = "Telangana",
) -> dict:
    """
    Identify the most likely pest or disease from crop and symptom description.

    Args:
        crop:     Affected crop name (e.g. "cotton", "paddy", "maize").
        symptoms: Free-text description of what the farmer observes.
        location: Farming location for regional context.

    Returns:
        Dict with identified threats, confidence level, management steps,
        and economic risk assessment.
    """
    crop_lower     = crop.lower().strip()
    symptoms_lower = symptoms.lower().strip()

    # ── Step 1: Find candidates that affect this crop ─────────────────────────
    crop_candidates = {
        name: info
        for name, info in PEST_DISEASE_DB.items()
        if crop_lower in info["affects"]
    }

    # ── Step 2: Score by symptom keyword matches ──────────────────────────────
    scored = []
    for name, info in crop_candidates.items():
        score = 0
        # Match symptom keywords
        for keyword, associated_diseases in SYMPTOM_KEYWORDS.items():
            if keyword in symptoms_lower and name in associated_diseases:
                score += 2
        # Match symptom descriptions
        for symptom_text in info["symptoms"]:
            for word in symptom_text.lower().split():
                if len(word) > 4 and word in symptoms_lower:
                    score += 1
        if score > 0:
            scored.append((score, name, info))

    scored.sort(reverse=True)

    if not scored:
        return {
            "status":     "No match found",
            "message":    (
                f"No known pest/disease matched your description for {crop.title()}. "
                f"Try describing the affected plant part (leaf/stem/boll), "
                f"the colour change, and any insects you see."
            ),
            "suggestion": "Contact your local Krishi Vigyan Kendra (KVK) for in-person diagnosis.",
        }

    # ── Step 3: Return top match with full details ────────────────────────────
    top_score, top_name, top_info = scored[0]
    confidence = "High" if top_score >= 4 else ("Medium" if top_score >= 2 else "Low")

    also_consider = [
        {"name": n.replace("_", " ").title(), "type": i["type"]}
        for _, n, i in scored[1:3]
    ]

    return {
        "identified_threat":   top_name.replace("_", " ").title(),
        "confidence":          confidence,
        "type":                top_info["type"],
        "pathogen":            top_info["pathogen"],
        "matching_symptoms":   top_info["symptoms"],
        "why_now":             top_info["conditions"],
        "management_steps":    top_info["management"],
        "economic_risk":       top_info["economic_loss"],
        "scouting_tip":        top_info["scouting_tip"],
        "also_consider":       also_consider,
        "location_context":    f"Common in {location} during this season.",
        "source":              "ICAR / NCIPM Integrated Pest Management guidelines",
    }
