from typing import Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.schemas.agent import AgentRunRequest, AgentRunResponse
from app.rag.assistant import RAGCareerAssistant
from app.agent.orchestrator import CareerAgentOrchestrator
from app.auth.dependencies import get_current_user_optional

router = APIRouter(prefix="/agent", tags=["AI Career Assistant & Agentic Workflows"])

@router.post("/chat")
def chat_with_assistant(
    req: AgentRunRequest,
    current_user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    user_id = current_user.id if current_user else 1
    rag = RAGCareerAssistant(db)
    result = rag.answer_query(
        query=req.message,
        user_id=user_id,
        context_job_id=req.context_job_id
    )
    return result

@router.post("/run", response_model=AgentRunResponse)
def execute_agent_workflow(
    req: AgentRunRequest,
    current_user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    user_id = current_user.id if current_user else 1
    orchestrator = CareerAgentOrchestrator(db, user_id)
    return orchestrator.run_agent(req.message, req.context_job_id)

@router.get("/tools")
def list_available_tools():
    return {
        "tools": [
            {"name": "search_jobs", "description": "Search opportunities by text query, skill overlap, and remote filters."},
            {"name": "retrieve_candidate_profile", "description": "Fetch structured candidate skills, education, and seniority."},
            {"name": "get_job_details", "description": "Retrieve full requirements, responsibilities, and salary for a job."},
            {"name": "compare_jobs", "description": "Perform multi-attribute comparison between multiple job listings."},
            {"name": "analyze_job_match", "description": "Calculate granular 5-signal match score and grounded evidence breakdown."},
            {"name": "identify_skill_gaps", "description": "Aggregate missing market skills across target positions."},
            {"name": "recommend_learning_priorities", "description": "Generate prioritized project roadmap for missing skills."},
            {"name": "save_job", "description": "Add a job to the candidate's tracked application list."},
            {"name": "update_job_status", "description": "Transition application stage (saved, applied, interview, offer, rejected)."},
            {"name": "retrieve_saved_jobs", "description": "List all active tracked applications with status notes."},
            {"name": "generate_application_checklist", "description": "Create tailored checklist for target company and role."},
            {"name": "prepare_resume_customization_suggestions", "description": "Produce evidence-grounded resume tailoring recommendations."},
            {"name": "generate_interview_questions", "description": "Synthesize technical and behavioral questions for the role."},
            {"name": "summarize_job_search", "description": "Generate high-level overview of available jobs and application pipeline."}
        ]
    }
