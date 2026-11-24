import time
import logging
import json
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.agent.tools import CareerAgentTools
from app.schemas.agent import AgentRunResponse, AgentStepTrace

logger = logging.getLogger(__name__)

class CareerAgentOrchestrator:
    """
    Autonomous multi-step career agent orchestrator.
    Executes approved tools with state tracking, safety loops, and structured traces.
    """
    def __init__(self, db: Session, user_id: int):
        self.db = db
        self.user_id = user_id
        self.tools = CareerAgentTools(db, user_id)

    def run_agent(self, user_prompt: str, context_job_id: Optional[int] = None) -> AgentRunResponse:
        p_lower = user_prompt.lower()
        steps: List[AgentStepTrace] = []
        tools_used: List[str] = []

        # Workflow Detection & Dynamic Tool Sequence Execution

        # Workflow A: Find top jobs, rank them, explain top match, identify skill gaps
        if any(k in p_lower for k in ["find the top", "top jobs for my profile", "rank them", "best jobs"]):
            # Step 1: retrieve profile
            t0 = time.time()
            prof_out = self.tools.retrieve_candidate_profile()
            steps.append(AgentStepTrace(
                step_number=1,
                thought="Retrieving structured candidate profile to understand competencies.",
                tool_name="retrieve_candidate_profile",
                tool_input={},
                tool_output_summary=f"Extracted {len(prof_out.get('skills', []))} skills, {prof_out.get('total_years_experience', 0)} years experience.",
                execution_time_ms=round((time.time() - t0) * 1000, 2)
            ))
            tools_used.append("retrieve_candidate_profile")

            # Step 2: search relevant jobs
            t0 = time.time()
            jobs_out = self.tools.search_jobs(query=" ".join(prof_out.get("skills", [])[:4]), top_k=5)
            steps.append(AgentStepTrace(
                step_number=2,
                thought="Searching job database matching candidate skills.",
                tool_name="search_jobs",
                tool_input={"top_k": 5},
                tool_output_summary=f"Found {len(jobs_out)} high-relevance positions.",
                execution_time_ms=round((time.time() - t0) * 1000, 2)
            ))
            tools_used.append("search_jobs")

            # Step 3: analyze top job match
            top_job_id = jobs_out[0]["job_id"] if jobs_out else 1
            t0 = time.time()
            match_out = self.tools.analyze_job_match(top_job_id)
            steps.append(AgentStepTrace(
                step_number=3,
                thought="Analyzing granular match breakdown for the top opportunity.",
                tool_name="analyze_job_match",
                tool_input={"job_id": top_job_id},
                tool_output_summary=f"Composite score: {match_out.get('composite_score', 0)}%. Matched: {len(match_out.get('matched_skills', []))} skills.",
                execution_time_ms=round((time.time() - t0) * 1000, 2)
            ))
            tools_used.append("analyze_job_match")

            # Step 4: identify skill gaps
            t0 = time.time()
            gaps_out = self.tools.identify_skill_gaps()
            steps.append(AgentStepTrace(
                step_number=4,
                thought="Aggregating skill gaps across target listings.",
                tool_name="identify_skill_gaps",
                tool_input={},
                tool_output_summary=f"Identified {len(gaps_out.get('high_priority_gaps', []))} priority skill gaps.",
                execution_time_ms=round((time.time() - t0) * 1000, 2)
            ))
            tools_used.append("identify_skill_gaps")

            final_text = (
                f"### Multi-Step Career Discovery Analysis\n\n"
                f"I evaluated your profile against open market opportunities and found **{len(jobs_out)} high-match roles**.\n\n"
                f"**Top Recommendation**: **{jobs_out[0]['title']}** at **{jobs_out[0]['company']}** (Match Score: **{match_out.get('composite_score')}%**)\n"
                f"- **Strengths**: {', '.join(match_out.get('matched_skills', [])[:4])}\n"
                f"- **Gaps to Address**: {', '.join(match_out.get('missing_skills', [])[:3]) if match_out.get('missing_skills') else 'None'}\n\n"
                f"**Market Skill Gap Priorities**:\n"
                + "\n".join([f"- **{g['skill']}**: Demanded by {g['frequency']} postings" for g in gaps_out.get("high_priority_gaps", [])[:3]]) +
                f"\n\nWould you like me to save this position or create an application checklist?"
            )

        # Workflow B: Compare saved jobs
        elif any(k in p_lower for k in ["compare", "versus", "vs"]):
            t0 = time.time()
            saved = self.tools.retrieve_saved_jobs()
            steps.append(AgentStepTrace(
                step_number=1,
                thought="Retrieving saved positions from candidate job tracker.",
                tool_name="retrieve_saved_jobs",
                tool_input={},
                tool_output_summary=f"Found {len(saved)} tracked applications.",
                execution_time_ms=round((time.time() - t0) * 1000, 2)
            ))
            tools_used.append("retrieve_saved_jobs")

            job_ids = [s["job_id"] for s in saved[:3]]
            if not job_ids:
                job_ids = [1, 2]

            t0 = time.time()
            comp_out = self.tools.compare_jobs(job_ids)
            steps.append(AgentStepTrace(
                step_number=2,
                thought="Comparing technical requirements and compensation bands.",
                tool_name="compare_jobs",
                tool_input={"job_ids": job_ids},
                tool_output_summary=f"Synthesized comparison across {len(comp_out.get('comparison', []))} positions.",
                execution_time_ms=round((time.time() - t0) * 1000, 2)
            ))
            tools_used.append("compare_jobs")

            final_text = (
                f"### Position Comparison & Tradeoffs\n\n"
                + "\n".join([
                    f"- **{c['title']}** at **{c['company']}**: {c['remote_status'].title()} | {c['experience_level'].title()} | Tech: {', '.join(c['skills'][:4])}"
                    for c in comp_out.get("comparison", [])
                ]) + "\n\n**Tradeoff Recommendation**: Focus on the role that provides the highest growth in frontier technologies aligned with your goals."
            )

        # Workflow C: Skill Gap & Learning Roadmap
        elif any(k in p_lower for k in ["gap", "learning", "roadmap", "plan", "priorities"]):
            t0 = time.time()
            gaps_out = self.tools.identify_skill_gaps()
            steps.append(AgentStepTrace(
                step_number=1,
                thought="Scanning job requirements across target tech sectors.",
                tool_name="identify_skill_gaps",
                tool_input={},
                tool_output_summary=f"Identified {len(gaps_out.get('high_priority_gaps', []))} major skill gaps.",
                execution_time_ms=round((time.time() - t0) * 1000, 2)
            ))
            tools_used.append("identify_skill_gaps")

            t0 = time.time()
            plan_out = self.tools.recommend_learning_priorities(top_n=3)
            steps.append(AgentStepTrace(
                step_number=2,
                thought="Generating prioritized project and learning roadmap.",
                tool_name="recommend_learning_priorities",
                tool_input={"top_n": 3},
                tool_output_summary="Created actionable 3-phase preparation roadmap.",
                execution_time_ms=round((time.time() - t0) * 1000, 2)
            ))
            tools_used.append("recommend_learning_priorities")

            roadmap_items = plan_out.get("learning_roadmap", [])
            final_text = (
                f"### Strategic Learning & Preparation Roadmap\n\n"
                f"Based on required qualifications across verified technical jobs:\n\n"
                + "\n".join([
                    f"**Phase {item['priority_rank']}: Master {item['skill']}** (Market Demand Weight: {item['market_demand_weight']})\n"
                    f"- Project Recommendation: {item['suggested_project']}"
                    for item in roadmap_items
                ]) + "\n\nCompleting these projects will maximize match score across top-tier listings."
            )

        # Workflow E: Interview Prep & Checklist
        elif any(k in p_lower for k in ["prepare", "interview", "checklist", "apply"]):
            target_id = context_job_id or 1
            t0 = time.time()
            chk_out = self.tools.generate_application_checklist(target_id)
            steps.append(AgentStepTrace(
                step_number=1,
                thought="Generating custom application checklist for target role.",
                tool_name="generate_application_checklist",
                tool_input={"job_id": target_id},
                tool_output_summary="Generated 5-point application preparation checklist.",
                execution_time_ms=round((time.time() - t0) * 1000, 2)
            ))
            tools_used.append("generate_application_checklist")

            t0 = time.time()
            q_out = self.tools.generate_interview_questions(target_id)
            steps.append(AgentStepTrace(
                step_number=2,
                thought="Synthesizing technical and architectural interview questions.",
                tool_name="generate_interview_questions",
                tool_input={"job_id": target_id},
                tool_output_summary="Formulated technical and behavioral interview questions.",
                execution_time_ms=round((time.time() - t0) * 1000, 2)
            ))
            tools_used.append("generate_interview_questions")

            final_text = (
                f"### Application & Interview Preparation\n\n"
                f"#### Pre-Application Checklist:\n"
                + "\n".join([f"- [ ] {c}" for c in chk_out.get("checklist", [])]) +
                f"\n\n#### High-Probability Technical Interview Questions:\n"
                + "\n".join([f"1. {q}" for q in q_out.get("technical_questions", [])]) +
                f"\n\n#### Behavioral Preparation:\n"
                + "\n".join([f"- {q}" for q in q_out.get("behavioral_questions", [])])
            )

        # General Search / Default
        else:
            t0 = time.time()
            sum_out = self.tools.summarize_job_search()
            steps.append(AgentStepTrace(
                step_number=1,
                thought="Checking overall career match platform state.",
                tool_name="summarize_job_search",
                tool_input={},
                tool_output_summary=f"Total jobs: {sum_out.get('total_available_opportunities')}, saved: {sum_out.get('total_saved')}.",
                execution_time_ms=round((time.time() - t0) * 1000, 2)
            ))
            tools_used.append("summarize_job_search")

            final_text = (
                f"I am CareerMatch AI, your career intelligence agent. "
                f"The platform currently tracks **{sum_out.get('total_available_opportunities')} active technical listings**.\n\n"
                f"You can prompt me to:\n"
                f"- *'Find the top jobs for my profile and rank them'*\n"
                f"- *'Compare my saved jobs and show tradeoffs'*\n"
                f"- *'Identify my biggest skill gaps and build a learning roadmap'*\n"
                f"- *'Prepare an application checklist and interview questions for this role'*"
            )

        return AgentRunResponse(
            response=final_text,
            steps=steps,
            tools_used=tools_used,
            evidence_citations=[],
            completed=True,
        )
