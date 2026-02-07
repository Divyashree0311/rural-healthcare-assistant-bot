from core.question_engine import load_questions
from core.inference_engine import infer_condition
from tests.conftest import get_answers

def test_snake_neurotoxic():
    questions = load_questions("snake")
    answers = get_answers(questions, ["S1", "S2"])

    condition, confidence = infer_condition(questions, answers)

    assert condition == "NEUROTOXIC"
    assert confidence >= 1.0

def test_snake_hemotoxic():
    questions = load_questions("snake")
    answers = get_answers(questions, ["S3", "S4"])

    condition, confidence = infer_condition(questions, answers)

    assert condition == "HEMOTOXIC"

def test_snake_fallback():
    questions = load_questions("snake")
    answers = get_answers(questions, [])

    condition, confidence = infer_condition(questions, answers)

    assert condition is None
