from app.schemas.candidate import (
    CandidateProfile,
    SkillEvidence
)

from app.schemas.job import (
    JobProfile,
    JobSkill
)

from app.services.alignment_engine import (
    calculate_alignment
)


def test_alignment():

    candidate = CandidateProfile(
        name="Test Candidate",
        skills=[
            SkillEvidence(
                skill="Python"
            ),
            SkillEvidence(
                skill="AWS"
            ),
            SkillEvidence(
                skill="Postgres"
            )
        ]
    )

    job = JobProfile(
        title="Backend Developer",

        required_skills=[
            JobSkill(
                skill="Python",
                importance=0.4
            ),

            JobSkill(
                skill="AWS",
                importance=0.3
            ),

            JobSkill(
                skill="PostgreSQL",
                importance=0.3
            )
        ]
    )

    result = calculate_alignment(
        candidate,
        job
    )

    assert result[
        "weighted_alignment"
    ] == 100