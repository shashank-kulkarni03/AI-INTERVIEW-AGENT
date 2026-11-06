from langchain_google_genai import (
    ChatGoogleGenerativeAI
)

from app.config import settings


llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.5,
    google_api_key=settings.GEMINI_API_KEY
)


def generate_question(
    role: str,
    skill: str,
    difficulty: str,
    candidate_profile: dict,
    job_profile: dict,
    previous_questions: list,
    previous_answers: list
) -> str:

    prompt = f"""
You are an experienced technical interviewer.

ROLE:
{role}

SKILL:
{skill}

DIFFICULTY:
{difficulty}

CANDIDATE PROFILE:
{candidate_profile}

JOB PROFILE:
{job_profile}

PREVIOUS QUESTIONS:
{previous_questions}

PREVIOUS ANSWERS:
{previous_answers}

Generate exactly ONE interview question.

Rules:

1. It must be relevant to the role.
2. It must test the specified skill.
3. It must match the difficulty.
4. Do not repeat previous questions.
5. Prefer practical or scenario-based
   questions when appropriate.
6. Do not provide the answer.
7. Do not ask multiple questions.
8. Do not ask about protected characteristics.
9. Keep the question concise.

Return only the question.
"""

    response = llm.invoke(
        prompt
    )

    return response.content.strip()


def generate_follow_up(
    role: str,
    skill: str,
    original_question: str,
    candidate_answer: str,
    follow_up_reason: str
) -> str:

    prompt = f"""
You are conducting a technical interview.

ROLE:
{role}

SKILL:
{skill}

ORIGINAL QUESTION:
{original_question}

CANDIDATE ANSWER:
{candidate_answer}

REASON FOR FOLLOW-UP:
{follow_up_reason}

Generate exactly ONE targeted follow-up question.

The follow-up must address the weakness,
missing concept, or ambiguity identified
in the candidate's answer.

Do not repeat the original question.

Do not provide the answer.

Return only the question.
"""

    response = llm.invoke(
        prompt
    )

    return response.content.strip()