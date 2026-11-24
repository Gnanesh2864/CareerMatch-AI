import time
import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.job import Job
from app.models.candidate import CandidateProfile
from app.schemas.candidate import CandidateProfileSchema
from app.schemas.matching import (
    HybridSearchQuery,
    HybridSearchResponse,
    RankedJobMatch,
    MatchSignalBreakdown,
)
from app.retrieval.hybrid_retriever import HybridRetriever
from app.ranking.scorer import multi_signal_ranker
from app.api.jobs import _job_to_response
from app.auth.dependencies import get_current_user_optional

router = APIRouter(prefix="/search", tags=["Hybrid Retrieval & Ranking"])

@router.post("/hybrid", response_model=HybridSearchResponse)
def execute_hybrid_search(
    query_in: HybridSearchQuery,
    current_user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    t0 = time.time()
    retriever = HybridRetriever(db)

    # Fetch candidate profile if available
    candidate = None
    cand_embed = None
    if current_user:
        prof = db.query(CandidateProfile).filter(CandidateProfile.user_id == current_user.id).first()
        if prof and prof.structured_data_json:
            try:
                candidate = CandidateProfileSchema.model_validate_json(prof.structured_data_json)
                cand_embed = json.loads(prof.embedding_json) if prof.embedding_json else None
            except Exception:
                pass

    # If query text is empty but candidate profile exists, use profile for query
    effective_query = query_in.query_text
    if not effective_query and candidate:
        skills = [s.name for s in candidate.skills[:5]]
        effective_query = f"{candidate.experience_level} software engineer {' '.join(skills)}"

    raw_results = retriever.retrieve(
        query_text=effective_query,
        alpha=query_in.alpha,
        top_k=query_in.top_k,
        remote_status=query_in.remote_status,
        experience_level=query_in.experience_level,
        location=query_in.location,
        min_salary=query_in.min_salary,
    )

    ranked_matches = []
    for item in raw_results:
        job = item["job"]
        job_resp = _job_to_response(job)

        if candidate:
            match_breakdown = multi_signal_ranker.score_match(candidate, job, cand_embed)
        else:
            # Neutral baseline match signal when no candidate profile is logged in
            s_dense = item["dense_score"]
            s_hybrid = item["hybrid_score"]
            match_breakdown = MatchSignalBreakdown(
                semantic_score=round(s_dense, 3),
                skill_overlap_score=0.7,
                experience_score=0.8,
                education_score=0.8,
                preference_score=0.8,
                composite_score=round(s_hybrid * 100, 1),
                matched_skills=job_resp.skills[:3],
                explanation_summary="Relevant match based on query parameters and keyword density."
            )

        ranked_matches.append(RankedJobMatch(job=job_resp, match=match_breakdown))

    if query_in.rerank:
        # Sort by composite_score
        ranked_matches.sort(key=lambda x: x.match.composite_score, reverse=True)

    elapsed_ms = round((time.time() - t0) * 1000, 2)
    method_name = "Pure Keyword (BM25)" if query_in.alpha == 0.0 else (
        "Pure Semantic (Dense)" if query_in.alpha == 1.0 else f"Hybrid Fusion (α={query_in.alpha})"
    )
    if query_in.rerank:
        method_name += " + Multi-Signal Reranking"

    return HybridSearchResponse(
        results=ranked_matches,
        total_matches=len(ranked_matches),
        retrieval_method=method_name,
        execution_time_ms=elapsed_ms,
        alpha=query_in.alpha,
    )

@router.get("/match/{job_id}", response_model=MatchSignalBreakdown)
def get_match_breakdown(
    job_id: int,
    current_user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    candidate = None
    cand_embed = None
    if current_user:
        prof = db.query(CandidateProfile).filter(CandidateProfile.user_id == current_user.id).first()
        if prof and prof.structured_data_json:
            candidate = CandidateProfileSchema.model_validate_json(prof.structured_data_json)
            cand_embed = json.loads(prof.embedding_json) if prof.embedding_json else None

    if not candidate:
        # Generic breakdown
        skills = json.loads(job.skills_json) if job.skills_json else []
        return MatchSignalBreakdown(
            composite_score=75.0,
            matched_skills=skills[:3],
            explanation_summary="Upload your resume to receive a personalized match analysis."
        )

    return multi_signal_ranker.score_match(candidate, job, cand_embed)
