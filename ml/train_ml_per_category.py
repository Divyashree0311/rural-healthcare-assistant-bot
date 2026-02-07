import sys
from pathlib import Path
import pickle
import pandas as pd
from pymongo import MongoClient
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

CATEGORIES = ["snake", "newborn", "women", "injury", "rural_health"]

client = MongoClient("mongodb://localhost:27017/")
db = client["rural_health_ai"]

Path("ml/models").mkdir(exist_ok=True)

for category in CATEGORIES:
    records = list(db.sessions.find({
        "category": category,
        "predicted_condition": {"$ne": "fallback"}
    }))

    if len(records) < 20:
        print(f"Skipping {category} (not enough data)")
        continue

    X, y = [], []

    for r in records:
        X.append(list(r["answers"].values()))
        y.append(r["predicted_condition"])

    X = pd.DataFrame(X).fillna(0)
    y = pd.Series(y)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=42
    )

    model = LogisticRegression(max_iter=1000)
    model.fit(X_train, y_train)

    acc = accuracy_score(y_test, model.predict(X_test))
    print(f"{category.upper()} accuracy: {acc:.2f}")

    with open(f"ml/models/{category}.pkl", "wb") as f:
        pickle.dump(model, f)
