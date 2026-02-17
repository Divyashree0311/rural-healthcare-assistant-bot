from pathlib import Path
import pickle
import pandas as pd
import pyttsx3
import speech_recognition as sr

from core.question_engine import load_questions
from core.inference_engine import infer_condition
from core.advice_engine import get_advice
from core.fallback import fallback_message
from db.mongo import save_session


# =====================================================
# VOICE ENGINE
# =====================================================
engine = pyttsx3.init()
engine.setProperty("rate", 160)


def speak(text):
    print(text)
    engine.say(text)
    engine.runAndWait()


# =====================================================
# VOICE INPUT (YES / NO)
# =====================================================
def listen_yes_no():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        audio = r.listen(source)

    try:
        text = r.recognize_google(audio).lower()
        print("You said:", text)

        if "yes" in text:
            return 1
        elif "no" in text:
            return 0
    except:
        pass

    speak("Please say Yes or No.")
    return listen_yes_no()


# =====================================================
# KEYBOARD INPUT (YES / NO)
# =====================================================
def type_yes_no():
    while True:
        user_input = input("Enter 1 = YES, 0 = NO : ").strip()
        if user_input in ["0", "1"]:
            return int(user_input)
        print("Invalid input. Please type 1 or 0.")


# =====================================================
# ML SETTINGS
# =====================================================
ML_CONFIDENCE_THRESHOLD = 0.60
MODEL_DIR = Path("ml/models")


def load_ml_model(category):
    model_path = MODEL_DIR / f"{category}.pkl"
    if model_path.exists():
        with open(model_path, "rb") as f:
            return pickle.load(f)
    return None


def ml_predict(model, answers):
    X = pd.DataFrame([list(answers.values())])
    probs = model.predict_proba(X)[0]
    classes = model.classes_
    idx = probs.argmax()
    return classes[idx], probs[idx]


# =====================================================
# MAIN PROGRAM
# =====================================================
def main():
    speak("Welcome to Rural Health AI Assistant")

    # -------- SELECT MODE --------
    print("\nSelect Interaction Mode:")
    print("1 - Voice Mode")
    print("2 - Typing Mode")

    mode = input("Enter mode number: ").strip()

    if mode == "1":
        input_method = listen_yes_no
        speak("Voice mode selected.")
    else:
        input_method = type_yes_no
        speak("Typing mode selected.")

    # -------- USER INFO --------
    name = input("Enter your name: ")
    age = int(input("Enter your age: "))

    speak("Select category. 1 Snake bite, 2 Newborn, 3 Women, 4 Injury, 5 Rural diseases.")
    choice = input("Enter choice number: ")

    cat_map = {
        "1": "snake",
        "2": "newborn",
        "3": "women",
        "4": "injury",
        "5": "rural_health"
    }

    category = cat_map.get(choice)
    if not category:
        speak("Invalid category.")
        return

    questions = load_questions(category)
    answers = {}

    speak("Answer the following questions.")

    # -------- QUESTION LOOP --------
    for q in questions:
        speak(q["question_en"])
        answers[q["question_id"]] = input_method()

    # -------- RULE ENGINE --------
    rule_condition, rule_conf = infer_condition(questions, answers)

    # -------- ML ENGINE --------
    model = load_ml_model(category)
    final_condition = rule_condition
    final_confidence = rule_conf

    if model and rule_condition:
        ml_condition, ml_conf = ml_predict(model, answers)

        if ml_conf >= ML_CONFIDENCE_THRESHOLD and ml_condition == rule_condition:
            final_condition = ml_condition
            final_confidence = ml_conf

    # -------- FALLBACK --------
    if not final_condition:
        speak(fallback_message("en"))
        return

    # -------- ADVICE --------
    advice, severity = get_advice(category, final_condition, "en")

    result_text = f"Detected condition {final_condition}. Severity {severity}. {advice}"
    speak(result_text)

    # -------- SAVE SESSION --------
    save_session(
        name=name,
        age=age,
        category=category,
        answers=answers,
        predicted_condition=final_condition,
        confidence=final_confidence,
        severity=severity,
        language="en",
        advice=advice
    )


# =====================================================
# RUN
# =====================================================
if __name__ == "__main__":
    main()
