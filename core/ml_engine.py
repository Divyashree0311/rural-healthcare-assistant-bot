import pickle
import numpy as np

with open("ml/model.pkl", "rb") as f:
    model = pickle.load(f)

def ml_predict(answers):
    vector = np.array(list(answers.values())).reshape(1, -1)
    probs = model.predict_proba(vector)[0]
    classes = model.classes_

    best_idx = probs.argmax()
    return classes[best_idx], probs[best_idx]
