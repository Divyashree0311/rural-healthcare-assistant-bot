from pymongo import MongoClient
from datetime import datetime

client = MongoClient("mongodb://localhost:27017/")
db = client["rural_health_ai"]
collection = db.sessions


def save_session(
    name,
    age,
    category,
    answers,
    predicted_condition,
    confidence,
    severity,
    language=None,
    phone_number=None,
    advice=None
):
    session = {
        "phone_number": phone_number,
        "name": name,
        "age": age,
        "category": category,
        "answers": answers,
        "predicted_condition": predicted_condition,
        "confidence": confidence,
        "severity": severity,
        "language": language,
        "advice": advice,
        "timestamp": datetime.now()
    }

    collection.insert_one(session)
