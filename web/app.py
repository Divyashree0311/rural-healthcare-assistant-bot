from flask import Flask, render_template, request, jsonify
import sys
from pathlib import Path

# ------------------------------
# Fix Python path (VERY IMPORTANT)
# ------------------------------
ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT))

from core.question_engine import load_questions
from core.inference_engine import infer_condition
from core.advice_engine import get_advice
from db.mongo import save_session

app = Flask(__name__)

# ------------------------------
# Home page
# ------------------------------
@app.route("/")
def index():
    return render_template("chat.html")

# ------------------------------
# Load questions
# ------------------------------
@app.route("/questions", methods=["POST"])
def questions():
    data = request.json
    category = data.get("category")
    lang = data.get("lang", "en")

    qs = load_questions(category)

    result = []
    for q in qs:
        result.append({
            "id": q["question_id"],
            "text": q.get(f"question_{lang}", q["question_en"])
        })

    return jsonify(result)

# ------------------------------
# Submit answers
# ------------------------------
@app.route("/submit", methods=["POST"])
def submit():
    data = request.json

    # SAFE INPUT (NO CRASH)
    name = data.get("name", "anonymous")
    age = int(data.get("age", 0))
    category = data.get("category")
    lang = data.get("lang", "en")
    answers = data.get("answers", {})

    questions = load_questions(category)
    condition, confidence = infer_condition(questions, answers)

    if condition:
        advice, severity = get_advice(category, condition, lang)
    else:
        condition = "fallback"
        advice = "Please consult the nearest hospital."
        severity = "unknown"

    # Save to DB (optional but safe)
    save_session(
        name=name,
        age=age,
        category=category,
        answers=answers,
        predicted_condition=condition,
        confidence=confidence,
        severity=severity,
        language=lang
    )

    return jsonify({
        "condition": condition,
        "severity": severity,
        "advice": advice
    })

if __name__ == "__main__":
    app.run(debug=True)
