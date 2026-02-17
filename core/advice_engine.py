import json
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

ADVICE_FILES = {
    "snake": ROOT_DIR / "data/kb/snake/snake_advice_master.json",
    "newborn": ROOT_DIR / "data/kb/newborn/newborn_health_kb.json",
    "women": ROOT_DIR / "data/kb/women/women_health_kb.json",
    "injury": ROOT_DIR / "data/kb/injury/injury_health_kb.json",
    "rural_health": ROOT_DIR / "data/kb/rural_health/rural_health_health_kb.json",
}



def get_advice(category, condition, lang="en"):
    json_path = ADVICE_FILES.get(category)

    print("DEBUG LOADING:", json_path)
    print("DEBUG CONDITION:", condition)

    if not json_path or not json_path.exists():
        return ("Please visit the nearest hospital.", "unknown")

    with open(json_path, "r", encoding="utf-8") as f:
        kb = json.load(f)

    # ------------------------------------------------
    # NORMALIZE STRUCTURE
    # ------------------------------------------------
    if isinstance(kb, dict):
        # Some files wrap data inside key
        kb = list(kb.values())

    # ------------------------------------------------
    # SMART MATCH
    # ------------------------------------------------
    for item in kb:

        cond_obj = item.get("condition", {})
        cond_code = cond_obj.get("code", "").lower()

        # MATCH even if minor_cut vs minor_cut_10
        if cond_code.startswith(condition.lower()):

            advice_text = (
                item.get("advice", {}).get(lang)
                or item.get("advice", {}).get("en")
                or "Please consult a doctor."
            )

            severity = item.get("severity", "unknown")

            print("DEBUG MATCH FOUND:", cond_code)

            return advice_text, severity

    print("DEBUG NO MATCH FOUND")
    return ("Please visit the nearest hospital.", "unknown")
