import React, { useEffect, useState } from 'react';
import {
  X,
  Building2,
  MapPin,
  DollarSign,
  Briefcase,
  ExternalLink,
  Bookmark,
  CheckCircle2,
  AlertTriangle,
  Sparkles,
  ThumbsUp,
  ThumbsDown,
  Bot,
} from 'lucide-react';
import { Job, MatchSignalBreakdown } from '../types';
import { getMatchBreakdown, saveJobToTracker, updateApplicationStatus, recordJobFeedback } from '../api';

interface JobDetailModalProps {
  job: Job | null;
  onClose: () => void;
  onOpenAgentWithJob?: (jobId: number) => void;
}

export const JobDetailModal: React.FC<JobDetailModalProps> = ({ job, onClose, onOpenAgentWithJob }) => {
  const [match, setMatch] = useState<MatchSignalBreakdown | null>(null);
  const [loading, setLoading] = useState(false);
  const [actionMessage, setActionMessage] = useState<string | null>(null);

  useEffect(() => {
    if (job) {
      setLoading(true);
      getMatchBreakdown(job.id)
        .then((data) => setMatch(data))
        .catch((err) => console.error(err))
        .finally(() => setLoading(false));
    }
  }, [job]);

  if (!job) return null;

  const handleSave = async (status = 'saved') => {
    try {
      await saveJobToTracker(job.id, status);
      setActionMessage(`Job marked as ${status}!`);
      setTimeout(() => setActionMessage(null), 3000);
    } catch (e) {
      console.error(e);
    }
  };

  const handleFeedback = async (feedback: string) => {
    try {
      await recordJobFeedback(job.id, feedback);
      setActionMessage(`Preference recorded: ${feedback}`);
      setTimeout(() => setActionMessage(null), 3000);
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div className="fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center p-4 overflow-y-auto">
      <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-3xl w-full max-h-[90vh] flex flex-col shadow-2xl overflow-hidden animate-in fade-in zoom-in-95 duration-150">
        {/* Header */}
        <div className="p-6 border-b border-slate-800 flex items-start justify-between bg-slate-900/50">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                {job.remote_status.toUpperCase()}
              </span>
              <span className="px-2.5 py-0.5 rounded-full text-xs font-medium bg-slate-800 text-slate-300">
                {job.experience_level.toUpperCase()}
              </span>
            </div>
            <h2 className="text-xl font-bold text-white tracking-tight">{job.title}</h2>
            <div className="flex flex-wrap items-center gap-4 text-xs text-slate-400 mt-2">
              <div className="flex items-center gap-1">
                <Building2 className="w-3.5 h-3.5 text-slate-400" />
                <span className="font-semibold text-slate-200">{job.company}</span>
              </div>
              <div className="flex items-center gap-1">
                <MapPin className="w-3.5 h-3.5 text-slate-400" />
                <span>{job.location}</span>
              </div>
              {(job.min_salary || job.max_salary) && (
                <div className="flex items-center gap-1 text-emerald-400 font-mono font-medium">
                  <DollarSign className="w-3.5 h-3.5" />
                  <span>
                    ${(job.min_salary || 0).toLocaleString()} - ${(job.max_salary || 0).toLocaleString()} {job.currency}
                  </span>
                </div>
              )}
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Action message banner */}
        {actionMessage && (
          <div className="bg-emerald-500/10 border-b border-emerald-500/20 px-6 py-2 text-xs text-emerald-400 flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4" />
            <span>{actionMessage}</span>
          </div>
        )}

        {/* Content Body */}
        <div className="p-6 overflow-y-auto space-y-6 flex-1">
          {/* Match Intelligence Breakdown */}
          {match && (
            <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800 space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Sparkles className="w-4 h-4 text-emerald-400" />
                  <h3 className="text-sm font-semibold text-slate-200">Grounded Match Intelligence</h3>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-xs text-slate-400">Composite Fit:</span>
                  <span className="px-2.5 py-1 rounded-md bg-emerald-500/20 text-emerald-300 font-bold text-sm font-mono">
                    {match.composite_score}%
                  </span>
                </div>
              </div>

              {/* 5-Signal Progress Bars */}
              <div className="grid grid-cols-2 sm:grid-cols-5 gap-3 pt-2">
                {[
                  { label: 'Semantic', score: match.semantic_score * 100 },
                  { label: 'Skills', score: match.skill_overlap_score * 100 },
                  { label: 'Experience', score: match.experience_score * 100 },
                  { label: 'Education', score: match.education_score * 100 },
                  { label: 'Preferences', score: match.preference_score * 100 },
                ].map((sig) => (
                  <div key={sig.label} className="bg-slate-900/80 p-2.5 rounded-lg border border-slate-800/80">
                    <div className="text-[11px] text-slate-400 flex justify-between">
                      <span>{sig.label}</span>
                      <span className="font-mono text-slate-200">{Math.round(sig.score)}%</span>
                    </div>
                    <div className="w-full bg-slate-800 h-1.5 rounded-full mt-1.5 overflow-hidden">
                      <div
                        className="bg-emerald-400 h-full rounded-full transition-all duration-300"
                        style={{ width: `${Math.min(100, sig.score)}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>

              <p className="text-xs text-slate-300 italic bg-slate-900/40 p-2.5 rounded-lg border border-slate-800/40">
                "{match.explanation_summary}"
              </p>

              {/* Matched vs Missing Skills Badges */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2">
                <div>
                  <div className="text-xs font-semibold text-emerald-400 mb-2 flex items-center gap-1.5">
                    <CheckCircle2 className="w-3.5 h-3.5" />
                    <span>Confirmed Profile Strengths ({match.matched_skills.length})</span>
                  </div>
                  <div className="flex flex-wrap gap-1.5">
                    {match.matched_skills.map((s) => (
                      <span key={s} className="px-2 py-0.5 rounded text-xs bg-emerald-500/10 text-emerald-300 border border-emerald-500/20">
                        {s}
                      </span>
                    ))}
                    {match.matched_skills.length === 0 && (
                      <span className="text-xs text-slate-500">No direct explicit skill overlap</span>
                    )}
                  </div>
                </div>

                <div>
                  <div className="text-xs font-semibold text-amber-400 mb-2 flex items-center gap-1.5">
                    <AlertTriangle className="w-3.5 h-3.5" />
                    <span>Missing Market Skills ({match.missing_skills.length})</span>
                  </div>
                  <div className="flex flex-wrap gap-1.5">
                    {match.missing_skills.map((s) => (
                      <span key={s} className="px-2 py-0.5 rounded text-xs bg-amber-500/10 text-amber-300 border border-amber-500/20">
                        {s}
                      </span>
                    ))}
                    {match.missing_skills.length === 0 && (
                      <span className="text-xs text-emerald-400">All required skills covered!</span>
                    )}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Job Description */}
          <div>
            <h3 className="text-sm font-semibold text-white mb-2">Role Overview</h3>
            <p className="text-sm text-slate-300 leading-relaxed whitespace-pre-line">{job.description}</p>
          </div>

          {/* Responsibilities */}
          {job.responsibilities && job.responsibilities.length > 0 && (
            <div>
              <h3 className="text-sm font-semibold text-white mb-2">Key Responsibilities</h3>
              <ul className="space-y-1.5 text-sm text-slate-300">
                {job.responsibilities.map((r, i) => (
                  <li key={i} className="flex items-start gap-2">
                    <span className="text-emerald-400 font-bold">•</span>
                    <span>{r}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Qualifications */}
          {job.required_qualifications && job.required_qualifications.length > 0 && (
            <div>
              <h3 className="text-sm font-semibold text-white mb-2">Required Qualifications</h3>
              <ul className="space-y-1.5 text-sm text-slate-300">
                {job.required_qualifications.map((q, i) => (
                  <li key={i} className="flex items-start gap-2">
                    <span className="text-emerald-400 font-bold">•</span>
                    <span>{q}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>

        {/* Footer Actions */}
        <div className="p-5 border-t border-slate-800 bg-slate-900/60 flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center gap-2">
            <span className="text-xs text-slate-400 mr-1">Feedback:</span>
            <button
              onClick={() => handleFeedback('interested')}
              title="Train recommendation memory (Interested)"
              className="p-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-emerald-400 transition"
            >
              <ThumbsUp className="w-4 h-4" />
            </button>
            <button
              onClick={() => handleFeedback('not_interested')}
              title="Dismiss / Less like this"
              className="p-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-rose-400 transition"
            >
              <ThumbsDown className="w-4 h-4" />
            </button>
          </div>

          <div className="flex items-center gap-2">
            {onOpenAgentWithJob && (
              <button
                onClick={() => {
                  onClose();
                  onOpenAgentWithJob(job.id);
                }}
                className="flex items-center gap-1.5 px-3.5 py-2 rounded-lg bg-indigo-600/20 text-indigo-300 border border-indigo-500/30 hover:bg-indigo-600/30 text-xs font-semibold transition"
              >
                <Bot className="w-4 h-4" />
                <span>Ask AI About Role</span>
              </button>
            )}

            <button
              onClick={() => handleSave('saved')}
              className="flex items-center gap-1.5 px-3.5 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold border border-slate-700 transition"
            >
              <Bookmark className="w-4 h-4" />
              <span>Save Job</span>
            </button>

            <button
              onClick={() => handleSave('applied')}
              className="flex items-center gap-1.5 px-4 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold transition shadow-md shadow-emerald-600/20"
            >
              <CheckCircle2 className="w-4 h-4" />
              <span>Mark as Applied</span>
            </button>

            {job.application_url && (
              <a
                href={job.application_url}
                target="_blank"
                rel="noreferrer"
                className="flex items-center gap-1.5 px-3.5 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium border border-slate-700 transition"
              >
                <ExternalLink className="w-4 h-4" />
                <span>Apply Externally</span>
              </a>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
