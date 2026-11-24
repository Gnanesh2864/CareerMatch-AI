import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Float, Index
from app.database import Base

class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), index=True, nullable=False)
    company = Column(String(255), index=True, nullable=False)
    description = Column(Text, nullable=False)
    responsibilities_json = Column(Text, nullable=True)  # JSON array
    required_qualifications_json = Column(Text, nullable=True)  # JSON array
    preferred_qualifications_json = Column(Text, nullable=True)  # JSON array
    skills_json = Column(Text, nullable=True)  # JSON array of normalized skill names
    experience_level = Column(String(50), index=True, default="mid")  # entry, mid, senior, lead, executive
    employment_type = Column(String(50), index=True, default="full-time")  # full-time, part-time, contract, internship
    min_salary = Column(Float, nullable=True)
    max_salary = Column(Float, nullable=True)
    currency = Column(String(10), default="USD")
    location = Column(String(255), index=True, default="Remote")
    remote_status = Column(String(50), index=True, default="remote")  # remote, hybrid, on-site
    application_url = Column(String(1024), nullable=True)
    source = Column(String(100), default="open_dataset")
    posting_date = Column(DateTime, default=datetime.datetime.utcnow)
    expiration_date = Column(DateTime, nullable=True)
    content_hash = Column(String(64), unique=True, index=True, nullable=False)  # SHA-256 for deduplication
    embedding_json = Column(Text, nullable=True)  # Serialized 384-d vector embedding
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    __table_args__ = (
        Index("ix_jobs_company_title", "company", "title"),
        Index("ix_jobs_remote_exp", "remote_status", "experience_level"),
    )
