import sys
from pathlib import Path

# ---------------------------------------
# Fix PYTHONPATH
# ---------------------------------------
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

import pickle
import pandas as pd
from pymongo import MongoClient
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score

# ---------------------------------------
# MongoDB connection
# ---------------------------------------
client = MongoClient("mongodb://localhost:27017/")
db = client["rural_health_ai"]
collection = db.sessions

# ---------------------------------------
# Load data from MongoDB
# ---------------------------------------
records = list(collection.find({
    "predicted_condition": {"$ne": "fallback"}
}))

if len(records) < 20:
    raise ValueError("Not enough data to train ML model (need at least 20 records)")

# ---------------------------------------
# Prepare dataset
# ---------------------------------------
X = []
y = []

for rec in records:
    answers = rec["answers"]
    X.append(list(answers.values()))
    y.append(rec["predicted_condition"])

X = pd.DataFrame(X)
X = X.fillna(0)   # 🔥 THIS IS THE FIX
y = pd.Series(y)

# ---------------------------------------
# Train / test split
# ---------------------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.25, random_state=42
)

# ---------------------------------------
# Train ML model
# ---------------------------------------
model = LogisticRegression(
    max_iter=1000
)


model.fit(X_train, y_train)

# ---------------------------------------
# Evaluate model
# ---------------------------------------
y_pred = model.predict(X_test)

print("\n--- ML MODEL EVALUATION ---")
print("Accuracy:", accuracy_score(y_test, y_pred))
print("\nClassification Report:\n")
print(classification_report(y_test, y_pred))

# ---------------------------------------
# Save model
# ---------------------------------------
model_path = Path("ml/model.pkl")
with open(model_path, "wb") as f:
    pickle.dump(model, f)

print(f"\nModel saved to {model_path}")
