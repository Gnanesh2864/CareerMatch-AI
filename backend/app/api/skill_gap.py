from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.skill_gap.analyzer import SkillGapAnalyzer
from app.auth.dependencies import get_current_user_optional

router = APIRouter(prefix="/skills", tags=["Skill Gap Intelligence"])

@router.get("/gap-analysis")
def get_skill_gap_analysis(
    job_id: Optional[int] = Query(None),
    current_user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    user_id = current_user.id if current_user else 1
    analyzer = SkillGapAnalyzer(db, user_id)
    return analyzer.analyze_gaps(target_job_id=job_id)
