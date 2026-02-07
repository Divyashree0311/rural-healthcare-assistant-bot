import csv
from pathlib import Path

# -------------------------------------------------
# Always resolve paths from PROJECT ROOT
# -------------------------------------------------
ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data" / "kb"

def load_questions(category):
    """
    Load question rules CSV for a given category.
    Works correctly from CLI, Streamlit, Flask, Telegram.
    """

    csv_path = DATA_DIR / category / f"{category}_rules.csv"

    if not csv_path.exists():
        raise FileNotFoundError(f"Rules file not found: {csv_path}")

    questions = []

    with open(csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            questions.append({
                "question_id": row["question_id"],
                "question_en": row.get("question_en", ""),
                "question_hi": row.get("question_hi", ""),
                "question_te": row.get("question_te", ""),
                "condition_code": row["condition_code"],
                "weight": float(row["weight"])
            })

    return questions
