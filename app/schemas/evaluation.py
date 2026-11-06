from typing import List

from pydantic import BaseModel, Field


class AnswerEvaluation(BaseModel):

    correctness: float = Field(
        ge=0,
        le=10
    )

    technical_depth: float = Field(
        ge=0,
        le=10
    )

    problem_solving: float = Field(
        ge=0,
        le=10
    )

    communication: float = Field(
        ge=0,
        le=10
    )

    overall_score: float = Field(
        ge=0,
        le=10
    )

    strengths: List[str] = Field(
        default_factory=list
    )

    gaps: List[str] = Field(
        default_factory=list
    )

    feedback: str

    follow_up_required: bool

    follow_up_reason: str = ""

    confidence: float = Field(
        ge=0,
        le=1
    )