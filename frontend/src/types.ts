export interface Job {
  id: number;
  title: string;
  company: string;
  description: string;
  responsibilities: string[];
  required_qualifications: string[];
  preferred_qualifications: string[];
  skills: string[];
  experience_level: string;
  employment_type: string;
  min_salary?: number;
  max_salary?: number;
  currency: string;
  location: string;
  remote_status: string;
  application_url?: string;
  source: string;
  posting_date: string;
  created_at: string;
}

export interface MatchSignalBreakdown {
  semantic_score: number;
  skill_overlap_score: number;
  experience_score: number;
  education_score: number;
  preference_score: number;
  composite_score: number;
  matched_skills: string[];
  missing_skills: string[];
  partial_skills: string[];
  strengths: string[];
  gaps: string[];
  preference_alignment: string[];
  explanation_summary: string;
}

export interface RankedJobMatch {
  job: Job;
  match: MatchSignalBreakdown;
}

export interface HybridSearchResponse {
  results: RankedJobMatch[];
  total_matches: number;
  retrieval_method: string;
  execution_time_ms: number;
  alpha: number;
}

export interface CandidateSkill {
  name: string;
  category: string;
  is_explicit: boolean;
  years_experience?: number;
  confidence: number;
}

export interface CandidateExperience {
  company: string;
  role: string;
  location?: string;
  start_date?: string;
  end_date?: string;
  is_current: boolean;
  description: string;
  technologies: string[];
}

export interface CandidateEducation {
  institution: string;
  degree: string;
  field_of_study?: string;
  graduation_year?: number;
  gpa?: number;
}

export interface CandidateProject {
  title: string;
  description: string;
  technologies: string[];
  url?: string;
}

export interface CandidateProfileSchema {
  full_name: string;
  email?: string;
  phone?: string;
  location?: string;
  summary: string;
  experience_level: string;
  total_years_experience: number;
  career_interests: string[];
  skills: CandidateSkill[];
  experience: CandidateExperience[];
  education: CandidateEducation[];
  projects: CandidateProject[];
}

export interface TrackedApplication {
  application_id: number;
  job_id: number;
  title: string;
  company: string;
  location: string;
  remote_status: string;
  experience_level: string;
  status: string; // saved, applied, interview, offer, rejected, closed
  feedback?: string;
  notes?: string;
  applied_date?: string;
  updated_at: string;
}

export interface TrackerAnalytics {
  total_tracked: number;
  status_funnel: {
    saved: number;
    applied: number;
    interview: number;
    offer: number;
    rejected: number;
    closed: number;
  };
  feedback_metrics: {
    interested: number;
    not_interested: number;
  };
  response_rate: number;
}

export interface AgentStepTrace {
  step_number: number;
  thought: string;
  tool_name: string;
  tool_input: Record<string, any>;
  tool_output_summary: string;
  execution_time_ms: number;
}

export interface AgentRunResponse {
  response: string;
  steps: AgentStepTrace[];
  tools_used: string[];
  evidence_citations: any[];
  completed: boolean;
}

export interface RetrievalMetrics {
  precision_at_k: number;
  recall_at_k: number;
  mrr: number;
  ndcg_at_k: number;
  latency_ms: number;
}

export interface EvaluationReport {
  experiment_id: string;
  dataset_name: string;
  total_benchmark_queries: number;
  retrieval_comparison: {
    keyword: RetrievalMetrics;
    semantic: RetrievalMetrics;
    hybrid: RetrievalMetrics;
    hybrid_rerank: RetrievalMetrics;
  };
  rag_metrics: {
    groundedness_score: number;
    citation_accuracy: number;
    answer_relevance: number;
    hallucination_rate: number;
    avg_latency_ms: number;
  };
  agent_metrics: {
    task_completion_rate: number;
    tool_selection_accuracy: number;
    tool_failure_rate: number;
    avg_steps_per_task: number;
    avg_latency_ms: number;
  };
  summary: string;
  timestamp: string;
}
