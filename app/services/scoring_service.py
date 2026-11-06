def calculate_final_score(
    evaluations: list
) -> float:

    if not evaluations:
        return 0.0

    scores = [
        evaluation["overall_score"]
        for evaluation in evaluations
        if evaluation.get(
            "overall_score"
        ) is not None
    ]

    if not scores:
        return 0.0

    return round(
        sum(scores) / len(scores),
        2
    )


def get_recommendation(
    score: float
) -> str:

    if score >= 8.5:
        return "Strong Hire"

    if score >= 7.5:
        return "Hire"

    if score >= 6.0:
        return "Consider"

    if score >= 5.0:
        return "Weak Consider"

    return "No Hire"