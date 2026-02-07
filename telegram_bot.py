from telegram import Update
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    CallbackContext,
)

from core.question_engine import load_questions
from core.inference_engine import infer_condition
from core.advice_engine import get_advice
from db.mongo import save_session

# ---------------------------------
# BOT TOKEN (paste yours)
# ---------------------------------
BOT_TOKEN = "8241628974:AAG3WWPy_XetMZUXiDpe3hkM6Jfy4VfpZOU"

# ---------------------------------
# Start command
# ---------------------------------
def start(update: Update, context: CallbackContext):
    context.user_data.clear()

    update.message.reply_text(
        "Welcome to Rural Health AI Assistant 🤖\n\n"
        "Please enter your name:"
    )
    context.user_data["step"] = "name"

# ---------------------------------
# Handle messages
# ---------------------------------
def handle_message(update: Update, context: CallbackContext):
    text = update.message.text.strip()
    step = context.user_data.get("step")

    # -------- NAME --------
    if step == "name":
        context.user_data["name"] = text
        context.user_data["step"] = "age"
        update.message.reply_text("Enter your age:")
        return

    # -------- AGE --------
    if step == "age":
        if not text.isdigit():
            update.message.reply_text("Please enter a valid age.")
            return

        context.user_data["age"] = int(text)
        context.user_data["step"] = "category"

        update.message.reply_text(
            "Select category:\n"
            "1. Snake Bite\n"
            "2. Newborn Health\n"
            "3. Women Health\n"
            "4. Injury\n"
            "5. Rural Diseases\n\n"
            "Reply with number (1–5)"
        )
        return

    # -------- CATEGORY --------
    if step == "category":
        cat_map = {
            "1": "snake",
            "2": "newborn",
            "3": "women",
            "4": "injury",
            "5": "rural_health"
        }

        if text not in cat_map:
            update.message.reply_text("Please reply with a number from 1 to 5.")
            return

        category = cat_map[text]
        context.user_data["category"] = category
        context.user_data["questions"] = load_questions(category)
        context.user_data["answers"] = {}
        context.user_data["q_index"] = 0
        context.user_data["step"] = "questions"

        ask_next_question(update, context)
        return

    # -------- QUESTIONS --------
    if step == "questions":
        if text not in ["0", "1"]:
            update.message.reply_text("Reply with 1 = YES or 0 = NO.")
            return

        questions = context.user_data["questions"]
        q_index = context.user_data["q_index"]

        q = questions[q_index]
        context.user_data["answers"][q["question_id"]] = int(text)
        context.user_data["q_index"] += 1

        if context.user_data["q_index"] >= len(questions):
            finish(update, context)
        else:
            ask_next_question(update, context)
        return

# ---------------------------------
# Ask question
# ---------------------------------
def ask_next_question(update, context):
    q_index = context.user_data["q_index"]
    q = context.user_data["questions"][q_index]

    update.message.reply_text(
        f"{q['question_en']}\n"
        "Reply: 1 = YES, 0 = NO"
    )

# ---------------------------------
# Finish & result
# ---------------------------------
def finish(update, context):
    questions = context.user_data["questions"]
    answers = context.user_data["answers"]

    condition, confidence = infer_condition(questions, answers)

    if condition:
        advice, severity = get_advice(
            context.user_data["category"],
            condition,
            "en"
        )

        update.message.reply_text(
            f"🩺 Detected Condition: {condition}\n"
            f"⚠ Severity: {severity.upper()}\n\n"
            f"{advice}"
        )

        save_session(
            phone_number=str(update.message.from_user.id),
            name=context.user_data["name"],
            age=context.user_data["age"],
            category=context.user_data["category"],
            answers=answers,
            predicted_condition=condition,
            confidence=confidence,
            severity=severity,
            language="en",
            advice=advice
        )
    else:
        update.message.reply_text(
            "Unable to detect condition.\n"
            "Please visit nearest hospital."
        )

    context.user_data.clear()

# ---------------------------------
# MAIN
# ---------------------------------
def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    updater.start_polling()
    print("Telegram bot started...")
    updater.idle()

if __name__ == "__main__":
    main()
