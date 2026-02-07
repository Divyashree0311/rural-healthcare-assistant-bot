from core.question_engine import load_questions
from core.inference_engine import infer_condition
from tests.conftest import get_answers

def test_rural_diarrhea():
    questions = load_questions("rural_health")
    answers = get_answers(questions, ["R2"])

    condition, _ = infer_condition(questions, answers)
    assert condition == "diarrhea"

def test_rural_fallback():
    questions = load_questions("rural_health")
    answers = get_answers(questions, [])

    condition, _ = infer_condition(questions, answers)
    assert condition is None
