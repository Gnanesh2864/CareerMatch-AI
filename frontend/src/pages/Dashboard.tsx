import React, { useEffect, useState } from 'react';
import {
  Sparkles,
  Search,
  Briefcase,
  TrendingUp,
  Bookmark,
  Send,
  Calendar,
  CheckCircle,
  ArrowRight,
  Bot,
  Zap,
} from 'lucide-react';
import { RankedJobMatch, TrackerAnalytics, CandidateProfileSchema } from '../types';
import { hybridSearch, getTrackerAnalytics, getProfile } from '../api';

interface DashboardProps {
  onSelectJob: (jobId: number) => void;
  onNavigate: (tab: string) => void;
}

export const Dashboard: React.FC<DashboardProps> = ({ onSelectJob, onNavigate }) => {
  const [recommendations, setRecommendations] = useState<RankedJobMatch[]>([]);
  const [analytics, setAnalytics] = useState<TrackerAnalytics | null>(null);
  const [profile, setProfile] = useState<CandidateProfileSchema | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadDashboardData = async () => {
      try {
        setLoading(true);
        const [recsData, analyticsData, profileData] = await Promise.all([
          hybridSearch({ query_text: '', alpha: 0.6, top_k: 4, rerank: true }),
          getTrackerAnalytics(),
          getProfile(),
        ]);
        setRecommendations(recsData.results);
        setAnalytics(analyticsData);
        setProfile(profileData);
      } catch (err) {
        console.error('Error loading dashboard data:', err);
      } finally {
        setLoading(false);
      }
    };
    loadDashboardData();
  }, []);

  return (
    <div className="space-y-8 animate-in fade-in duration-200">
      {/* Hero Welcome Banner */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-slate-900 via-slate-900 to-emerald-950/40 border border-slate-800 p-8 shadow-xl">
        <div className="relative z-10 max-w-2xl">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-semibold mb-4">
            <Sparkles className="w-3.5 h-3.5" />
            <span>AI Career Agent Active & Synced</span>
          </div>
          <h1 className="text-3xl font-extrabold text-white tracking-tight">
            Welcome back, {profile?.full_name || 'Candidate'}
          </h1>
          <p className="text-slate-400 text-sm mt-2 leading-relaxed">
            CareerMatch AI has continuously indexed verified engineering roles, aligned your 
            qualifications via dense embeddings, and analyzed market skill demands.
          </p>
          <div className="flex flex-wrap gap-3 mt-6">
            <button
              onClick={() => onNavigate('search')}
              className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-semibold text-xs transition shadow-lg shadow-emerald-600/20"
            >
              <Search className="w-4 h-4" />
              <span>Explore Hybrid Search</span>
            </button>
            <button
              onClick={() => onNavigate('assistant')}
              className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 font-semibold text-xs border border-slate-700 transition"
            >
              <Bot className="w-4 h-4 text-emerald-400" />
              <span>Launch Autonomous Agent</span>
            </button>
          </div>
        </div>
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          {
            label: 'Tracked Jobs',
            value: analytics?.total_tracked || 0,
            icon: Bookmark,
            color: 'text-indigo-400',
            bg: 'bg-indigo-500/10 border-indigo-500/20',
          },
          {
            label: 'Applications Submitted',
            value: analytics?.status_funnel.applied || 0,
            icon: Send,
            color: 'text-emerald-400',
            bg: 'bg-emerald-500/10 border-emerald-500/20',
          },
          {
            label: 'Interviews & Screenings',
            value: analytics?.status_funnel.interview || 0,
            icon: Calendar,
            color: 'text-amber-400',
            bg: 'bg-amber-500/10 border-amber-500/20',
          },
          {
            label: 'Verified Skills',
            value: profile?.skills.length || 0,
            icon: Zap,
            color: 'text-teal-400',
            bg: 'bg-teal-500/10 border-teal-500/20',
          },
        ].map((m) => {
          const Icon = m.icon;
          return (
            <div key={m.label} className="p-5 rounded-xl bg-slate-900 border border-slate-800 shadow-sm flex items-center gap-4">
              <div className={`p-3 rounded-lg border ${m.bg}`}>
                <Icon className={`w-5 h-5 ${m.color}`} />
              </div>
              <div>
                <div className="text-2xl font-extrabold text-white font-mono">{m.value}</div>
                <div className="text-xs text-slate-400 font-medium">{m.label}</div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Main Grid: Personalized Recommendations + Skill Intelligence Snapshot */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Ranked Recommendations */}
        <div className="lg:col-span-2 space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-lg font-bold text-white tracking-tight">Top Ranked Opportunities</h2>
              <p className="text-xs text-slate-400">Scored via multi-signal reranking against your profile</p>
            </div>
            <button
              onClick={() => onNavigate('search')}
              className="text-xs font-semibold text-emerald-400 hover:text-emerald-300 flex items-center gap-1 transition"
            >
              <span>View all</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>

          <div className="space-y-3">
            {recommendations.map((item) => (
              <div
                key={item.job.id}
                onClick={() => onSelectJob(item.job.id)}
                className="p-5 rounded-xl bg-slate-900/90 border border-slate-800 hover:border-slate-700 transition cursor-pointer hover:shadow-lg group flex flex-col sm:flex-row sm:items-center justify-between gap-4"
              >
                <div className="space-y-1.5 flex-1">
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">{item.job.company}</span>
                    <span className="text-slate-600">•</span>
                    <span className="text-xs text-slate-400">{item.job.location}</span>
                    <span className="px-2 py-0.5 rounded text-[10px] font-mono font-medium bg-slate-800 text-slate-300">
                      {item.job.remote_status}
                    </span>
                  </div>
                  <h3 className="text-base font-bold text-white group-hover:text-emerald-400 transition">
                    {item.job.title}
                  </h3>
                  <div className="flex flex-wrap gap-1.5 pt-1">
                    {item.job.skills.slice(0, 4).map((s) => (
                      <span key={s} className="px-2 py-0.5 rounded text-[11px] bg-slate-800 text-slate-300">
                        {s}
                      </span>
                    ))}
                  </div>
                </div>

                <div className="flex items-center sm:flex-col items-end justify-between sm:justify-center border-t sm:border-t-0 pt-3 sm:pt-0 border-slate-800 shrink-0">
                  <div className="text-right">
                    <div className="text-2xl font-black text-emerald-400 font-mono">
                      {item.match.composite_score}%
                    </div>
                    <div className="text-[10px] text-slate-500 font-medium">Match Fit</div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Sidebar Snapshot: Profile Competencies & Quick Agent Action */}
        <div className="space-y-6">
          <div className="p-6 rounded-xl bg-slate-900 border border-slate-800 space-y-4">
            <h3 className="text-sm font-bold text-white flex items-center gap-2">
              <Zap className="w-4 h-4 text-emerald-400" />
              <span>Extracted Competencies</span>
            </h3>
            <p className="text-xs text-slate-400">
              Verified skills parsed directly from your uploaded resume.
            </p>
            <div className="flex flex-wrap gap-1.5 pt-2">
              {profile?.skills.slice(0, 10).map((s) => (
                <span
                  key={s.name}
                  className={`px-2.5 py-1 rounded-md text-xs font-medium border ${
                    s.is_explicit
                      ? 'bg-emerald-500/10 text-emerald-300 border-emerald-500/20'
                      : 'bg-indigo-500/10 text-indigo-300 border-indigo-500/20'
                  }`}
                >
                  {s.name}
                </span>
              ))}
            </div>
            <button
              onClick={() => onNavigate('profile')}
              className="w-full mt-2 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-slate-300 transition border border-slate-700"
            >
              Edit Profile & Upload Resume
            </button>
          </div>

          <div className="p-6 rounded-xl bg-gradient-to-b from-indigo-950/40 to-slate-900 border border-indigo-900/40 space-y-3">
            <div className="flex items-center gap-2 text-indigo-400 font-bold text-sm">
              <Bot className="w-4 h-4" />
              <span>Autonomous Career Agent</span>
            </div>
            <p className="text-xs text-slate-300 leading-relaxed">
              Let the multi-step agent compare your saved jobs, identify market gaps, and prepare custom interview prep plans using 14 approved tools.
            </p>
            <button
              onClick={() => onNavigate('assistant')}
              className="w-full py-2.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold transition shadow-md shadow-indigo-600/20 flex items-center justify-center gap-2"
            >
              <span>Ask Career Agent</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
