from core.question_engine import load_questions
from core.inference_engine import infer_condition
from tests.conftest import get_answers

def test_women_anemia():
    questions = load_questions("women")
    answers = get_answers(questions, ["W5"])

    condition, _ = infer_condition(questions, answers)
    assert condition == "anemia"
