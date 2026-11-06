from typing import List, Optional

from pydantic import BaseModel, Field


class JobSkill(BaseModel):

    skill: str

    importance: float = 1.0

    required: bool = True

    minimum_years: Optional[float] = None


class JobProfile(BaseModel):

    title: Optional[str] = None

    required_skills: List[JobSkill] = Field(
        default_factory=list
    )

    preferred_skills: List[JobSkill] = Field(
        default_factory=list
    )

    minimum_experience_years: Optional[float] = None

    responsibilities: List[str] = Field(
        default_factory=list
    )