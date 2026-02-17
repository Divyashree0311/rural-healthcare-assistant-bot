from pymongo import MongoClient
from datetime import datetime
import os
import certifi

# =====================================================
# SMART MongoDB Connection (Local + Atlas Compatible)
# =====================================================

# If environment variable exists -> use Atlas
# Otherwise fallback to local MongoDB
MONGO_URI = os.environ.get(
    "MONGO_URI",
    "mongodb://localhost:27017/"
)

# -----------------------------------------------------
# AUTO DETECT CONNECTION TYPE
# -----------------------------------------------------
try:
    if "mongodb+srv" in MONGO_URI:
        # 🌐 MongoDB Atlas (Needs TLS + Certifi)
        client = MongoClient(
            MONGO_URI,
            tls=True,
            tlsCAFile=certifi.where(),
            serverSelectionTimeoutMS=5000
        )
    else:
        # 💻 Local MongoDB (NO TLS)
        client = MongoClient(
            MONGO_URI,
            serverSelectionTimeoutMS=5000
        )

    # Test connection once
    client.admin.command("ping")
    print("✅ MongoDB Connected Successfully")

except Exception as e:
    print("❌ MongoDB Connection Failed:", e)
    client = None

# -----------------------------------------------------
# DATABASE + COLLECTION
# -----------------------------------------------------
db = client["rural_health_ai"] if client is not None else None
collection = db["sessions"] if db is not None else None



# =====================================================
# SAVE SESSION FUNCTION
# =====================================================
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
    """
    Stores user interaction session safely.
    Works for Local + Atlas DB.
    """

    if collection is None:
        print("⚠️ MongoDB not connected. Skipping save.")
        return

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

    try:
        collection.insert_one(session)
        print("💾 Session saved to MongoDB")
    except Exception as e:
        print("❌ Failed to save session:", e)
