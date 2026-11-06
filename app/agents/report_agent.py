from langchain_google_genai import (
    ChatGoogleGenerativeAI
)

from app.config import settings


llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.2,
    google_api_key=settings.GEMINI_API_KEY
)


def generate_final_report(
    role: str,
    candidate_profile: dict,
    alignment: dict,
    transcript: list,
    final_score: float,
    recommendation: str
) -> str:

    prompt = f"""
You are a senior technical interviewer.

Generate a professional final interview
evaluation report.

ROLE:
{role}

CANDIDATE PROFILE:
{candidate_profile}

JOB ALIGNMENT:
{alignment}

INTERVIEW TRANSCRIPT:
{transcript}

FINAL SCORE:
{final_score}/10

RECOMMENDATION:
{recommendation}

Generate the report with:

1. Executive Summary

2. JD Skill Alignment

3. Technical Performance

4. Problem Solving

5. Communication

6. Strengths

7. Knowledge Gaps

8. Areas for Improvement

9. Interview Evidence

10. Final Recommendation

Important:

- Base all conclusions on the evidence.
- Do not invent candidate information.
- Do not infer protected characteristics.
- Clearly distinguish demonstrated skills
  from skills that were not tested.
"""

    response = llm.invoke(
        prompt
    )

    return response.content.strip()