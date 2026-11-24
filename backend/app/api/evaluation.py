from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.evaluation.runner import EvaluationRunner
from app.schemas.evaluation import EvaluationReport

router = APIRouter(prefix="/evaluation", tags=["Evaluation Lab"])

_latest_report = None

@router.post("/run", response_model=EvaluationReport)
def run_evaluation_benchmark(k: int = Query(5, ge=1, le=20), db: Session = Depends(get_db)):
    global _latest_report
    runner = EvaluationRunner(db)
    _latest_report = runner.run_full_benchmark(k=k)
    return _latest_report

@router.get("/latest", response_model=EvaluationReport)
def get_latest_evaluation_report(db: Session = Depends(get_db)):
    global _latest_report
    if _latest_report is None:
        runner = EvaluationRunner(db)
        _latest_report = runner.run_full_benchmark(k=5)
    return _latest_report
