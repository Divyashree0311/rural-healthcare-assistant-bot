from pymongo import MongoClient
from datetime import datetime
import os
import certifi

# -------------------------------------------------
# Mongo URI (Atlas OR Local)
# -------------------------------------------------
MONGO_URI = os.environ.get(
    "MONGO_URI",
    "mongodb://localhost:27017/"   # fallback for local dev
)

# -------------------------------------------------
# IMPORTANT: TLS + Certifi fix for Atlas SSL errors
# -------------------------------------------------
client = MongoClient(
    MONGO_URI,
    tls=True,
    tlsCAFile=certifi.where()
)

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
        "timestamp": datetime.utcnow()
    }

    collection.insert_one(session)
