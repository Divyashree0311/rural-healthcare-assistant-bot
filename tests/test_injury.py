from core.question_engine import load_questions
from core.inference_engine import infer_condition
from tests.conftest import get_answers

def test_injury_heat_exhaustion():
    questions = load_questions("injury")
    answers = get_answers(questions, ["I7"])

    condition, _ = infer_condition(questions, answers)
    assert condition == "heat_exhaustion"
