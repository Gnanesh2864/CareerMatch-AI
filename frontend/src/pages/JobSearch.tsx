import React, { useState, useEffect } from 'react';
import {
  Search as SearchIcon,
  SlidersHorizontal,
  Sparkles,
  Building2,
  MapPin,
  DollarSign,
  Filter,
  Layers,
  ArrowUpDown,
  Clock,
} from 'lucide-react';
import { RankedJobMatch } from '../types';
import { hybridSearch } from '../api';

interface JobSearchProps {
  onSelectJob: (jobId: number) => void;
}

export const JobSearch: React.FC<JobSearchProps> = ({ onSelectJob }) => {
  const [query, setQuery] = useState('');
  const [alpha, setAlpha] = useState(0.6);
  const [remoteStatus, setRemoteStatus] = useState('all');
  const [expLevel, setExpLevel] = useState('all');
  const [minSalary, setMinSalary] = useState<number | undefined>(undefined);
  const [rerank, setRerank] = useState(true);

  const [results, setResults] = useState<RankedJobMatch[]>([]);
  const [loading, setLoading] = useState(false);
  const [executionTime, setExecutionTime] = useState<number>(0);
  const [retrievalMethod, setRetrievalMethod] = useState('');

  const executeSearch = async () => {
    try {
      setLoading(true);
      const data = await hybridSearch({
        query_text: query,
        alpha: alpha,
        remote_status: remoteStatus === 'all' ? undefined : remoteStatus,
        experience_level: expLevel === 'all' ? undefined : expLevel,
        min_salary: minSalary,
        rerank: rerank,
        top_k: 20,
      });
      setResults(data.results);
      setExecutionTime(data.execution_time_ms);
      setRetrievalMethod(data.retrieval_method);
    } catch (err) {
      console.error('Error executing hybrid search:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    executeSearch();
  }, [alpha, remoteStatus, expLevel, rerank]);

  return (
    <div className="space-y-6 animate-in fade-in duration-200">
      {/* Header & Controls */}
      <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 space-y-6 shadow-xl">
        <div>
          <h1 className="text-2xl font-black text-white tracking-tight">Hybrid Career Search Engine</h1>
          <p className="text-xs text-slate-400 mt-1">
            Combines dense neural embeddings (<span className="text-emerald-400 font-mono">all-MiniLM-L6-v2</span>) 
            with BM25 keyword matching and explainable 5-signal reranking.
          </p>
        </div>

        {/* Search Bar */}
        <div className="flex gap-3">
          <div className="relative flex-1">
            <SearchIcon className="w-5 h-5 absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && executeSearch()}
              placeholder="e.g. Remote AI systems engineer involving PyTorch, RAG, and FastAPI..."
              className="w-full bg-slate-950 border border-slate-800 rounded-xl pl-11 pr-4 py-3 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-emerald-500 transition"
            />
          </div>
          <button
            onClick={executeSearch}
            disabled={loading}
            className="px-6 py-3 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-sm transition shadow-lg shadow-emerald-600/20 shrink-0"
          >
            {loading ? 'Retrieving...' : 'Search'}
          </button>
        </div>

        {/* Fusion Slider & Reranker Controls */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 pt-2 border-t border-slate-800/80">
          {/* Alpha Slider */}
          <div className="space-y-2 lg:col-span-2">
            <div className="flex justify-between items-center text-xs">
              <span className="font-semibold text-slate-300 flex items-center gap-1.5">
                <SlidersHorizontal className="w-3.5 h-3.5 text-emerald-400" />
                <span>Hybrid Fusion Balance (α: {alpha.toFixed(2)})</span>
              </span>
              <span className="text-[11px] font-mono text-emerald-400">
                {alpha === 0 ? 'Pure Keyword (BM25)' : alpha === 1 ? 'Pure Dense Vector' : `${Math.round((1-alpha)*100)}% BM25 / ${Math.round(alpha*100)}% Dense`}
              </span>
            </div>
            <input
              type="range"
              min="0"
              max="1"
              step="0.05"
              value={alpha}
              onChange={(e) => setAlpha(parseFloat(e.target.value))}
              className="w-full accent-emerald-500 bg-slate-800 h-2 rounded-lg cursor-pointer"
            />
            <div className="flex justify-between text-[10px] text-slate-500 font-mono">
              <span>0.0 (BM25 Lexical)</span>
              <span>0.5 (Balanced RRF)</span>
              <span>1.0 (Dense Semantic)</span>
            </div>
          </div>

          {/* Remote Filter */}
          <div className="space-y-1.5">
            <label className="text-xs font-semibold text-slate-300 flex items-center gap-1">
              <Filter className="w-3.5 h-3.5 text-slate-400" />
              <span>Remote Mode</span>
            </label>
            <select
              value={remoteStatus}
              onChange={(e) => setRemoteStatus(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-emerald-500"
            >
              <option value="all">All Modes</option>
              <option value="remote">Remote Only</option>
              <option value="hybrid">Hybrid</option>
              <option value="on-site">On-Site</option>
            </select>
          </div>

          {/* Experience Filter & Rerank Toggle */}
          <div className="space-y-1.5">
            <label className="text-xs font-semibold text-slate-300 flex items-center gap-1">
              <ArrowUpDown className="w-3.5 h-3.5 text-slate-400" />
              <span>Seniority Level</span>
            </label>
            <select
              value={expLevel}
              onChange={(e) => setExpLevel(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-emerald-500"
            >
              <option value="all">All Experience Levels</option>
              <option value="internship">Internship</option>
              <option value="entry">Entry Level (0-2 yrs)</option>
              <option value="mid">Mid Level (2-5 yrs)</option>
              <option value="senior">Senior (5+ yrs)</option>
              <option value="lead">Staff / Lead</option>
            </select>
          </div>
        </div>

        {/* Toggle Reranking & Stats */}
        <div className="flex flex-wrap items-center justify-between text-xs pt-3 border-t border-slate-800/60 text-slate-400">
          <label className="flex items-center gap-2 cursor-pointer select-none">
            <input
              type="checkbox"
              checked={rerank}
              onChange={(e) => setRerank(e.target.checked)}
              className="rounded bg-slate-800 border-slate-700 text-emerald-500 focus:ring-emerald-500/20"
            />
            <span className="text-slate-300 font-medium">Enable Multi-Signal Reranking (Skills + Exp + Education + Preferences)</span>
          </label>

          <div className="flex items-center gap-4 mt-2 sm:mt-0 font-mono text-[11px]">
            <div className="flex items-center gap-1.5">
              <Clock className="w-3.5 h-3.5 text-emerald-400" />
              <span>{executionTime}ms</span>
            </div>
            <div className="px-2 py-0.5 rounded bg-slate-800 text-slate-300">
              {retrievalMethod || 'Hybrid Engine'}
            </div>
          </div>
        </div>
      </div>

      {/* Results Header */}
      <div className="flex items-center justify-between text-xs text-slate-400 px-1">
        <span>Found <strong className="text-white">{results.length}</strong> matching positions</span>
        <span>Sorted by composite match score</span>
      </div>

      {/* Results List */}
      <div className="space-y-3">
        {results.map((item) => (
          <div
            key={item.job.id}
            onClick={() => onSelectJob(item.job.id)}
            className="p-6 rounded-2xl bg-slate-900 border border-slate-800 hover:border-emerald-500/50 hover:shadow-xl transition cursor-pointer group flex flex-col md:flex-row md:items-center justify-between gap-6"
          >
            <div className="space-y-2 flex-1">
              <div className="flex flex-wrap items-center gap-2">
                <span className="font-extrabold text-xs text-slate-300 uppercase tracking-wider">
                  {item.job.company}
                </span>
                <span className="text-slate-600">•</span>
                <span className="px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                  {item.job.remote_status.toUpperCase()}
                </span>
                <span className="px-2.5 py-0.5 rounded-full text-[11px] font-medium bg-slate-800 text-slate-300">
                  {item.job.experience_level.toUpperCase()}
                </span>
                {item.job.source && (
                  <span className="text-[10px] text-slate-500 font-mono">
                    via {item.job.source}
                  </span>
                )}
              </div>

              <h2 className="text-lg font-bold text-white group-hover:text-emerald-400 transition">
                {item.job.title}
              </h2>

              <p className="text-xs text-slate-400 line-clamp-2 leading-relaxed">
                {item.job.description}
              </p>

              <div className="flex flex-wrap items-center gap-4 text-xs text-slate-400 pt-1">
                <div className="flex items-center gap-1">
                  <MapPin className="w-3.5 h-3.5 text-slate-500" />
                  <span>{item.job.location}</span>
                </div>
                {(item.job.min_salary || item.job.max_salary) && (
                  <div className="flex items-center gap-1 text-emerald-400 font-mono font-medium">
                    <DollarSign className="w-3.5 h-3.5" />
                    <span>
                      ${(item.job.min_salary || 0).toLocaleString()} - ${(item.job.max_salary || 0).toLocaleString()}
                    </span>
                  </div>
                )}
              </div>

              <div className="flex flex-wrap gap-1.5 pt-2">
                {item.job.skills.map((s) => {
                  const isMatched = item.match.matched_skills.some(
                    (m) => m.toLowerCase() === s.toLowerCase()
                  );
                  return (
                    <span
                      key={s}
                      className={`px-2 py-0.5 rounded text-[11px] font-medium ${
                        isMatched
                          ? 'bg-emerald-500/10 text-emerald-300 border border-emerald-500/30'
                          : 'bg-slate-800 text-slate-400'
                      }`}
                    >
                      {s}
                    </span>
                  );
                })}
              </div>
            </div>

            {/* Score & Breakdown Callout */}
            <div className="flex md:flex-col items-center md:items-end justify-between border-t md:border-t-0 pt-4 md:pt-0 border-slate-800 shrink-0 gap-2">
              <div className="text-right">
                <div className="text-3xl font-black text-emerald-400 font-mono">
                  {item.match.composite_score}%
                </div>
                <div className="text-[10px] text-slate-500 font-medium">Match Fit</div>
              </div>

              <div className="text-right hidden sm:block">
                <span className="text-[11px] text-slate-400">
                  {item.match.matched_skills.length} of {item.job.skills.length} skills matched
                </span>
              </div>
            </div>
          </div>
        ))}
        {results.length === 0 && !loading && (
          <div className="text-center py-12 rounded-2xl bg-slate-900 border border-slate-800 text-slate-400">
            No matching opportunities found. Try adjusting your search query or filters.
          </div>
        )}
      </div>
    </div>
  );
};
