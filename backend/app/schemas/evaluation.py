from typing import List, Dict, Any, Optional
from pydantic import BaseModel

class RetrievalMetrics(BaseModel):
    precision_at_k: float
    recall_at_k: float
    mrr: float
    ndcg_at_k: float
    latency_ms: float

class MethodComparisonMetrics(BaseModel):
    keyword: RetrievalMetrics
    semantic: RetrievalMetrics
    hybrid: RetrievalMetrics
    hybrid_rerank: RetrievalMetrics

class RAGMetrics(BaseModel):
    groundedness_score: float      # 0.0 - 1.0 (proportion of claims supported by retrieved context)
    citation_accuracy: float       # 0.0 - 1.0 (validity of reference links)
    answer_relevance: float        # 0.0 - 1.0 (relevance of generated response to user prompt)
    hallucination_rate: float      # 0.0 - 1.0 (unsupported claims rate)
    avg_latency_ms: float

class AgentMetrics(BaseModel):
    task_completion_rate: float    # 0.0 - 1.0
    tool_selection_accuracy: float # 0.0 - 1.0
    tool_failure_rate: float       # 0.0 - 1.0
    avg_steps_per_task: float
    avg_latency_ms: float

class EvaluationReport(BaseModel):
    experiment_id: str
    dataset_name: str
    total_benchmark_queries: int
    retrieval_comparison: MethodComparisonMetrics
    rag_metrics: RAGMetrics
    agent_metrics: AgentMetrics
    summary: str
    timestamp: str
