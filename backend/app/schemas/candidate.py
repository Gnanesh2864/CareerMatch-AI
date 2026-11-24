from typing import List, Optional
from pydantic import BaseModel, Field

class CandidateSkill(BaseModel):
    name: str
    category: str = "General"  # Languages, Frameworks, Databases, Cloud/DevOps, AI/ML, Tools
    is_explicit: bool = True   # True if directly extracted from text, False if inferred from projects
    years_experience: Optional[float] = None
    confidence: float = 1.0

class CandidateExperience(BaseModel):
    company: str
    role: str
    location: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    is_current: bool = False
    description: str = ""
    technologies: List[str] = []

class CandidateEducation(BaseModel):
    institution: str
    degree: str
    field_of_study: Optional[str] = None
    graduation_year: Optional[int] = None
    gpa: Optional[float] = None

class CandidateProject(BaseModel):
    title: str
    description: str = ""
    technologies: List[str] = []
    url: Optional[str] = None

class CandidateCertification(BaseModel):
    name: str
    issuer: Optional[str] = None
    year: Optional[int] = None

class CandidateProfileSchema(BaseModel):
    full_name: str = ""
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    summary: str = ""
    experience_level: str = "mid"  # entry, mid, senior, lead
    total_years_experience: float = 0.0
    career_interests: List[str] = []
    skills: List[CandidateSkill] = []
    experience: List[CandidateExperience] = []
    education: List[CandidateEducation] = []
    projects: List[CandidateProject] = []
    certifications: List[CandidateCertification] = []

class ResumeParseResponse(BaseModel):
    success: bool
    structured_profile: CandidateProfileSchema
    raw_text_preview: str
    message: str
