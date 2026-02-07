import sys
from pathlib import Path
import random

# -------------------------------------------------
# FIX: Add project root to PYTHONPATH
# -------------------------------------------------
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

# -------------------------------------------------
# Imports from project
# -------------------------------------------------
from core.question_engine import load_questions
from core.inference_engine import infer_condition
from core.advice_engine import get_advice
from db.mongo import save_session

# -------------------------------------------------
# Configuration
# -------------------------------------------------
CATEGORIES = ["snake", "newborn", "women", "injury", "rural_health"]
SESSIONS_PER_CATEGORY = 20   # increase = better ML
NOISE_PROBABILITY = 0.1      # small randomness to avoid overfitting

# -------------------------------------------------
# Rule-aware answer generator (M3)
# -------------------------------------------------
def simulate_answers_rule_aware(questions, target_condition):
    """
    Generate medically consistent answers.
    Questions related to target_condition -> Yes
    Others -> No (with small noise)
    """
    answers = {}

    for q in questions:
        qid = q["question_id"]
        q_condition = q["condition_code"]

        if q_condition == target_condition:
            answers[qid] = 1
        else:
            # small noise to avoid perfect patterns
            answers[qid] = 1 if random.random() < NOISE_PROBABILITY else 0

    return answers

# -------------------------------------------------
# Main simulation logic
# -------------------------------------------------
def simulate_sessions():
    total = 0

    for category in CATEGORIES:
        print(f"\nSimulating category: {category}")

        questions = load_questions(category)

        # collect possible conditions for this category
        condition_pool = list(
            set(q["condition_code"] for q in questions if q["condition_code"])
        )

        for i in range(SESSIONS_PER_CATEGORY):
            # choose a medically valid condition
            chosen_condition = random.choice(condition_pool)

            # generate rule-aware answers
            answers = simulate_answers_rule_aware(questions, chosen_condition)

            # infer using existing rule engine
            condition, confidence = infer_condition(questions, answers)

            if condition:
                advice, severity = get_advice(category, condition, "en")
            else:
                condition = "fallback"
                severity = "unknown"
                confidence = 0.0

            save_session(
                name=f"auto_user_{category}_{i}",
                age=random.randint(1, 70),
                category=category,
                answers=answers,
                predicted_condition=condition,
                confidence=confidence,
                severity=severity
            )

            print(f"  Saved: {category} → {condition}")
            total += 1

    print("\n----------------------------------")
    print(f"Simulation complete. Total records inserted: {total}")
    print("----------------------------------")

# -------------------------------------------------
# Entry point
# -------------------------------------------------
if __name__ == "__main__":
    simulate_sessions()
