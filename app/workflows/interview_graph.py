from typing import TypedDict


class InterviewState(TypedDict):

    interview_id: int

    role: str

    current_skill: str

    current_difficulty: str

    current_question: str

    current_answer: str

    question_number: int

    is_follow_up: bool

    followups_for_current_question: int

    interview_complete: bool

    evaluation: dict


def decide_next_action(
    state: InterviewState
) -> str:

    evaluation = state.get(
        "evaluation",
        {}
    )

    question_number = (
        state["question_number"]
    )

    followups = (
        state[
            "followups_for_current_question"
        ]
    )

    follow_up_required = evaluation.get(
        "follow_up_required",
        False
    )

    if (
        follow_up_required
        and followups < 1
    ):
        return "follow_up"

    if question_number >= 5:
        return "next_or_finish"

    return "next_question"