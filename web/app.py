from flask import Flask, render_template, request, jsonify
import sys
from pathlib import Path
import os

# -------------------------------------------------
# FIX PYTHON PATH (VERY IMPORTANT FOR RENDER)
# -------------------------------------------------
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

# -------------------------------------------------
# Project imports
# -------------------------------------------------
from core.question_engine import load_questions
from core.inference_engine import infer_condition
from core.advice_engine import get_advice
from db.mongo import save_session

# -------------------------------------------------
# Flask app
# -------------------------------------------------
app = Flask(__name__, template_folder="templates", static_folder="static")

# -------------------------------------------------
# Home page (Website Chat UI)
# -------------------------------------------------
@app.route("/", methods=["GET"])
def index():
    return render_template("chat.html")

# -------------------------------------------------
# Load questions for selected category + language
# -------------------------------------------------
@app.route("/questions", methods=["POST"])
def questions():
    data = request.get_json(force=True)

    category = data.get("category")
    lang = data.get("lang", "en")

    if not category:
        return jsonify({"error": "Category missing"}), 400

    qs = load_questions(category)

    response = []
    for q in qs:
        response.append({
            "id": q["question_id"],
            "text": q.get(f"question_{lang}", q["question_en"])
        })

    return jsonify(response)

# -------------------------------------------------
# Submit answers and return diagnosis
# -------------------------------------------------
@app.route("/submit", methods=["POST"])
def submit():
    data = request.get_json(force=True)

    # ---- SAFE INPUTS (NO CRASHES) ----
    name = data.get("name", "anonymous")
    age = int(data.get("age", 0))
    category = data.get("category")
    lang = data.get("lang", "en")
    answers = data.get("answers", {})

    if not category or not answers:
        return jsonify({
            "condition": "fallback",
            "severity": "unknown",
            "advice": "Please consult the nearest hospital."
        })

    questions = load_questions(category)
    condition, confidence = infer_condition(questions, answers)

    if condition:
        advice, severity = get_advice(category, condition, lang)
    else:
        condition = "fallback"
        severity = "unknown"
        advice = "Please consult the nearest hospital."

    # ---- SAVE SESSION (MongoDB Atlas / Local) ----
    try:
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
    except Exception as e:
        print("DB save failed:", e)

    return jsonify({
        "condition": condition,
        "severity": severity,
        "advice": advice
    })

# -------------------------------------------------
# ENTRY POINT (RENDER + LOCAL SAFE)
# -------------------------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
