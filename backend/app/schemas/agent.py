from typing import List, Optional, Dict, Any
from pydantic import BaseModel

class ToolExecutionRequest(BaseModel):
    tool_name: str
    parameters: Dict[str, Any] = {}

class ToolExecutionResponse(BaseModel):
    tool_name: str
    success: bool
    output: Any
    error: Optional[str] = None

class AgentStepTrace(BaseModel):
    step_number: int
    thought: str
    tool_name: str
    tool_input: Dict[str, Any]
    tool_output_summary: str
    execution_time_ms: float

class AgentRunRequest(BaseModel):
    message: str
    context_job_id: Optional[int] = None
    session_id: Optional[str] = None

class AgentRunResponse(BaseModel):
    response: str
    steps: List[AgentStepTrace] = []
    tools_used: List[str] = []
    evidence_citations: List[Dict[str, Any]] = []
    completed: bool = True
