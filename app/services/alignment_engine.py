from app.schemas.candidate import CandidateProfile
from app.schemas.job import JobProfile

from app.services.skill_normalizer import (
    normalize_skill
)


def calculate_alignment(
    candidate: CandidateProfile,
    job: JobProfile
) -> dict:

    candidate_skills = {
        normalize_skill(skill.skill)
        for skill in candidate.skills
    }

    job_skills = (
        job.required_skills
        + job.preferred_skills
    )

    if not job_skills:

        return {
            "weighted_alignment": 0.0,
            "skill_coverage": 0.0,
            "required_skill_coverage": 0.0,
            "matched_skills": [],
            "missing_skills": [],
            "critical_skills_missing": []
        }

    total_weight = sum(
        skill.importance
        for skill in job_skills
    )

    matched_weight = 0.0

    matched_skills = []

    missing_skills = []

    for job_skill in job_skills:

        normalized_job_skill = (
            normalize_skill(
                job_skill.skill
            )
        )

        if normalized_job_skill in candidate_skills:

            matched_weight += (
                job_skill.importance
            )

            matched_skills.append(
                job_skill.skill
            )

        else:

            missing_skills.append(
                job_skill.skill
            )

    weighted_alignment = (
        matched_weight
        / total_weight
    ) * 100

    required_skills = (
        job.required_skills
    )

    if required_skills:

        required_matched = sum(
            1
            for skill in required_skills
            if normalize_skill(
                skill.skill
            ) in candidate_skills
        )

        required_coverage = (
            required_matched
            / len(required_skills)
        ) * 100

    else:

        required_coverage = 100.0

    critical_missing = [
        skill.skill
        for skill in required_skills
        if skill.required
        and normalize_skill(
            skill.skill
        ) not in candidate_skills
    ]

    skill_coverage = (
        len(matched_skills)
        / len(job_skills)
    ) * 100

    return {

        "weighted_alignment": round(
            weighted_alignment,
            2
        ),

        "skill_coverage": round(
            skill_coverage,
            2
        ),

        "required_skill_coverage": round(
            required_coverage,
            2
        ),

        "matched_skills": matched_skills,

        "missing_skills": missing_skills,

        "critical_skills_missing":
            critical_missing
    }