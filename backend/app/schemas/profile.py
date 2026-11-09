
from typing import Literal

from pydantic import BaseModel, Field, ConfigDict


class StrictSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Education(StrictSchema):
    degree: str = ""
    institution: str = ""
    location: str = ""
    start_year: str = ""
    end_year: str = ""
    status: str = ""


class Experience(StrictSchema):
    role: str = ""
    company: str = ""
    start_date: str = ""
    end_date: str = ""
    responsibilities: list[str] = Field(default_factory=list)


class Project(StrictSchema):
    name: str
    description: str = ""
    technologies: list[str] = Field(default_factory=list)
    status: Literal[
        "completed",
        "in_progress",
        "prototype",
        "unknown",
    ] = "unknown"
    achievements: list[str] = Field(default_factory=list)
    github_url: str = ""
    demo_url: str = ""


class Certification(StrictSchema):
    name: str
    issuer: str = ""
    date: str = ""


class CandidateProfile(StrictSchema):
    full_name: str = ""
    location: str = ""
    email: str = ""
    phone: str = ""
    github: str = ""
    linkedin: str = ""

    professional_summary: str = ""

    skills: list[str] = Field(default_factory=list)

    education: list[Education] = Field(default_factory=list)
    experience: list[Experience] = Field(default_factory=list)
    projects: list[Project] = Field(default_factory=list)
    certifications: list[Certification] = Field(default_factory=list)
