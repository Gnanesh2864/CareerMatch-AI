import json
import logging
import httpx
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.config import settings
from app.models.job import Job
from app.models.candidate import CandidateProfile
from app.schemas.candidate import CandidateProfileSchema
from app.rag.guardrails import wrap_untrusted_context, sanitize_untrusted_text
from app.ranking.scorer import multi_signal_ranker

logger = logging.getLogger(__name__)

class RAGCareerAssistant:
    def __init__(self, db: Session):
        self.db = db

    def answer_query(
        self,
        query: str,
        user_id: int,
        context_job_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Executes grounded retrieval-augmented career guidance based on
        candidate profile and retrieved job postings.
        """
        # 1. Fetch Candidate Profile
        profile_row = self.db.query(CandidateProfile).filter(CandidateProfile.user_id == user_id).first()
        candidate = None
        cand_embed = None
        if profile_row and profile_row.structured_data_json:
            try:
                candidate = CandidateProfileSchema.model_validate_json(profile_row.structured_data_json)
                cand_embed = json.loads(profile_row.embedding_json) if profile_row.embedding_json else None
            except Exception:
                pass

        # 2. Fetch Relevant Job Context
        context_jobs: List[Job] = []
        if context_job_id:
            specific_job = self.db.query(Job).filter(Job.id == context_job_id).first()
            if specific_job:
                context_jobs.append(specific_job)

        if not context_jobs:
            # Fallback to top 3 jobs in database
            context_jobs = self.db.query(Job).limit(3).all()

        # 3. Build Evidence Citations
        citations = []
        for j in context_jobs:
            citations.append({
                "job_id": j.id,
                "title": j.title,
                "company": j.company,
                "location": j.location,
                "skills": json.loads(j.skills_json) if j.skills_json else []
            })

        # 4. Check for External LLM Provider
        if settings.GEMINI_API_KEY:
            try:
                response_text = self._call_gemini(query, candidate, context_jobs)
                return {
                    "answer": response_text,
                    "citations": citations,
                    "model": "gemini-1.5-pro",
                    "grounded": True,
                }
            except Exception as e:
                logger.warning(f"Gemini API call failed ({e}). Using grounded local synthesis engine.")

        # 5. Grounded Offline Synthesis Engine
        local_answer = self._synthesize_grounded_answer(query, candidate, context_jobs)
        return {
            "answer": local_answer,
            "citations": citations,
            "model": "grounded-local-engine",
            "grounded": True,
        }

    def _call_gemini(self, query: str, candidate: Optional[CandidateProfileSchema], jobs: List[Job]) -> str:
        prompt = self._build_rag_prompt(query, candidate, jobs)
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent?key={settings.GEMINI_API_KEY}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.2, "maxOutputTokens": 1000}
        }
        with httpx.Client(timeout=15.0) as client:
            resp = client.post(url, json=payload)
            resp.raise_for_status()
            data = resp.json()
            return data["candidates"][0]["content"]["parts"][0]["text"]

    def _build_rag_prompt(self, query: str, candidate: Optional[CandidateProfileSchema], jobs: List[Job]) -> str:
        cand_str = candidate.model_dump_json(indent=2) if candidate else "No candidate profile uploaded."
        jobs_str = "\n\n".join([
            f"Job ID: {j.id}\nTitle: {j.title}\nCompany: {j.company}\nDescription: {j.description}\nSkills: {j.skills_json}"
            for j in jobs
        ])
        return (
            "You are CareerMatch AI, a strictly grounded, objective career intelligence assistant.\n"
            "Rules:\n"
            "1. Answer ONLY using the facts from the Candidate Profile and Retrieved Jobs below.\n"
            "2. Never hallucinate skills or qualifications.\n"
            "3. If information is missing, explicitly state so.\n"
            "4. Provide actionable, evidence-based recommendations.\n\n"
            f"{wrap_untrusted_context('candidate_profile', cand_str)}\n\n"
            f"{wrap_untrusted_context('retrieved_jobs', jobs_str)}\n\n"
            f"User Question: {sanitize_untrusted_text(query)}"
        )

    def _synthesize_grounded_answer(
        self,
        query: str,
        candidate: Optional[CandidateProfileSchema],
        jobs: List[Job]
    ) -> str:
        q_lower = query.lower()

        if not jobs:
            return "No job context is currently available. Please search for or select a job first."

        target_job = jobs[0]
        job_skills = set(json.loads(target_job.skills_json) if target_job.skills_json else [])
        cand_skills = set([s.name.lower() for s in candidate.skills]) if candidate else set()

        matched = sorted(list(job_skills.intersection(cand_skills)))
        missing = sorted(list(job_skills - cand_skills))

        # Handle specific question intents
        if any(w in q_lower for w in ["why", "relevant", "match"]):
            answer = (
                f"### Relevance Analysis for **{target_job.title}** at **{target_job.company}**\n\n"
                f"- **Confirmed Skill Overlap**: You meet key required competencies in "
                f"{', '.join([m.title() for m in matched[:4]]) if matched else 'general software foundations'}.\n"
                f"- **Seniority Alignment**: The role seeks a **{target_job.experience_level.title()}** engineer. "
                f"Your profile reflects approximately **{candidate.total_years_experience if candidate else '1-2'} years** experience.\n"
                f"- **Work Mode Fit**: This position is categorized as **{target_job.remote_status.title()}** "
                f"({target_job.location}).\n\n"
            )
            if missing:
                answer += f"**Key Skill Gaps to Bridge**: The job specifically lists requirements for {', '.join([m.title() for m in missing[:3]])}."
            return answer

        if any(w in q_lower for w in ["missing", "gap", "skill"]):
            if missing:
                return (
                    f"### Identified Skill Gaps for **{target_job.title}**\n\n"
                    f"Based on the required qualifications for {target_job.company}, the following skills are not explicitly documented in your resume:\n\n"
                    + "\n".join([f"- **{s.title()}**: Found in job requirements/technologies." for s in missing]) + "\n\n"
                    f"**Recommendation**: If you have hands-on project experience with any of these tools, add concrete project bullet points highlighting their usage."
                )
            else:
                return f"Excellent news! Your profile already covers all key technical skills listed for **{target_job.title}** ({', '.join([s.title() for s in job_skills])})."

        if any(w in q_lower for w in ["compare", "versus", "vs"]):
            if len(jobs) >= 2:
                j1, j2 = jobs[0], jobs[1]
                return (
                    f"### Position Comparison\n\n"
                    f"| Attribute | **{j1.title}** ({j1.company}) | **{j2.title}** ({j2.company}) |\n"
                    f"|---|---|---|\n"
                    f"| **Location / Mode** | {j1.location} ({j1.remote_status}) | {j2.location} ({j2.remote_status}) |\n"
                    f"| **Experience Level** | {j1.experience_level.title()} | {j2.experience_level.title()} |\n"
                    f"| **Key Skills** | {', '.join(json.loads(j1.skills_json or '[]')[:3]).title()} | {', '.join(json.loads(j2.skills_json or '[]')[:3]).title()} |\n"
                    f"| **Salary Band** | ${j1.min_salary or 'N/A':,} - ${j1.max_salary or 'N/A':,} | ${j2.min_salary or 'N/A':,} - ${j2.max_salary or 'N/A':,} |\n\n"
                    f"**Tradeoff Summary**: If your primary career focus is {j1.title.split()[0]}, {j1.company} provides direct alignment. "
                    f"Conversely, {j2.company} emphasizes {j2.title.split()[0]}."
                )

        if any(w in q_lower for w in ["prepare", "interview", "questions"]):
            return (
                f"### Interview Preparation for **{target_job.title}** ({target_job.company})\n\n"
                f"1. **Core Domain Deep-Dive**: Be prepared to discuss architectural tradeoffs in {', '.join([s.title() for s in list(job_skills)[:3]])}.\n"
                f"2. **Production Scenario Questions**: Practice explaining how you optimize latency, handle failure modes, and test distributed components.\n"
                f"3. **Behavioral Alignment**: Have 2 structured STAR stories demonstrating collaboration and resolving technical ambiguity."
            )

        # Default comprehensive grounded answer
        return (
            f"### Career Intelligence for **{target_job.title}**\n\n"
            f"**Company**: {target_job.company} | **Location**: {target_job.location} ({target_job.remote_status})\n\n"
            f"**Summary of Role**: {target_job.description[:350]}...\n\n"
            f"- **Your Matched Strengths**: {', '.join([m.title() for m in matched[:4]]) if matched else 'Foundational engineering skills'}\n"
            f"- **Missing Credentials**: {', '.join([m.title() for m in missing[:3]]) if missing else 'None detected'}\n\n"
            f"Let me know if you would like me to prepare an application checklist, interview questions, or a skill learning roadmap!"
        )
