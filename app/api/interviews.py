import json
from datetime import datetime

from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

from sqlalchemy.orm import Session

from app.config import settings

from app.db.database import get_db

from app.models.candidate import Candidate
from app.models.job import Job
from app.models.interview import Interview
from app.models.answer import InterviewAnswer

from app.schemas.interview import (
    StartInterviewRequest,
    SubmitAnswerRequest
)

from app.agents.interview_agent import (
    generate_question,
    generate_follow_up
)

from app.agents.evaluation_agent import (
    evaluate_answer
)

from app.agents.report_agent import (
    generate_final_report
)

from app.services.scoring_service import (
    calculate_final_score,
    get_recommendation
)

from app.workflows.interview_graph import (
    decide_next_action
)


router = APIRouter()


def get_interview_or_404(
    interview_id: int,
    db: Session
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

    return interview


def select_next_skill(
    interview: Interview,
    candidate: Candidate,
    job: Job,
    db: Session
) -> str:

    candidate_profile = json.loads(
        candidate.profile_json
    )

    job_profile = json.loads(
        job.profile_json
    )

    tested_skills = {
        answer.skill
        for answer in (
            db.query(
                InterviewAnswer
            )
            .filter(
                InterviewAnswer.interview_id
                == interview.id
            )
            .all()
        )
    }

    required_skills = [
        item["skill"]
        for item in job_profile.get(
            "required_skills",
            []
        )
    ]

    preferred_skills = [
        item["skill"]
        for item in job_profile.get(
            "preferred_skills",
            []
        )
    ]

    all_skills = (
        required_skills
        + preferred_skills
    )

    for skill in all_skills:

        if skill not in tested_skills:
            return skill

    candidate_skills = [
        item["skill"]
        for item in candidate_profile.get(
            "skills",
            []
        )
    ]

    for skill in candidate_skills:

        if skill not in tested_skills:
            return skill

    return (
        all_skills[0]
        if all_skills
        else "General Technical Knowledge"
    )


def get_previous_questions(
    interview_id: int,
    db: Session
):

    answers = (
        db.query(
            InterviewAnswer
        )
        .filter(
            InterviewAnswer.interview_id
            == interview_id
        )
        .order_by(
            InterviewAnswer.question_number
        )
        .all()
    )

    return [
        answer.question
        for answer in answers
    ]


def get_previous_answers(
    interview_id: int,
    db: Session
):

    answers = (
        db.query(
            InterviewAnswer
        )
        .filter(
            InterviewAnswer.interview_id
            == interview_id
        )
        .order_by(
            InterviewAnswer.question_number
        )
        .all()
    )

    return [
        answer.answer
        for answer in answers
    ]


@router.post(
    "/start"
)
def start_interview(
    request: StartInterviewRequest,
    db: Session = Depends(get_db)
):

    candidate = (
        db.query(Candidate)
        .filter(
            Candidate.id
            == request.candidate_id
        )
        .first()
    )

    if not candidate:

        raise HTTPException(
            status_code=404,
            detail="Candidate not found."
        )

    job = (
        db.query(Job)
        .filter(
            Job.id == request.job_id
        )
        .first()
    )

    if not job:

        raise HTTPException(
            status_code=404,
            detail="Job not found."
        )

    candidate_profile = json.loads(
        candidate.profile_json
    )

    job_profile = json.loads(
        job.profile_json
    )

    # Recalculate alignment for safety.
    from app.schemas.candidate import (
        CandidateProfile
    )

    from app.schemas.job import (
        JobProfile
    )

    candidate_obj = (
        CandidateProfile.model_validate(
            candidate_profile
        )
    )

    job_obj = (
        JobProfile.model_validate(
            job_profile
        )
    )

    from app.services.alignment_engine import (
        calculate_alignment
    )

    alignment = calculate_alignment(
        candidate_obj,
        job_obj
    )

    eligible = (
        alignment[
            "weighted_alignment"
        ]
        >= settings.ALIGNMENT_THRESHOLD
        and not alignment[
            "critical_skills_missing"
        ]
    )

    if not eligible:

        raise HTTPException(
            status_code=403,
            detail={
                "message":
                    "Candidate is not "
                    "eligible for interview.",
                "alignment":
                    alignment
            }
        )

    interview = Interview(
        candidate_id=candidate.id,
        job_id=job.id,
        role=job_profile.get(
            "title",
            "Technical Role"
        ),
        status="active",
        alignment_score=alignment[
            "weighted_alignment"
        ],
        question_count=0
    )

    db.add(interview)

    db.commit()

    db.refresh(interview)

    first_skill = select_next_skill(
        interview,
        candidate,
        job,
        db
    )

    question = generate_question(
        role=interview.role,
        skill=first_skill,
        difficulty="medium",
        candidate_profile=candidate_profile,
        job_profile=job_profile,
        previous_questions=[],
        previous_answers=[]
    )

    first_record = InterviewAnswer(
        interview_id=interview.id,
        question_number=1,
        skill=first_skill,
        difficulty="medium",
        question_type="technical",
        question=question,
        answer="",
        is_follow_up=False
    )

    db.add(first_record)

    interview.question_count = 1

    db.commit()

    return {
        "interview_id": interview.id,
        "question_number": 1,
        "question": question,
        "skill": first_skill,
        "difficulty": "medium",
        "question_type": "technical",
        "is_follow_up": False,
        "message": "Interview started."
    }


@router.post(
    "/{interview_id}/answer"
)
def submit_answer(
    interview_id: int,
    request: SubmitAnswerRequest,
    db: Session = Depends(get_db)
):

    interview = get_interview_or_404(
        interview_id,
        db
    )

    if interview.status != "active":

        raise HTTPException(
            status_code=400,
            detail="Interview is not active."
        )

    if not request.answer.strip():

        raise HTTPException(
            status_code=400,
            detail="Answer cannot be empty."
        )

    current_question = (
        db.query(InterviewAnswer)
        .filter(
            InterviewAnswer.interview_id
            == interview_id
        )
        .order_by(
            InterviewAnswer.question_number.desc()
        )
        .first()
    )

    if not current_question:

        raise HTTPException(
            status_code=400,
            detail=(
                "No question is currently "
                "waiting for an answer."
            )
        )

    if current_question.answer:

        raise HTTPException(
            status_code=400,
            detail=(
                "This question has already "
                "been answered."
            )
        )

    candidate = (
        db.query(Candidate)
        .filter(
            Candidate.id
            == interview.candidate_id
        )
        .first()
    )

    job = (
        db.query(Job)
        .filter(
            Job.id == interview.job_id
        )
        .first()
    )

    candidate_profile = json.loads(
        candidate.profile_json
    )

    job_profile = json.loads(
        job.profile_json
    )

    evaluation = evaluate_answer(
        role=interview.role,
        skill=current_question.skill,
        question=current_question.question,
        answer=request.answer
    )

    current_question.answer = (
        request.answer
    )

    current_question.correctness = (
        evaluation.correctness
    )

    current_question.technical_depth = (
        evaluation.technical_depth
    )

    current_question.problem_solving = (
        evaluation.problem_solving
    )

    current_question.communication = (
        evaluation.communication
    )

    current_question.overall_score = (
        evaluation.overall_score
    )

    current_question.strengths = json.dumps(
        evaluation.strengths
    )

    current_question.gaps = json.dumps(
        evaluation.gaps
    )

    current_question.feedback = (
        evaluation.feedback
    )

    current_question.follow_up_required = (
        evaluation.follow_up_required
    )

    current_question.follow_up_reason = (
        evaluation.follow_up_reason
    )

    db.commit()

    state = {
        "interview_id": interview.id,
        "role": interview.role,
        "current_skill":
            current_question.skill,
        "current_difficulty":
            current_question.difficulty,
        "current_question":
            current_question.question,
        "current_answer":
            request.answer,
        "question_number":
            current_question.question_number,
        "is_follow_up":
            current_question.is_follow_up,
        "followups_for_current_question": 0,
        "interview_complete": False,
        "evaluation":
            evaluation.model_dump()
    }

    action = decide_next_action(
        state
    )

    # Follow-up question.
    if (
        action == "follow_up"
        and not current_question.is_follow_up
    ):

        follow_up_question = (
            generate_follow_up(
                role=interview.role,
                skill=current_question.skill,
                original_question=
                    current_question.question,
                candidate_answer=
                    request.answer,
                follow_up_reason=
                    evaluation.follow_up_reason
            )
        )

        next_number = (
            interview.question_count + 1
        )

        follow_up_record = InterviewAnswer(
            interview_id=interview.id,
            question_number=next_number,
            skill=current_question.skill,
            difficulty=current_question.difficulty,
            question_type="follow_up",
            question=follow_up_question,
            answer="",
            is_follow_up=True
        )

        db.add(follow_up_record)

        interview.question_count = (
            next_number
        )

        db.commit()

        return {
            "interview_id":
                interview.id,

            "question_number":
                next_number,

            "question":
                follow_up_question,

            "skill":
                current_question.skill,

            "difficulty":
                current_question.difficulty,

            "question_type":
                "follow_up",

            "is_follow_up":
                True,

            "evaluation":
                evaluation.model_dump(),

            "interview_complete":
                False
        }

    # Check minimum five-question requirement.
    answered_questions = (
        db.query(InterviewAnswer)
        .filter(
            InterviewAnswer.interview_id
            == interview.id,
            InterviewAnswer.answer != ""
        )
        .count()
    )

    if (
        answered_questions
        >= settings.MIN_INTERVIEW_QUESTIONS
    ):

        if (
            answered_questions
            >= settings.MAX_INTERVIEW_QUESTIONS
        ):

            return complete_interview(
                interview,
                candidate,
                job,
                db
            )

    # Continue with next skill.
    next_skill = select_next_skill(
        interview,
        candidate,
        job,
        db
    )

    previous_questions = (
        get_previous_questions(
            interview.id,
            db
        )
    )

    previous_answers = (
        get_previous_answers(
            interview.id,
            db
        )
    )

    next_difficulty = "medium"

    if evaluation.overall_score >= 8.5:
        next_difficulty = "hard"

    elif evaluation.overall_score <= 5:
        next_difficulty = "easy"

    else:
        next_difficulty = "medium"

    next_question = generate_question(
        role=interview.role,
        skill=next_skill,
        difficulty=next_difficulty,
        candidate_profile=candidate_profile,
        job_profile=job_profile,
        previous_questions=
            previous_questions,
        previous_answers=
            previous_answers
    )

    next_number = (
        interview.question_count + 1
    )

    next_record = InterviewAnswer(
        interview_id=interview.id,
        question_number=next_number,
        skill=next_skill,
        difficulty=next_difficulty,
        question_type="technical",
        question=next_question,
        answer="",
        is_follow_up=False
    )

    db.add(next_record)

    interview.question_count = (
        next_number
    )

    db.commit()

    return {
        "interview_id":
            interview.id,

        "question_number":
            next_number,

        "question":
            next_question,

        "skill":
            next_skill,

        "difficulty":
            next_difficulty,

        "question_type":
            "technical",

        "is_follow_up":
            False,

        "evaluation":
            evaluation.model_dump(),

        "interview_complete":
            False
    }


def complete_interview(
    interview,
    candidate,
    job,
    db
):

    answers = (
        db.query(
            InterviewAnswer
        )
        .filter(
            InterviewAnswer.interview_id
            == interview.id,
            InterviewAnswer.answer != ""
        )
        .order_by(
            InterviewAnswer.question_number
        )
        .all()
    )

    evaluations = []

    transcript = []

    for answer in answers:

        evaluation = {
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
                answer.feedback
        }

        evaluations.append(
            {
                "overall_score":
                    answer.overall_score
            }
        )

        transcript.append(
            evaluation
        )

    final_score = calculate_final_score(
        evaluations
    )

    recommendation = get_recommendation(
        final_score
    )

    candidate_profile = json.loads(
        candidate.profile_json
    )

    job_profile = json.loads(
        job.profile_json
    )

    alignment = {
        "alignment_score":
            interview.alignment_score
    }

    report = generate_final_report(
        role=interview.role,
        candidate_profile=
            candidate_profile,
        alignment=alignment,
        transcript=transcript,
        final_score=final_score,
        recommendation=recommendation
    )

    interview.status = "completed"

    interview.final_score = final_score

    interview.recommendation = (
        recommendation
    )

    interview.final_report = report

    interview.completed_at = datetime.utcnow()

    db.commit()

    return {
        "interview_id":
            interview.id,

        "status":
            "completed",

        "questions_answered":
            len(answers),

        "final_score":
            final_score,

        "recommendation":
            recommendation,

        "transcript":
            transcript,

        "final_report":
            report
    }