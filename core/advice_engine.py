import json
from pathlib import Path

# -------------------------------------------------
# FIX: Always resolve from project root
# -------------------------------------------------
ROOT_DIR = Path(__file__).resolve().parent.parent


def get_advice(category, condition, lang="en"):
    """
    Returns (advice_text, severity)
    """

    json_path = (
        ROOT_DIR
        / "data"
        / "kb"
        / category
        / f"{category}_health_kb.json"
    )

    if not json_path.exists():
        raise FileNotFoundError(f"Advice file not found: {json_path}")

    with open(json_path, "r", encoding="utf-8") as f:
        kb = json.load(f)

    # Fallback safety
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
