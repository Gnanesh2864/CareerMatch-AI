import json
import logging
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.models.job import Job
from app.models.candidate import CandidateProfile
from app.models.application import JobApplication
from app.schemas.candidate import CandidateProfileSchema
from app.retrieval.hybrid_retriever import HybridRetriever
from app.ranking.scorer import multi_signal_ranker

logger = logging.getLogger(__name__)

class CareerAgentTools:
    def __init__(self, db: Session, user_id: int):
        self.db = db
        self.user_id = user_id
        self.retriever = HybridRetriever(db)

    # 1. search_jobs
    def search_jobs(self, query: str = "", top_k: int = 5, remote_only: bool = False) -> List[Dict[str, Any]]:
        remote = "remote" if remote_only else None
        results = self.retriever.retrieve(query_text=query, top_k=top_k, remote_status=remote)
        out = []
        for r in results:
            j = r["job"]
            out.append({
                "job_id": j.id,
                "title": j.title,
                "company": j.company,
                "location": j.location,
                "remote_status": j.remote_status,
                "experience_level": j.experience_level,
                "skills": json.loads(j.skills_json) if j.skills_json else [],
                "hybrid_score": round(r["hybrid_score"], 3),
            })
        return out

    # 2. retrieve_candidate_profile
    def retrieve_candidate_profile(self) -> Dict[str, Any]:
        row = self.db.query(CandidateProfile).filter(CandidateProfile.user_id == self.user_id).first()
        if not row or not row.structured_data_json:
            return {"error": "No candidate profile found. Please upload a resume first."}
        cand = CandidateProfileSchema.model_validate_json(row.structured_data_json)
        return {
            "full_name": cand.full_name,
            "skills": [s.name for s in cand.skills],
            "explicit_skills": [s.name for s in cand.skills if s.is_explicit],
            "experience_level": cand.experience_level,
            "total_years_experience": cand.total_years_experience,
            "education": [{"degree": e.degree, "institution": e.institution} for e in cand.education],
            "projects_count": len(cand.projects),
        }

    # 3. get_job_details
    def get_job_details(self, job_id: int) -> Dict[str, Any]:
        j = self.db.query(Job).filter(Job.id == job_id).first()
        if not j:
            return {"error": f"Job ID {job_id} not found."}
        return {
            "job_id": j.id,
            "title": j.title,
            "company": j.company,
            "description": j.description,
            "responsibilities": json.loads(j.responsibilities_json) if j.responsibilities_json else [],
            "required_qualifications": json.loads(j.required_qualifications_json) if j.required_qualifications_json else [],
            "skills": json.loads(j.skills_json) if j.skills_json else [],
            "experience_level": j.experience_level,
            "remote_status": j.remote_status,
            "salary": f"${j.min_salary or 'N/A'} - ${j.max_salary or 'N/A'} {j.currency}",
            "application_url": j.application_url,
        }

    # 4. compare_jobs
    def compare_jobs(self, job_ids: List[int]) -> Dict[str, Any]:
        jobs = self.db.query(Job).filter(Job.id.in_(job_ids)).all()
        if not jobs:
            return {"error": "No jobs found for the provided IDs."}
        comparison = []
        for j in jobs:
            comparison.append({
                "job_id": j.id,
                "title": j.title,
                "company": j.company,
                "remote_status": j.remote_status,
                "experience_level": j.experience_level,
                "skills": json.loads(j.skills_json) if j.skills_json else [],
                "salary": f"${j.min_salary or 'N/A'} - ${j.max_salary or 'N/A'}",
            })
        return {"comparison": comparison, "total": len(jobs)}

    # 5. analyze_job_match
    def analyze_job_match(self, job_id: int) -> Dict[str, Any]:
        j = self.db.query(Job).filter(Job.id == job_id).first()
        if not j:
            return {"error": f"Job ID {job_id} not found."}
        prof_row = self.db.query(CandidateProfile).filter(CandidateProfile.user_id == self.user_id).first()
        if not prof_row or not prof_row.structured_data_json:
            return {"error": "Candidate profile not found."}
        candidate = CandidateProfileSchema.model_validate_json(prof_row.structured_data_json)
        cand_embed = json.loads(prof_row.embedding_json) if prof_row.embedding_json else None

        breakdown = multi_signal_ranker.score_match(candidate, j, cand_embed)
        return {
            "job_id": j.id,
            "title": j.title,
            "company": j.company,
            "composite_score": breakdown.composite_score,
            "matched_skills": breakdown.matched_skills,
            "missing_skills": breakdown.missing_skills,
            "strengths": breakdown.strengths,
            "gaps": breakdown.gaps,
            "explanation_summary": breakdown.explanation_summary,
        }

    # 6. identify_skill_gaps
    def identify_skill_gaps(self, job_ids: Optional[List[int]] = None) -> Dict[str, Any]:
        prof_row = self.db.query(CandidateProfile).filter(CandidateProfile.user_id == self.user_id).first()
        if not prof_row or not prof_row.structured_data_json:
            return {"error": "Candidate profile not found."}
        candidate = CandidateProfileSchema.model_validate_json(prof_row.structured_data_json)
        cand_skills = set([s.name.lower() for s in candidate.skills])

        query = self.db.query(Job)
        if job_ids:
            query = query.filter(Job.id.in_(job_ids))
        target_jobs = query.limit(10).all()

        missing_frequency: Dict[str, int] = {}
        for j in target_jobs:
            jskills = json.loads(j.skills_json) if j.skills_json else []
            for s in jskills:
                if s.lower() not in cand_skills:
                    missing_frequency[s] = missing_frequency.get(s, 0) + 1

        sorted_gaps = sorted(missing_frequency.items(), key=lambda x: x[1], reverse=True)
        return {
            "high_priority_gaps": [{"skill": s.title(), "frequency": count} for s, count in sorted_gaps[:5]],
            "all_gaps": [{"skill": s.title(), "frequency": count} for s, count in sorted_gaps],
            "jobs_analyzed": len(target_jobs),
        }

    # 7. recommend_learning_priorities
    def recommend_learning_priorities(self, top_n: int = 3) -> Dict[str, Any]:
        gaps_result = self.identify_skill_gaps()
        if "error" in gaps_result:
            return gaps_result
        top_gaps = gaps_result.get("high_priority_gaps", [])[:top_n]
        plan = []
        for i, item in enumerate(top_gaps, 1):
            skill = item["skill"]
            plan.append({
                "priority_rank": i,
                "skill": skill,
                "suggested_project": f"Build an end-to-end service or benchmark leveraging {skill}.",
                "market_demand_weight": item["frequency"],
            })
        return {"learning_roadmap": plan}

    # 8. save_job
    def save_job(self, job_id: int) -> Dict[str, Any]:
        j = self.db.query(Job).filter(Job.id == job_id).first()
        if not j:
            return {"error": f"Job ID {job_id} not found."}
        existing = self.db.query(JobApplication).filter(
            JobApplication.user_id == self.user_id,
            JobApplication.job_id == job_id
        ).first()
        if existing:
            return {"message": "Job already saved.", "application_id": existing.id}
        new_app = JobApplication(
            user_id=self.user_id,
            job_id=job_id,
            status="saved",
            feedback="interested",
        )
        self.db.add(new_app)
        self.db.commit()
        return {"message": f"Successfully saved job '{j.title}' at {j.company}.", "job_id": job_id}

    # 9. update_job_status
    def update_job_status(self, job_id: int, new_status: str, notes: Optional[str] = None) -> Dict[str, Any]:
        app = self.db.query(JobApplication).filter(
            JobApplication.user_id == self.user_id,
            JobApplication.job_id == job_id
        ).first()
        if not app:
            app = JobApplication(user_id=self.user_id, job_id=job_id, status=new_status, notes=notes)
            self.db.add(app)
        else:
            app.status = new_status
            if notes:
                app.notes = notes
        self.db.commit()
        return {"message": f"Updated job ID {job_id} status to '{new_status}'.", "status": new_status}

    # 10. retrieve_saved_jobs
    def retrieve_saved_jobs(self) -> List[Dict[str, Any]]:
        apps = self.db.query(JobApplication).filter(JobApplication.user_id == self.user_id).all()
        out = []
        for a in apps:
            j = a.job
            out.append({
                "application_id": a.id,
                "job_id": j.id,
                "title": j.title,
                "company": j.company,
                "status": a.status,
                "feedback": a.feedback,
                "notes": a.notes,
            })
        return out

    # 11. generate_application_checklist
    def generate_application_checklist(self, job_id: int) -> Dict[str, Any]:
        j = self.db.query(Job).filter(Job.id == job_id).first()
        if not j:
            return {"error": f"Job ID {job_id} not found."}
        skills = json.loads(j.skills_json) if j.skills_json else []
        return {
            "job_id": j.id,
            "checklist": [
                f"Review required qualifications for {j.company} ({j.experience_level} role).",
                f"Verify your resume highlights key technologies: {', '.join([s.title() for s in skills[:3]])}.",
                "Draft tailored cover letter focusing on high-scale systems and verifiable metrics.",
                "Review system design principles and prepare code repository links.",
                f"Submit application via: {j.application_url or 'Company Portal'}.",
            ]
        }

    # 12. prepare_resume_customization_suggestions
    def prepare_resume_customization_suggestions(self, job_id: int) -> Dict[str, Any]:
        match_analysis = self.analyze_job_match(job_id)
        if "error" in match_analysis:
            return match_analysis
        return {
            "job_id": job_id,
            "suggestions": [
                f"Emphasize demonstrated achievements with {', '.join(match_analysis.get('matched_skills', [])[:3])}.",
                f"Address gaps in {', '.join(match_analysis.get('missing_skills', [])[:2])} by showcasing relevant personal or open-source projects.",
                "Include quantifiable metrics (e.g. latency improvements, test coverage percentage, request throughput) in work experience bullets."
            ]
        }

    # 13. generate_interview_questions
    def generate_interview_questions(self, job_id: int) -> Dict[str, Any]:
        j = self.db.query(Job).filter(Job.id == job_id).first()
        if not j:
            return {"error": f"Job ID {job_id} not found."}
        skills = json.loads(j.skills_json) if j.skills_json else ["general"]
        return {
            "technical_questions": [
                f"How would you architect a production system in {skills[0].title()} to handle high concurrency and failures?",
                f"What are the main tradeoffs when indexing and caching data with {skills[1].title() if len(skills) > 1 else 'SQL'}?",
                "Describe a situation where a deployed pipeline had latency bottlenecks and how you profiled it."
            ],
            "behavioral_questions": [
                "Tell me about a time you had to push back on a requirement or compromise on technical debt.",
                "How do you approach learning an unfamiliar technology stack under tight delivery deadlines?"
            ]
        }

    # 14. summarize_job_search
    def summarize_job_search(self) -> Dict[str, Any]:
        total_jobs = self.db.query(Job).count()
        saved_count = self.db.query(JobApplication).filter(JobApplication.user_id == self.user_id).count()
        applied_count = self.db.query(JobApplication).filter(
            JobApplication.user_id == self.user_id,
            JobApplication.status == "applied"
        ).count()
        return {
            "total_available_opportunities": total_jobs,
            "total_saved": saved_count,
            "total_applied": applied_count,
            "status": "Active search in progress",
        }
