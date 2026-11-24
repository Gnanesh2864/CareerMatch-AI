import React, { useState, useEffect } from 'react';
import {
  Zap,
  CheckCircle2,
  AlertTriangle,
  HelpCircle,
  TrendingUp,
  Map,
  Building2,
  Calendar,
  Briefcase,
} from 'lucide-react';
import { getSkillGapAnalysis } from '../api';

interface SkillGapData {
  demonstrated_skills: any[];
  weak_evidence_skills: any[];
  high_priority_gaps: any[];
  optional_gaps: any[];
  roadmap: any[];
  total_jobs_analyzed: number;
}

export const SkillIntelligence: React.FC = () => {
  const [data, setData] = useState<SkillGapData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const res = await getSkillGapAnalysis();
      setData(res);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading || !data) {
    return <div className="p-12 text-center text-slate-400">Analyzing market skill distribution...</div>;
  }

  return (
    <div className="space-y-8 animate-in fade-in duration-200">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-black text-white tracking-tight">Skill Gap Intelligence & Market Analysis</h1>
        <p className="text-xs text-slate-400 mt-1">
          Empirical comparison of your profile against <strong className="text-white">{data.total_jobs_analyzed} active engineering listings</strong>.
        </p>
      </div>

      {/* 4-Category Breakdown Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Demonstrated */}
        <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-emerald-400 flex items-center gap-1.5">
              <CheckCircle2 className="w-4 h-4" />
              <span>Demonstrated</span>
            </span>
            <span className="text-xs font-mono font-bold bg-emerald-500/10 text-emerald-300 px-2 py-0.5 rounded">
              {data.demonstrated_skills.length}
            </span>
          </div>
          <p className="text-[11px] text-slate-400">Explicitly confirmed qualifications in your resume.</p>
          <div className="flex flex-wrap gap-1.5 pt-1">
            {data.demonstrated_skills.map((s) => (
              <span key={s.skill} className="px-2.5 py-1 rounded-lg text-xs bg-emerald-500/10 text-emerald-300 border border-emerald-500/20">
                {s.skill}
              </span>
            ))}
          </div>
        </div>

        {/* Weak Evidence */}
        <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-indigo-400 flex items-center gap-1.5">
              <HelpCircle className="w-4 h-4" />
              <span>Weak Evidence</span>
            </span>
            <span className="text-xs font-mono font-bold bg-indigo-500/10 text-indigo-300 px-2 py-0.5 rounded">
              {data.weak_evidence_skills.length}
            </span>
          </div>
          <p className="text-[11px] text-slate-400">Inferred from project context; lacks explicit bullet points.</p>
          <div className="flex flex-wrap gap-1.5 pt-1">
            {data.weak_evidence_skills.map((s) => (
              <span key={s.skill} className="px-2.5 py-1 rounded-lg text-xs bg-indigo-500/10 text-indigo-300 border border-indigo-500/20">
                {s.skill}
              </span>
            ))}
          </div>
        </div>

        {/* High Priority Gaps */}
        <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-rose-400 flex items-center gap-1.5">
              <AlertTriangle className="w-4 h-4" />
              <span>High Priority Gaps</span>
            </span>
            <span className="text-xs font-mono font-bold bg-rose-500/10 text-rose-300 px-2 py-0.5 rounded">
              {data.high_priority_gaps.length}
            </span>
          </div>
          <p className="text-[11px] text-slate-400">Required across multiple listings in your target domain.</p>
          <div className="flex flex-wrap gap-1.5 pt-1">
            {data.high_priority_gaps.map((s) => (
              <span key={s.skill} className="px-2.5 py-1 rounded-lg text-xs bg-rose-500/10 text-rose-300 border border-rose-500/20">
                {s.skill} ({s.market_demand_count}x)
              </span>
            ))}
          </div>
        </div>

        {/* Optional / Specialized */}
        <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-slate-300 flex items-center gap-1.5">
              <TrendingUp className="w-4 h-4 text-slate-400" />
              <span>Specialized Skills</span>
            </span>
            <span className="text-xs font-mono font-bold bg-slate-800 text-slate-300 px-2 py-0.5 rounded">
              {data.optional_gaps.length}
            </span>
          </div>
          <p className="text-[11px] text-slate-400">Preferred skills for specialized sub-fields.</p>
          <div className="flex flex-wrap gap-1.5 pt-1">
            {data.optional_gaps.map((s) => (
              <span key={s.skill} className="px-2.5 py-1 rounded-lg text-xs bg-slate-800 text-slate-300">
                {s.skill}
              </span>
            ))}
          </div>
        </div>
      </div>

      {/* Actionable Learning & Preparation Roadmap */}
      <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 space-y-6">
        <div>
          <h2 className="text-lg font-bold text-white flex items-center gap-2">
            <Map className="w-5 h-5 text-emerald-400" />
            <span>Targeted Preparation Roadmap</span>
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Structured roadmap prioritizing highest-impact market competencies.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {data.roadmap.map((item) => (
            <div key={item.step} className="p-5 rounded-xl bg-slate-950/70 border border-slate-800 space-y-3 relative overflow-hidden">
              <div className="flex items-center justify-between">
                <span className="text-xs font-mono font-bold text-emerald-400">
                  PHASE {item.step}
                </span>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-300 border border-emerald-500/20">
                  {item.milestone}
                </span>
              </div>
              <h3 className="text-base font-bold text-white">Master {item.skill}</h3>
              <p className="text-xs text-slate-300 leading-relaxed">{item.action}</p>
              <div className="text-[11px] text-slate-400 border-t border-slate-800/80 pt-2 font-medium">
                {item.market_impact}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
