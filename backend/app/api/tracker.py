import datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.job import Job
from app.models.application import JobApplication
from app.personalization.memory import PersonalizationMemory
from app.auth.dependencies import get_current_user_optional

router = APIRouter(prefix="/tracker", tags=["Application Tracker"])

class UpdateStatusRequest(BaseModel):
    status: str
    notes: Optional[str] = None

class FeedbackRequest(BaseModel):
    feedback: str  # interested, not_interested, relevant, irrelevant

@router.get("")
def get_tracked_applications(
    current_user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    user_id = current_user.id if current_user else 1
    apps = db.query(JobApplication).filter(JobApplication.user_id == user_id).order_by(JobApplication.updated_at.desc()).all()
    results = []
    for a in apps:
        j = a.job
        results.append({
            "application_id": a.id,
            "job_id": j.id,
            "title": j.title,
            "company": j.company,
            "location": j.location,
            "remote_status": j.remote_status,
            "experience_level": j.experience_level,
            "status": a.status,
            "feedback": a.feedback,
            "notes": a.notes,
            "applied_date": a.applied_date.isoformat() if a.applied_date else None,
            "updated_at": a.updated_at.isoformat(),
        })
    return results

@router.post("/{job_id}")
def save_or_track_job(
    job_id: int,
    status: str = Query("saved"),
    current_user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    user_id = current_user.id if current_user else 1
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    app = db.query(JobApplication).filter(
        JobApplication.user_id == user_id,
        JobApplication.job_id == job_id
    ).first()

    if not app:
        app = JobApplication(
            user_id=user_id,
            job_id=job_id,
            status=status,
            feedback="interested",
            applied_date=datetime.datetime.utcnow() if status == "applied" else None,
        )
        db.add(app)
    else:
        app.status = status
        if status == "applied" and not app.applied_date:
            app.applied_date = datetime.datetime.utcnow()

    db.commit()
    return {"message": "Job successfully updated in tracker", "status": app.status}

@router.put("/{job_id}/status")
def update_application_status(
    job_id: int,
    req: UpdateStatusRequest,
    current_user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    user_id = current_user.id if current_user else 1
    app = db.query(JobApplication).filter(
        JobApplication.user_id == user_id,
        JobApplication.job_id == job_id
    ).first()
    if not app:
        app = JobApplication(user_id=user_id, job_id=job_id, status=req.status, notes=req.notes)
        db.add(app)
    else:
        app.status = req.status
        if req.notes is not None:
            app.notes = req.notes
        if req.status == "applied" and not app.applied_date:
            app.applied_date = datetime.datetime.utcnow()

    db.commit()
    return {"message": "Status updated successfully", "status": app.status}

@router.post("/{job_id}/feedback")
def submit_feedback(
    job_id: int,
    req: FeedbackRequest,
    current_user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    user_id = current_user.id if current_user else 1
    memory = PersonalizationMemory(db, user_id)
    return memory.record_feedback(job_id, req.feedback)

@router.get("/analytics")
def get_tracker_analytics(
    current_user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    user_id = current_user.id if current_user else 1
    apps = db.query(JobApplication).filter(JobApplication.user_id == user_id).all()

    counts = {
        "saved": 0,
        "applied": 0,
        "interview": 0,
        "offer": 0,
        "rejected": 0,
        "closed": 0,
    }
    feedback_counts = {
        "interested": 0,
        "not_interested": 0,
    }

    for a in apps:
        st = a.status.lower()
        if st in counts:
            counts[st] += 1
        fb = (a.feedback or "").lower()
        if fb in feedback_counts:
            feedback_counts[fb] += 1

    return {
        "total_tracked": len(apps),
        "status_funnel": counts,
        "feedback_metrics": feedback_counts,
        "response_rate": round(
            (counts["interview"] + counts["offer"]) / max(1, counts["applied"]) * 100, 1
        ) if counts["applied"] > 0 else 0.0
    }
