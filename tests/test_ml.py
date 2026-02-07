import pytest

try:
    from core.ml_engine import ml_predict
    ML_AVAILABLE = True
except:
    ML_AVAILABLE = False


@pytest.mark.skipif(not ML_AVAILABLE, reason="ML model not trained yet")
def test_ml_prediction_output():
    """
    Basic sanity test:
    - ML should return (condition, confidence)
    - confidence should be between 0 and 1
    """

    answers = {
        "S1": 1,
        "S2": 1,
        "S3": 0,
        "S4": 0,
        "S5": 0,
        "S6": 0
    }

    condition, confidence = ml_predict(answers)

    assert isinstance(condition, str)
    assert 0.0 <= confidence <= 1.0
