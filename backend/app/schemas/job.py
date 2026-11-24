from typing import List, Optional
import datetime
from pydantic import BaseModel, Field

class JobBase(BaseModel):
    title: str
    company: str
    description: str
    responsibilities: List[str] = []
    required_qualifications: List[str] = []
    preferred_qualifications: List[str] = []
    skills: List[str] = []
    experience_level: str = "mid"
    employment_type: str = "full-time"
    min_salary: Optional[float] = None
    max_salary: Optional[float] = None
    currency: str = "USD"
    location: str = "Remote"
    remote_status: str = "remote"
    application_url: Optional[str] = None
    source: str = "open_dataset"
    expiration_date: Optional[datetime.datetime] = None

class JobCreate(JobBase):
    pass

class JobResponse(JobBase):
    id: int
    posting_date: datetime.datetime
    created_at: datetime.datetime

    class Config:
        from_attributes = True

class JobFilterParams(BaseModel):
    keyword: Optional[str] = None
    skills: List[str] = []
    remote_status: Optional[str] = None
    experience_level: Optional[str] = None
    location: Optional[str] = None
    min_salary: Optional[float] = None
    page: int = 1
    page_size: int = 15
