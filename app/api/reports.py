import json

from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

from sqlalchemy.orm import Session

from app.db.database import get_db

from app.models.interview import Interview
from app.models.answer import InterviewAnswer


router = APIRouter()


@router.get(
    "/{interview_id}"
)
def get_report(
    interview_id: int,
    db: Session = Depends(get_db)
):

    interview = (
        db.query(Interview)
        .filter(
            Interview.id == interview_id
        )
        .first()
    )

    if not interview:

        raise HTTPException(
            status_code=404,
            detail="Interview not found."
        )

    answers = (
        db.query(
            InterviewAnswer
        )
        .filter(
            InterviewAnswer.interview_id
            == interview_id,
            InterviewAnswer.answer != ""
        )
        .order_by(
            InterviewAnswer.question_number
        )
        .all()
    )

    transcript = []

    for answer in answers:

        transcript.append({

            "question_number":
                answer.question_number,

            "skill":
                answer.skill,

            "question":
                answer.question,

            "answer":
                answer.answer,

            "score":
                answer.overall_score,

            "correctness":
                answer.correctness,

            "technical_depth":
                answer.technical_depth,

            "problem_solving":
                answer.problem_solving,

            "communication":
                answer.communication,

            "strengths":
                json.loads(
                    answer.strengths
                    or "[]"
                ),

            "gaps":
                json.loads(
                    answer.gaps
                    or "[]"
                ),

            "feedback":
                answer.feedback,

            "is_follow_up":
                answer.is_follow_up
        })

    return {

        "interview_id":
            interview.id,

        "role":
            interview.role,

        "status":
            interview.status,

        "alignment_score":
            interview.alignment_score,

        "questions_answered":
            len(transcript),

        "final_score":
            interview.final_score,

        "recommendation":
            interview.recommendation,

        "transcript":
            transcript,

        "final_report":
            interview.final_report
    }