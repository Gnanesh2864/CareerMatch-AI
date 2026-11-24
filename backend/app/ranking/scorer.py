import json
from typing import Dict, Any, List, Tuple
from app.models.job import Job
from app.schemas.candidate import CandidateProfileSchema
from app.schemas.matching import MatchSignalBreakdown
from app.embeddings.embedder import embedding_service

class MultiSignalRanker:
    """
    Computes a transparent, explainable 5-signal composite match score
    between a CandidateProfile and a Job.
    Signals:
    1. Semantic Similarity (30%)
    2. Skill Overlap & Alignment (35%)
    3. Experience & Seniority Compatibility (15%)
    4. Education Fit (10%)
    5. Work Preferences Alignment (10%)
    """

    EXP_LEVEL_MAP = {
        "internship": 0.5,
        "entry": 1.5,
        "mid": 3.5,
        "senior": 6.0,
        "lead": 9.0,
        "executive": 12.0
    }

    def score_match(
        self,
        candidate: CandidateProfileSchema,
        job: Job,
        candidate_embedding: List[float] = None,
    ) -> MatchSignalBreakdown:
        # 1. Semantic Score
        semantic_score = 0.5
        if candidate_embedding and job.embedding_json:
            try:
                job_vec = json.loads(job.embedding_json)
                raw_sim = embedding_service.cosine_similarity(candidate_embedding, job_vec)
                semantic_score = max(0.0, float((raw_sim + 1.0) / 2.0))
            except Exception:
                semantic_score = 0.5

        # 2. Skill Overlap
        job_skills = set([s.lower() for s in (json.loads(job.skills_json) if job.skills_json else [])])
        cand_explicit = set([s.name.lower() for s in candidate.skills if s.is_explicit])
        cand_inferred = set([s.name.lower() for s in candidate.skills if not s.is_explicit])
        cand_all = cand_explicit.union(cand_inferred)

        matched_skills = sorted(list(job_skills.intersection(cand_explicit)))
        partial_skills = sorted(list(job_skills.intersection(cand_inferred)))
        missing_skills = sorted(list(job_skills - cand_all))

        if job_skills:
            # Explicit matches get 1.0 weight, inferred get 0.6 weight
            match_points = len(matched_skills) * 1.0 + len(partial_skills) * 0.6
            skill_score = min(1.0, match_points / max(1.0, float(len(job_skills))))
        else:
            skill_score = 0.7  # Neutral default when job lists no explicit tags

        # 3. Experience Compatibility
        req_exp = self.EXP_LEVEL_MAP.get(job.experience_level.lower(), 3.0)
        cand_exp = candidate.total_years_experience

        if cand_exp >= req_exp:
            exp_score = 1.0
        else:
            diff = req_exp - cand_exp
            exp_score = max(0.2, 1.0 - (diff * 0.25))

        # 4. Education Fit
        # Most tech roles accept B.S. or practical equivalent
        has_degree = len(candidate.education) > 0
        edu_score = 1.0 if has_degree else 0.8

        # 5. Preference Alignment
        pref_align = []
        pref_score = 0.8
        if job.remote_status.lower() in ["remote", "hybrid"]:
            pref_align.append(f"Flexible working mode ({job.remote_status})")
            pref_score += 0.2

        pref_score = min(1.0, pref_score)

        # Composite Score Calculation (Scaled to 0 - 100)
        # Weights: Semantic 30%, Skills 35%, Experience 15%, Education 10%, Preference 10%
        composite = (
            (semantic_score * 0.30) +
            (skill_score * 0.35) +
            (exp_score * 0.15) +
            (edu_score * 0.10) +
            (pref_score * 0.10)
        ) * 100.0

        # Construct grounded explanation & evidence
        strengths = []
        if matched_skills:
            strengths.append(f"Strong skill match: {', '.join([s.title() for s in matched_skills[:5]])}")
        if cand_exp >= req_exp:
            strengths.append(f"Meets seniority requirement ({job.experience_level.capitalize()} level)")
        if semantic_score > 0.75:
            strengths.append("High semantic alignment with candidate background and projects")

        gaps = []
        if missing_skills:
            gaps.append(f"Missing required skills: {', '.join([s.title() for s in missing_skills[:4]])}")
        if cand_exp < req_exp:
            gaps.append(f"Experience gap: target role prefers ~{req_exp:.0f} yrs, candidate profile reflects ~{cand_exp:.1f} yrs")

        summary_parts = []
        if composite >= 80:
            summary_parts.append("Excellent match")
        elif composite >= 65:
            summary_parts.append("Strong competitive match")
        elif composite >= 50:
            summary_parts.append("Moderate match with addressable gaps")
        else:
            summary_parts.append("Growth opportunity with significant skill requirements")

        if matched_skills:
            summary_parts.append(f"matches key competencies in {', '.join([s.title() for s in matched_skills[:3]])}")
        if missing_skills:
            summary_parts.append(f"requires building evidence for {', '.join([s.title() for s in missing_skills[:2]])}")

        explanation_summary = ". ".join(summary_parts) + "."

        return MatchSignalBreakdown(
            semantic_score=round(semantic_score, 3),
            skill_overlap_score=round(skill_score, 3),
            experience_score=round(exp_score, 3),
            education_score=round(edu_score, 3),
            preference_score=round(pref_score, 3),
            composite_score=round(composite, 1),
            matched_skills=[s.title() for s in matched_skills],
            missing_skills=[s.title() for s in missing_skills],
            partial_skills=[s.title() for s in partial_skills],
            strengths=strengths,
            gaps=gaps,
            preference_alignment=pref_align,
            explanation_summary=explanation_summary,
        )

multi_signal_ranker = MultiSignalRanker()
