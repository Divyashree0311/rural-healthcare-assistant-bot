import pickle
import numpy as np
from pathlib import Path

# -------------------------------------------------
# Load trained ML model safely
# -------------------------------------------------
MODEL_PATH = Path("ml/models/snake.pkl")

if not MODEL_PATH.exists():
    raise FileNotFoundError(
        "ML model not found. Please train the model before running predictions."
    )

with open(MODEL_PATH, "rb") as f:
    model = pickle.load(f)


def ml_predict(answers: dict):
    """
    Predicts health condition using trained ML model.

    Parameters:
        answers (dict): Symptom answers {question_id: 0/1}

    Returns:
        condition (str): Predicted condition label
        confidence (float): Prediction confidence (0 to 1)
    """

    # Convert answers dict to ordered feature vector
    feature_vector = list(answers.values())

    # ML model expects fixed number of features
    expected_features = model.n_features_in_

    # Pad missing features with 0 (safe default)
    if len(feature_vector) < expected_features:
        feature_vector.extend(
            [0] * (expected_features - len(feature_vector))
        )

    # Trim extra features if any (extra safety)
    feature_vector = feature_vector[:expected_features]

    # Convert to numpy array
    X = np.array(feature_vector).reshape(1, -1)

    # Predict probabilities
    probabilities = model.predict_proba(X)[0]
    max_index = probabilities.argmax()

    predicted_condition = model.classes_[max_index]
    confidence = float(probabilities[max_index])

    return predicted_condition, confidence
