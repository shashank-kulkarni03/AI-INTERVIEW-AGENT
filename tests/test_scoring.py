from app.services.scoring_service import (
    calculate_final_score,
    get_recommendation
)


def test_final_score():

    evaluations = [
        {
            "overall_score": 8
        },
        {
            "overall_score": 9
        },
        {
            "overall_score": 7
        }
    ]

    score = calculate_final_score(
        evaluations
    )

    assert score == 8


def test_recommendation():

    assert (
        get_recommendation(9)
        == "Strong Hire"
    )

    assert (
        get_recommendation(8)
        == "Hire"
    )