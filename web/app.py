from flask import Flask, render_template, request, jsonify
import sys
import os
from pathlib import Path

# ------------------------------
# Fix Python import path
# ------------------------------
ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT))

from core.question_engine import load_questions
from core.inference_engine import infer_condition
from core.advice_engine import get_advice
from db.mongo import save_session

# ------------------------------
# Flask app
# ------------------------------
app = Flask(__name__, template_folder="templates", static_folder="static")

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
    data = request.json or {}
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
    data = request.json or {}

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
        condition = "unknown"
        advice = "Please visit the nearest hospital."
        severity = "unknown"

    # Save to MongoDB
    save_session(
        name=name,
        age=age,
        category=category,
        answers=answers,
        predicted_condition=condition,
        confidence=confidence,
        severity=severity,
        language=lang,
        advice=advice
    )

    return jsonify({
        "condition": condition,
        "confidence": confidence,
        "severity": severity,
        "advice": advice
    })

# ------------------------------
# Render entry point (IMPORTANT)
# ------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
