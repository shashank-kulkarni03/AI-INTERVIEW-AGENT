from langchain_google_genai import (
    ChatGoogleGenerativeAI
)

from app.config import settings

from app.schemas.candidate import (
    CandidateProfile
)

from app.schemas.job import (
    JobProfile
)


candidate_llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0,
    google_api_key=settings.GEMINI_API_KEY
)

job_llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0,
    google_api_key=settings.GEMINI_API_KEY
)


candidate_extractor = (
    candidate_llm
    .with_structured_output(
        CandidateProfile
    )
)


job_extractor = (
    job_llm
    .with_structured_output(
        JobProfile
    )
)


def extract_candidate_profile(
    resume_text: str
) -> CandidateProfile:

    prompt = f"""
You are an expert technical recruiter
and resume parser.

Extract a structured candidate profile
from the resume below.

Rules:

1. Only extract information supported
   by the resume.

2. Never invent skills.

3. For each skill, provide evidence
   from the resume.

4. Estimate years of experience only
   when the resume supports the estimate.

5. Include technical and relevant
   professional skills.

RESUME:

{resume_text}
"""

    return candidate_extractor.invoke(
        prompt
    )


def extract_job_profile(
    jd_text: str
) -> JobProfile:

    prompt = f"""
You are an expert technical recruiter.

Extract a structured job profile from
the job description below.

Identify:

- job title
- required skills
- preferred skills
- relative importance
- minimum experience
- responsibilities

Importance should be a number from
0.1 to 1.0 representing how important
the skill is for this role.

Required skills should have
required=true.

Preferred skills should have
required=false.

Do not invent requirements.

JOB DESCRIPTION:

{jd_text}
"""

    return job_extractor.invoke(
        prompt
    )