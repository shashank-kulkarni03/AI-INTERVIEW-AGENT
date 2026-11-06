from typing import List, Optional

from pydantic import BaseModel, Field


class StartInterviewRequest(BaseModel):

    candidate_id: int

    job_id: int


class SubmitAnswerRequest(BaseModel):

    answer: str


class InterviewQuestionResponse(BaseModel):

    interview_id: int

    question_number: int

    question: str

    skill: str

    difficulty: str

    question_type: str

    is_follow_up: bool


class InterviewStatusResponse(BaseModel):

    interview_id: int

    status: str

    question_count: int

    minimum_questions: int

    maximum_questions: int

    final_score: Optional[float] = None

    recommendation: Optional[str] = None