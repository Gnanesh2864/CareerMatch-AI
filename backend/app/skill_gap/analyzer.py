import json
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.models.job import Job
from app.models.candidate import CandidateProfile
from app.schemas.candidate import CandidateProfileSchema

class SkillGapAnalyzer:
    def __init__(self, db: Session, user_id: int):
        self.db = db
        self.user_id = user_id

    def analyze_gaps(self, target_job_id: Optional[int] = None) -> Dict[str, Any]:
        # 1. Fetch Candidate Profile
        prof_row = self.db.query(CandidateProfile).filter(CandidateProfile.user_id == self.user_id).first()
        if not prof_row or not prof_row.structured_data_json:
            return {"error": "Candidate profile not found."}
        candidate = CandidateProfileSchema.model_validate_json(prof_row.structured_data_json)

        explicit_skills = {s.name.lower() for s in candidate.skills if s.is_explicit}
        inferred_skills = {s.name.lower() for s in candidate.skills if not s.is_explicit}
        all_cand_skills = explicit_skills.union(inferred_skills)

        # 2. Fetch Relevant Jobs for Cluster Analysis
        if target_job_id:
            jobs = self.db.query(Job).filter(Job.id == target_job_id).all()
        else:
            jobs = self.db.query(Job).limit(10).all()

        # Skill frequency across target listings
        market_demand: Dict[str, int] = {}
        skill_to_jobs: Dict[str, List[Dict[str, str]]] = {}

        for j in jobs:
            jskills = json.loads(j.skills_json) if j.skills_json else []
            for s in jskills:
                s_lower = s.lower()
                market_demand[s_lower] = market_demand.get(s_lower, 0) + 1
                if s_lower not in skill_to_jobs:
                    skill_to_jobs[s_lower] = []
                skill_to_jobs[s_lower].append({
                    "job_id": j.id,
                    "title": j.title,
                    "company": j.company,
                })

        # Categorization
        demonstrated = []
        weak_evidence = []
        high_priority_gaps = []
        optional_gaps = []

        for skill, freq in sorted(market_demand.items(), key=lambda x: x[1], reverse=True):
            supporting = skill_to_jobs.get(skill, [])
            if skill in explicit_skills:
                demonstrated.append({
                    "skill": skill.title(),
                    "category": "Demonstrated",
                    "evidence_level": "High (Explicitly stated in profile)",
                    "market_demand_count": freq,
                    "supporting_jobs": supporting,
                })
            elif skill in inferred_skills:
                weak_evidence.append({
                    "skill": skill.title(),
                    "category": "Weak Evidence",
                    "evidence_level": "Medium (Inferred from project context)",
                    "market_demand_count": freq,
                    "supporting_jobs": supporting,
                })
            else:
                # Missing skill
                if freq >= 2:
                    high_priority_gaps.append({
                        "skill": skill.title(),
                        "category": "High Priority",
                        "evidence_level": "Missing from profile",
                        "market_demand_count": freq,
                        "supporting_jobs": supporting,
                    })
                else:
                    optional_gaps.append({
                        "skill": skill.title(),
                        "category": "Optional / Specialized",
                        "evidence_level": "Missing from profile",
                        "market_demand_count": freq,
                        "supporting_jobs": supporting,
                    })

        # Build actionable learning roadmap
        roadmap = []
        for i, gap in enumerate(high_priority_gaps[:4], 1):
            s_name = gap["skill"]
            roadmap.append({
                "step": i,
                "skill": s_name,
                "action": f"Build a verifiable project or integrate {s_name} into your current codebase.",
                "milestone": f"Week {i*2}: Publish working code and architectural documentation.",
                "market_impact": f"Directly unlocks requirements across {gap['market_demand_count']} target roles."
            })

        return {
            "demonstrated_skills": demonstrated,
            "weak_evidence_skills": weak_evidence,
            "high_priority_gaps": high_priority_gaps,
            "optional_gaps": optional_gaps,
            "roadmap": roadmap,
            "total_jobs_analyzed": len(jobs),
        }
