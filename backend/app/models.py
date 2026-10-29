from typing import Literal
from pydantic import BaseModel, Field

EvidenceStrength = Literal["mentioned", "supported_by_evidence", "demonstrated_substantial_experience"]

class ResumeSummary(BaseModel):
    profile: str
    education: list[str] = []
    experience: list[str] = []
    projects: list[str] = []
    achievements: list[str] = []
    potential_career_directions: list[str] = []

class Skill(BaseModel):
    name: str
    category: str
    evidence: str
    evidence_type: Literal["project", "internship", "coursework", "certification", "other"]
    evidence_strength: EvidenceStrength
    confidence: int = Field(ge=0, le=100)

class JobRecommendation(BaseModel):
    title: str
    description: str = ""
    match_score: int = Field(ge=0, le=100)
    match_reasons: list[str] = []
    matching_skills: list[str] = []
    skills_to_develop: list[str] = []
    readiness: str
    next_steps: list[str] = []

class SkillGap(BaseModel):
    skill: str
    target_role: str
    importance: Literal["high", "medium", "optional"]
    reason: str
    current_evidence: str = "Not demonstrated in the resume"
    development_suggestion: str

class RoadmapItem(BaseModel):
    stage: str
    topic: str
    estimated_hours: int = Field(ge=0, le=500)
    why_it_matters: str = ""
    resources: list[str] = []
    exercises: list[str] = []
    project: str = ""
    completion_criteria: str = ""

class SectionFeedback(BaseModel):
    section: str
    observations: list[str] = []

class Rewrite(BaseModel):
    original: str
    suggested: str
    note: str = "Use a measured result only if you have one"

class ResumeFeedback(BaseModel):
    strengths: list[str] = []
    high_priority_improvements: list[str] = []
    section_feedback: list[SectionFeedback] = []
    missing_information: list[str] = []
    suggested_rewrites: list[Rewrite] = []

class AnalysisResult(BaseModel):
    resume_summary: ResumeSummary
    skills: list[Skill] = []
    job_recommendations: list[JobRecommendation] = []
    skill_gaps: list[SkillGap] = []
    learning_roadmap: list[RoadmapItem] = []
    resume_feedback: ResumeFeedback
