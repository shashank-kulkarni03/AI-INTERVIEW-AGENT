from typing import List

from pydantic import BaseModel, Field

from langchain_google_genai import (
    ChatGoogleGenerativeAI
)

from app.config import settings


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


llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0,
    google_api_key=settings.GEMINI_API_KEY
)


evaluator = llm.with_structured_output(
    AnswerEvaluation
)


def evaluate_answer(
    role: str,
    skill: str,
    question: str,
    answer: str
) -> AnswerEvaluation:

    prompt = f"""
You are an expert technical interviewer.

Evaluate the candidate's answer objectively.

ROLE:
{role}

SKILL:
{skill}

QUESTION:
{question}

CANDIDATE ANSWER:
{answer}

Score the answer from 0 to 10 for:

1. correctness
2. technical depth
3. problem solving
4. communication

Then calculate an overall score.

Also provide:

- strengths
- knowledge gaps
- concise feedback
- whether a follow-up is needed
- reason for follow-up
- confidence in the evaluation

Evaluation rules:

1. Evaluate only what the candidate
   actually demonstrated.

2. Do not invent experience.

3. Do not reward confident language
   without technical evidence.

4. Do not penalize accent, nationality,
   gender, or other protected characteristics.

5. Communication means clarity,
   relevance, structure, and ability
   to explain the answer.

6. A follow-up is appropriate when:
   - the answer is incomplete
   - important concepts are missing
   - the answer is vague
   - deeper understanding should be tested

Return a structured evaluation.
"""

    return evaluator.invoke(
        prompt
    )