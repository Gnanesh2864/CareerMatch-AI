import json
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.job import Job
from app.schemas.job import JobResponse, JobCreate
from app.ingestion.pipeline import JobIngestionPipeline

router = APIRouter(prefix="/jobs", tags=["Jobs"])

def _job_to_response(job: Job) -> JobResponse:
    return JobResponse(
        id=job.id,
        title=job.title,
        company=job.company,
        description=job.description,
        responsibilities=json.loads(job.responsibilities_json) if job.responsibilities_json else [],
        required_qualifications=json.loads(job.required_qualifications_json) if job.required_qualifications_json else [],
        preferred_qualifications=json.loads(job.preferred_qualifications_json) if job.preferred_qualifications_json else [],
        skills=json.loads(job.skills_json) if job.skills_json else [],
        experience_level=job.experience_level,
        employment_type=job.employment_type,
        min_salary=job.min_salary,
        max_salary=job.max_salary,
        currency=job.currency,
        location=job.location,
        remote_status=job.remote_status,
        application_url=job.application_url,
        source=job.source,
        posting_date=job.posting_date,
        expiration_date=job.expiration_date,
        created_at=job.created_at,
    )

@router.get("", response_model=List[JobResponse])
def list_jobs(
    keyword: Optional[str] = Query(None),
    remote_status: Optional[str] = Query(None),
    experience_level: Optional[str] = Query(None),
    location: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    query = db.query(Job)
    if remote_status and remote_status != "all":
        query = query.filter(Job.remote_status == remote_status.lower())
    if experience_level and experience_level != "all":
        query = query.filter(Job.experience_level == experience_level.lower())
    if location and location != "all":
        query = query.filter(Job.location.ilike(f"%{location}%"))
    if keyword:
        kw = f"%{keyword}%"
        query = query.filter((Job.title.ilike(kw)) | (Job.company.ilike(kw)) | (Job.description.ilike(kw)))

    jobs = query.order_by(Job.id.desc()).offset(offset).limit(limit).all()
    return [_job_to_response(j) for j in jobs]

@router.get("/{job_id}", response_model=JobResponse)
def get_job_by_id(job_id: int, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return _job_to_response(job)

@router.post("/ingest")
def trigger_ingestion(db: Session = Depends(get_db)):
    pipeline = JobIngestionPipeline(db)
    stats = pipeline.run()
    return {"message": "Job ingestion pipeline executed.", "stats": stats}
