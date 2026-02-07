from core.question_engine import load_questions
from core.inference_engine import infer_condition
from tests.conftest import get_answers

def test_newborn_fever():
    questions = load_questions("newborn")
    answers = get_answers(questions, ["N1"])

    condition, _ = infer_condition(questions, answers)
    assert condition == "neonatal_fever"

def test_newborn_fallback():
    questions = load_questions("newborn")
    answers = get_answers(questions, [])

    condition, _ = infer_condition(questions, answers)
    assert condition is None
