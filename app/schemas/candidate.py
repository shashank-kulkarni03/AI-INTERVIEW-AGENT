from typing import List, Optional

from pydantic import BaseModel, Field


class SkillEvidence(BaseModel):

    skill: str

    years: Optional[float] = None

    proficiency: Optional[str] = None

    evidence: List[str] = Field(
        default_factory=list
    )


class CandidateProfile(BaseModel):

    name: Optional[str] = None

    total_experience_years: Optional[float] = None

    skills: List[SkillEvidence] = Field(
        default_factory=list
    )

    education: List[str] = Field(
        default_factory=list
    )

    certifications: List[str] = Field(
        default_factory=list
    )

    projects: List[str] = Field(
        default_factory=list
    )