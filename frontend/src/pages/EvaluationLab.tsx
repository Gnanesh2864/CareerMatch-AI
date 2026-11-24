import React, { useState, useEffect } from 'react';
import {
  BarChart3,
  Play,
  CheckCircle2,
  Cpu,
  ShieldAlert,
  Zap,
  Clock,
  Layers,
  FileCode,
  Sparkles,
} from 'lucide-react';
import { EvaluationReport } from '../types';
import { runEvaluationBenchmark, getLatestEvaluationReport } from '../api';

export const EvaluationLab: React.FC = () => {
  const [report, setReport] = useState<EvaluationReport | null>(null);
  const [running, setRunning] = useState(false);
  const [kValue, setKValue] = useState(5);

  useEffect(() => {
    getLatestEvaluationReport()
      .then((data) => setReport(data))
      .catch((err) => console.error(err));
  }, []);

  const handleRun = async () => {
    try {
      setRunning(true);
      const data = await runEvaluationBenchmark(kValue);
      setReport(data);
    } catch (err) {
      console.error(err);
    } finally {
      setRunning(false);
    }
  };

  return (
    <div className="space-y-8 animate-in fade-in duration-200">
      {/* Header & Benchmark Controls */}
      <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 flex flex-wrap items-center justify-between gap-4 shadow-xl">
        <div>
          <div className="inline-flex items-center gap-2 px-2.5 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-semibold mb-2">
            <BarChart3 className="w-3.5 h-3.5" />
            <span>Information Retrieval & AI Evaluation Lab</span>
          </div>
          <h1 className="text-2xl font-black text-white tracking-tight">Empirical System Evaluation</h1>
          <p className="text-xs text-slate-400 mt-1">
            Reproducible IR benchmarks across Keyword (BM25), Semantic (all-MiniLM-L6-v2), Hybrid Fusion, and Multi-Signal Reranking.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-300 font-mono">
            <span>Rank Cutoff:</span>
            <select
              value={kValue}
              onChange={(e) => setKValue(parseInt(e.target.value))}
              className="bg-transparent text-emerald-400 font-bold focus:outline-none"
            >
              <option value="3">K=3</option>
              <option value="5">K=5</option>
              <option value="10">K=10</option>
            </select>
          </div>

          <button
            onClick={handleRun}
            disabled={running}
            className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs transition shadow-lg shadow-emerald-600/20 shrink-0"
          >
            <Play className={`w-3.5 h-3.5 ${running ? 'animate-spin' : ''}`} />
            <span>{running ? 'Running Benchmark...' : 'Run Live Benchmark'}</span>
          </button>
        </div>
      </div>

      {report && (
        <>
          {/* Retrieval Comparison Table */}
          <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 space-y-4">
            <div className="flex justify-between items-center">
              <div>
                <h2 className="text-base font-bold text-white">Retrieval Engine Benchmark Comparison</h2>
                <p className="text-xs text-slate-400">
                  Evaluated across {report.total_benchmark_queries} human-labeled gold queries against ground-truth graded relevance.
                </p>
              </div>
              <span className="text-xs font-mono text-emerald-400 bg-emerald-500/10 px-2.5 py-1 rounded-md border border-emerald-500/20">
                {report.dataset_name}
              </span>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead>
                  <tr className="border-b border-slate-800 text-slate-400 font-mono">
                    <th className="py-3 px-4 font-semibold">METHOD</th>
                    <th className="py-3 px-4 font-semibold">PRECISION@{kValue}</th>
                    <th className="py-3 px-4 font-semibold">RECALL@{kValue}</th>
                    <th className="py-3 px-4 font-semibold">MRR</th>
                    <th className="py-3 px-4 font-semibold">NDCG@{kValue}</th>
                    <th className="py-3 px-4 font-semibold">AVG LATENCY</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60 font-mono">
                  {[
                    { name: '1. Pure Keyword (BM25)', data: report.retrieval_comparison.keyword, best: false },
                    { name: '2. Pure Semantic (Dense)', data: report.retrieval_comparison.semantic, best: false },
                    { name: '3. Hybrid (BM25 + Dense RRF)', data: report.retrieval_comparison.hybrid, best: false },
                    { name: '4. Hybrid + Multi-Signal Rerank', data: report.retrieval_comparison.hybrid_rerank, best: true },
                  ].map((row) => (
                    <tr
                      key={row.name}
                      className={row.best ? 'bg-emerald-500/10 font-bold text-emerald-300' : 'text-slate-300 hover:bg-slate-800/40'}
                    >
                      <td className="py-3.5 px-4 font-sans font-medium">{row.name}</td>
                      <td className="py-3.5 px-4">{row.data.precision_at_k.toFixed(3)}</td>
                      <td className="py-3.5 px-4">{row.data.recall_at_k.toFixed(3)}</td>
                      <td className="py-3.5 px-4">{row.data.mrr.toFixed(3)}</td>
                      <td className="py-3.5 px-4 text-emerald-400 font-bold">{row.data.ndcg_at_k.toFixed(3)}</td>
                      <td className="py-3.5 px-4 text-slate-400">{row.data.latency_ms}ms</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <div className="p-3 bg-slate-950/60 rounded-xl border border-slate-800/80 text-xs text-slate-300 italic">
              <strong>Key IR Insight:</strong> {report.summary}
            </div>
          </div>

          {/* RAG & Agent Performance Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* RAG Metrics */}
            <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 space-y-4">
              <h3 className="text-sm font-bold text-white flex items-center gap-2">
                <ShieldAlert className="w-4 h-4 text-emerald-400" />
                <span>RAG Groundedness & Safety Evaluation</span>
              </h3>
              <div className="grid grid-cols-2 gap-3">
                <div className="p-3 rounded-xl bg-slate-950 border border-slate-800 space-y-1">
                  <div className="text-[11px] text-slate-400">Groundedness Score</div>
                  <div className="text-xl font-bold text-emerald-400 font-mono">
                    {(report.rag_metrics.groundedness_score * 100).toFixed(0)}%
                  </div>
                </div>
                <div className="p-3 rounded-xl bg-slate-950 border border-slate-800 space-y-1">
                  <div className="text-[11px] text-slate-400">Citation Accuracy</div>
                  <div className="text-xl font-bold text-emerald-400 font-mono">
                    {(report.rag_metrics.citation_accuracy * 100).toFixed(0)}%
                  </div>
                </div>
                <div className="p-3 rounded-xl bg-slate-950 border border-slate-800 space-y-1">
                  <div className="text-[11px] text-slate-400">Answer Relevance</div>
                  <div className="text-xl font-bold text-emerald-400 font-mono">
                    {(report.rag_metrics.answer_relevance * 100).toFixed(0)}%
                  </div>
                </div>
                <div className="p-3 rounded-xl bg-slate-950 border border-slate-800 space-y-1">
                  <div className="text-[11px] text-slate-400">Hallucination Rate</div>
                  <div className="text-xl font-bold text-rose-400 font-mono">
                    {(report.rag_metrics.hallucination_rate * 100).toFixed(0)}%
                  </div>
                </div>
              </div>
            </div>

            {/* Agent Workflows Metrics */}
            <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 space-y-4">
              <h3 className="text-sm font-bold text-white flex items-center gap-2">
                <Cpu className="w-4 h-4 text-emerald-400" />
                <span>Autonomous Agent Orchestration Metrics</span>
              </h3>
              <div className="grid grid-cols-2 gap-3">
                <div className="p-3 rounded-xl bg-slate-950 border border-slate-800 space-y-1">
                  <div className="text-[11px] text-slate-400">Task Completion Rate</div>
                  <div className="text-xl font-bold text-emerald-400 font-mono">
                    {(report.agent_metrics.task_completion_rate * 100).toFixed(0)}%
                  </div>
                </div>
                <div className="p-3 rounded-xl bg-slate-950 border border-slate-800 space-y-1">
                  <div className="text-[11px] text-slate-400">Tool Selection Accuracy</div>
                  <div className="text-xl font-bold text-emerald-400 font-mono">
                    {(report.agent_metrics.tool_selection_accuracy * 100).toFixed(0)}%
                  </div>
                </div>
                <div className="p-3 rounded-xl bg-slate-950 border border-slate-800 space-y-1">
                  <div className="text-[11px] text-slate-400">Tool Execution Failure</div>
                  <div className="text-xl font-bold text-emerald-400 font-mono">
                    {(report.agent_metrics.tool_failure_rate * 100).toFixed(0)}%
                  </div>
                </div>
                <div className="p-3 rounded-xl bg-slate-950 border border-slate-800 space-y-1">
                  <div className="text-[11px] text-slate-400">Avg Steps / Workflow</div>
                  <div className="text-xl font-bold text-white font-mono">
                    {report.agent_metrics.avg_steps_per_task}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
};
