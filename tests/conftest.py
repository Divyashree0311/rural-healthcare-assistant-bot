import sys
from pathlib import Path

# Add project root to PYTHONPATH
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

from core.question_engine import load_questions

def get_answers(questions, yes_ids):
    answers = {}
    for q in questions:
        answers[q["question_id"]] = 1 if q["question_id"] in yes_ids else 0
    return answers
