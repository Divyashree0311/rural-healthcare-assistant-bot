def infer_condition(questions, answers):
    """
    Rule-based weighted inference.
    Returns:
        condition_code (str or None)
        confidence (float)
    """

    scores = {}

    for q in questions:
        qid = q["question_id"]

        if answers.get(qid) == 1:
            condition = q["condition_code"]
            weight = float(q["weight"])
            scores[condition] = scores.get(condition, 0) + weight

    # No YES answers → fallback
    if not scores:
        return None, 0.0

    # Pick highest scoring condition
    best_condition = max(scores, key=scores.get)
    confidence = scores[best_condition]

    return best_condition, confidence
