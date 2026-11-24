import axios from 'axios';
import {
  Job,
  HybridSearchResponse,
  CandidateProfileSchema,
  TrackedApplication,
  TrackerAnalytics,
  AgentRunResponse,
  EvaluationReport,
  MatchSignalBreakdown,
} from './types';

const api = axios.create({
  baseURL: '/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
});

export const getJobs = async (params: { keyword?: string; remote_status?: string; experience_level?: string; location?: string } = {}) => {
  const res = await api.get<Job[]>('/jobs', { params });
  return res.data;
};

export const getJobById = async (id: number) => {
  const res = await api.get<Job>(`/jobs/${id}`);
  return res.data;
};

export const triggerIngestion = async () => {
  const res = await api.post('/jobs/ingest');
  return res.data;
};

export const hybridSearch = async (payload: {
  query_text: string;
  alpha: number;
  top_k?: number;
  remote_status?: string;
  experience_level?: string;
  location?: string;
  min_salary?: number;
  rerank?: boolean;
}) => {
  const res = await api.post<HybridSearchResponse>('/search/hybrid', payload);
  return res.data;
};

export const getMatchBreakdown = async (jobId: number) => {
  const res = await api.get<MatchSignalBreakdown>(`/search/match/${jobId}`);
  return res.data;
};

export const getProfile = async () => {
  const res = await api.get<CandidateProfileSchema>('/resume/profile');
  return res.data;
};

export const updateProfile = async (profile: CandidateProfileSchema) => {
  const res = await api.put<CandidateProfileSchema>('/resume/profile', profile);
  return res.data;
};

export const uploadResume = async (file: File) => {
  const formData = new FormData();
  formData.append('file', file);
  const res = await api.post('/resume/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return res.data;
};

export const runAgentWorkflow = async (message: string, contextJobId?: number) => {
  const res = await api.post<AgentRunResponse>('/agent/run', {
    message,
    context_job_id: contextJobId,
  });
  return res.data;
};

export const chatAssistant = async (message: string, contextJobId?: number) => {
  const res = await api.post<{ answer: string; citations: any[]; model: string }>('/agent/chat', {
    message,
    context_job_id: contextJobId,
  });
  return res.data;
};

export const getTrackedApplications = async () => {
  const res = await api.get<TrackedApplication[]>('/tracker');
  return res.data;
};

export const saveJobToTracker = async (jobId: number, status = 'saved') => {
  const res = await api.post(`/tracker/${jobId}`, null, { params: { status } });
  return res.data;
};

export const updateApplicationStatus = async (jobId: number, status: string, notes?: string) => {
  const res = await api.put(`/tracker/${jobId}/status`, { status, notes });
  return res.data;
};

export const recordJobFeedback = async (jobId: number, feedback: string) => {
  const res = await api.post(`/tracker/${jobId}/feedback`, { feedback });
  return res.data;
};

export const getTrackerAnalytics = async () => {
  const res = await api.get<TrackerAnalytics>('/tracker/analytics');
  return res.data;
};

export const getSkillGapAnalysis = async (jobId?: number) => {
  const res = await api.get('/skills/gap-analysis', { params: { job_id: jobId } });
  return res.data;
};

export const runEvaluationBenchmark = async (k = 5) => {
  const res = await api.post<EvaluationReport>('/evaluation/run', null, { params: { k } });
  return res.data;
};

export const getLatestEvaluationReport = async () => {
  const res = await api.get<EvaluationReport>('/evaluation/latest');
  return res.data;
};

export default api;
