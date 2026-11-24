from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from app.schemas.job import JobResponse

class MatchSignalBreakdown(BaseModel):
    semantic_score: float = 0.0          # 0.0 - 1.0 (vector similarity)
    skill_overlap_score: float = 0.0     # 0.0 - 1.0 (exact & semantic skill fit)
    experience_score: float = 0.0        # 0.0 - 1.0 (seniority fit)
    education_score: float = 0.0         # 0.0 - 1.0 (degree requirements)
    preference_score: float = 0.0        # 0.0 - 1.0 (location/remote alignment)
    composite_score: float = 0.0         # 0.0 - 100.0 (weighted composite score)
    
    # Explainable Evidence Breakdown
    matched_skills: List[str] = []
    missing_skills: List[str] = []
    partial_skills: List[str] = []
    strengths: List[str] = []
    gaps: List[str] = []
    preference_alignment: List[str] = []
    explanation_summary: str = ""

class RankedJobMatch(BaseModel):
    job: JobResponse
    match: MatchSignalBreakdown

class HybridSearchQuery(BaseModel):
    query_text: str = ""
    candidate_id: Optional[int] = None
    alpha: float = 0.6  # 1.0 = Pure Semantic, 0.0 = Pure Keyword BM25
    top_k: int = 15
    remote_status: Optional[str] = None
    experience_level: Optional[str] = None
    location: Optional[str] = None
    min_salary: Optional[float] = None
    rerank: bool = True

class HybridSearchResponse(BaseModel):
    results: List[RankedJobMatch]
    total_matches: int
    retrieval_method: str
    execution_time_ms: float
    alpha: float
