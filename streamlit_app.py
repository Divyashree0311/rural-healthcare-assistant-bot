import streamlit as st
import pyttsx3

from core.question_engine import load_questions
from core.inference_engine import infer_condition
from core.advice_engine import get_advice
from db.mongo import save_session

# ---------------- SAFE TTS ----------------
def speak(text):
    engine = pyttsx3.init()
    engine.setProperty("rate", 160)
    engine.say(text)
    engine.runAndWait()
    engine.stop()

# ---------------------------------
# Language labels (SMS)
# ---------------------------------
LANG_LABELS = {
    "en": "English",
    "hi": "हिन्दी",
    "te": "తెలుగు"
}

# ---------------------------------
# SMS short summaries
# ---------------------------------
def sms_summary(condition, lang):
    summaries = {
        "NEUROTOXIC": {
            "en": "EMERGENCY: Neurotoxic snake bite.\nKeep patient still.\nDo NOT cut or tie.\nGo to hospital immediately.",
            "hi": "आपात स्थिति: न्यूरोटॉक्सिक सांप का काटना.\nमरीज को शांत रखें.\nकाटें या बांधें नहीं.\nतुरंत अस्पताल जाएं.",
            "te": "అత్యవసరం: న్యూరోటాక్సిక్ పాము కాటు.\nబాధితుడిని నిశ్చలంగా ఉంచండి.\nకాటు చేయకండి.\nవెంటనే ఆసుపత్రికి తీసుకెళ్లండి."
        }
    }
    return summaries.get(condition, {}).get(lang, "Please consult a doctor.")

# ---------------------------------
# SMS SIMULATION
# ---------------------------------
def sms_simulation():
    st.subheader("📩 SMS Simulation (3 Languages)")

    phone = st.text_input("Phone Number (Simulated)")
    name = st.text_input("Name")
    age = st.number_input("Age", min_value=1, max_value=100)

    lang = st.selectbox(
        "Select Language",
        ["en", "hi", "te"],
        format_func=lambda x: LANG_LABELS[x]
    )

    category = st.selectbox(
        "Category",
        ["snake", "newborn", "women", "injury", "rural_health"]
    )

    if st.button("Start SMS Session"):
        st.session_state.sms_started = True

    if st.session_state.get("sms_started"):
        questions = load_questions(category)
        answers = {}

        st.markdown("### Reply (1 = YES, 0 = NO)")

        for q in questions:
            q_text = q.get(f"question_{lang}", q["question_en"])
            answers[q["question_id"]] = st.radio(
                q_text,
                [0, 1],
                horizontal=True,
                key="sms_" + q["question_id"]
            )

        if st.button("Submit SMS"):
            condition, confidence = infer_condition(questions, answers)

            if condition:
                advice, severity = get_advice(category, condition, lang)
                short_msg = sms_summary(condition, lang)

                st.success(f"Condition: {condition}")
                st.text(short_msg)

                save_session(
                    phone_number=phone,
                    name=name,
                    age=age,
                    category=category,
                    answers=answers,
                    predicted_condition=condition,
                    confidence=confidence,
                    severity=severity,
                    language=lang,
                    advice=short_msg
                )

# ---------------------------------
# CALL / IVR SIMULATION (KEYPAD STYLE)
# ---------------------------------
def call_simulation():
    st.subheader("📞 Call / IVR Simulation (Voice + Keypad)")

    if "call_step" not in st.session_state:
        st.session_state.call_step = 0
        st.session_state.answers = {}
        st.session_state.q_index = 0

    phone = st.text_input("Caller Phone Number (Simulated)")
    name = st.text_input("Caller Name")
    age = st.number_input("Caller Age", min_value=1, max_value=100)

    category_map = {
        1: "snake",
        2: "newborn",
        3: "women",
        4: "injury",
        5: "rural_health"
    }

    if st.session_state.call_step == 0:
        if st.button("📞 Start Call"):
            speak("Welcome to Rural Health AI Assistant.")
            speak("Press 1 for Snake Bite. 2 for Newborn. 3 for Women. 4 for Injury. 5 for Rural Diseases.")
            st.session_state.call_step = 1
            st.rerun()

    elif st.session_state.call_step == 1:
        choice = st.radio(
            "Press number for category",
            [1, 2, 3, 4, 5],
            horizontal=True
        )
        if st.button("Confirm Category"):
            st.session_state.category = category_map[choice]
            st.session_state.questions = load_questions(st.session_state.category)
            st.session_state.call_step = 2
            st.rerun()

    elif st.session_state.call_step == 2:
        q = st.session_state.questions[st.session_state.q_index]
        speak(q["question_en"])
        st.info(f"Bot: {q['question_en']}")

        ans = st.radio("Press 1 = YES, 0 = NO", [1, 0], horizontal=True)

        if st.button("Submit"):
            st.session_state.answers[q["question_id"]] = ans
            st.session_state.q_index += 1

            if st.session_state.q_index >= len(st.session_state.questions):
                st.session_state.call_step = 3
            st.rerun()

    elif st.session_state.call_step == 3:
        condition, confidence = infer_condition(
            st.session_state.questions,
            st.session_state.answers
        )

        if condition:
            advice, severity = get_advice(st.session_state.category, condition, "en")
            speak(f"Detected condition {condition}. {advice}")

            st.success(f"Condition: {condition}")
            st.write(advice)

            save_session(
                phone_number=phone,
                name=name,
                age=age,
                category=st.session_state.category,
                answers=st.session_state.answers,
                predicted_condition=condition,
                confidence=confidence,
                severity=severity,
                language="en",
                advice=advice
            )

        if st.button("📴 End Call"):
            st.session_state.clear()
            st.rerun()

# ---------------------------------
# MAIN UI
# ---------------------------------
st.title("Rural Health AI Assistant")

tab1, tab2 = st.tabs(["📩 SMS Simulation", "📞 Call Simulation"])

with tab1:
    sms_simulation()

with tab2:
    call_simulation()
