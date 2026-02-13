import json
from pathlib import Path

# -------------------------------------------------
# Resolve project root
# -------------------------------------------------
ROOT_DIR = Path(__file__).resolve().parent.parent

# -------------------------------------------------
# Explicit advice file mapping (IMPORTANT)
# -------------------------------------------------
ADVICE_FILES = {
    "snake": ROOT_DIR / "data/kb/snake/snake_advice_master.json",
    "newborn": ROOT_DIR / "data/kb/newborn/newborn_health_kb.json",
    "women": ROOT_DIR / "data/kb/women/women_health_kb.json",
    "injury": ROOT_DIR / "data/kb/injury/rural_injuries_advice_kb.json",
    "rural_health": ROOT_DIR / "data/kb/rural_health/rural_health_advice_kb.json",
}

def get_advice(category, condition, lang="en"):
    """
    Returns (advice_text, severity)
    """

    json_path = ADVICE_FILES.get(category)

    # Hard safety (no crash)
    if not json_path or not json_path.exists():
        return (
            {
                "en": "Please visit the nearest hospital.",
                "hi": "कृपया नजदीकी अस्पताल जाएं।",
                "te": "దయచేసి సమీప ఆసుపత్రికి వెళ్లండి."
            }.get(lang, "Please consult a doctor."),
            "unknown"
        )

    with open(json_path, "r", encoding="utf-8") as f:
        kb = json.load(f)

    # Condition fallback
    if condition not in kb:
        return (
            {
                "en": "Please visit the nearest hospital.",
                "hi": "कृपया नजदीकी अस्पताल जाएं।",
                "te": "దయచేసి సమీప ఆసుపత్రికి వెళ్లండి."
            }.get(lang, "Please consult a doctor."),
            "unknown"
        )

    entry = kb[condition]

    advice_text = entry.get(f"advice_{lang}", entry.get("advice_en"))
    severity = entry.get("severity", "unknown")

    return advice_text, severity
