import React, { useState } from 'react';
import {
  Settings as SettingsIcon,
  Save,
  Key,
  Database,
  Cpu,
  ShieldCheck,
  CheckCircle2,
} from 'lucide-react';

export const Settings: React.FC = () => {
  const [targetTitles, setTargetTitles] = useState('AI Engineer, ML Engineer, Backend Software Engineer');
  const [preferredLocations, setPreferredLocations] = useState('Remote, San Francisco, CA, Seattle, WA');
  const [remoteOnly, setRemoteOnly] = useState(false);
  const [minSalary, setMinSalary] = useState(130000);
  const [geminiKey, setGeminiKey] = useState('');
  const [message, setMessage] = useState<string | null>(null);

  const handleSave = () => {
    setMessage('User preferences and platform configuration successfully saved!');
    setTimeout(() => setMessage(null), 3000);
  };

  return (
    <div className="space-y-8 max-w-4xl animate-in fade-in duration-200">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-black text-white tracking-tight">System & Candidate Settings</h1>
        <p className="text-xs text-slate-400 mt-1">
          Manage personalized matching preferences, vector model parameters, and external LLM keys.
        </p>
      </div>

      {message && (
        <div className="bg-emerald-500/10 border border-emerald-500/20 rounded-xl p-4 text-xs text-emerald-300 flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4 text-emerald-400" />
          <span>{message}</span>
        </div>
      )}

      {/* Matching Preferences */}
      <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 space-y-4">
        <h2 className="text-sm font-bold text-white flex items-center gap-2">
          <SettingsIcon className="w-4 h-4 text-emerald-400" />
          <span>Candidate Preferences (Tuned for Ranking Signals)</span>
        </h2>

        <div className="space-y-4 text-xs">
          <div>
            <label className="text-slate-400 block mb-1 font-medium">Target Job Titles (comma separated)</label>
            <input
              type="text"
              value={targetTitles}
              onChange={(e) => setTargetTitles(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-lg p-3 text-white"
            />
          </div>

          <div>
            <label className="text-slate-400 block mb-1 font-medium">Preferred Locations</label>
            <input
              type="text"
              value={preferredLocations}
              onChange={(e) => setPreferredLocations(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-lg p-3 text-white"
            />
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="text-slate-400 block mb-1 font-medium">Minimum Base Salary ($ USD)</label>
              <input
                type="number"
                value={minSalary}
                onChange={(e) => setMinSalary(parseInt(e.target.value) || 0)}
                className="w-full bg-slate-950 border border-slate-800 rounded-lg p-3 text-white font-mono"
              />
            </div>

            <div className="flex items-center pt-5">
              <label className="flex items-center gap-2 cursor-pointer select-none">
                <input
                  type="checkbox"
                  checked={remoteOnly}
                  onChange={(e) => setRemoteOnly(e.target.checked)}
                  className="rounded bg-slate-800 border-slate-700 text-emerald-500 focus:ring-emerald-500/20"
                />
                <span className="text-slate-300 font-medium">Strictly Remote Roles Only</span>
              </label>
            </div>
          </div>
        </div>
      </div>

      {/* Architecture & Engine Status */}
      <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 space-y-4">
        <h2 className="text-sm font-bold text-white flex items-center gap-2">
          <Cpu className="w-4 h-4 text-emerald-400" />
          <span>Active Architecture Configuration</span>
        </h2>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-xs font-mono">
          <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-1">
            <div className="text-slate-400 font-sans">Dense Vector Model</div>
            <div className="text-emerald-400 font-bold">all-MiniLM-L6-v2</div>
            <div className="text-[10px] text-slate-500">384 Dimensions (Local Inference)</div>
          </div>

          <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-1">
            <div className="text-slate-400 font-sans">Persistence Layer</div>
            <div className="text-emerald-400 font-bold">Dual Storage Engine</div>
            <div className="text-[10px] text-slate-500">Postgres + pgvector / SQLite</div>
          </div>

          <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-1">
            <div className="text-slate-400 font-sans">Autonomous Agent</div>
            <div className="text-emerald-400 font-bold">14 Approved Tools</div>
            <div className="text-[10px] text-slate-500">Zero arbitrary code execution</div>
          </div>
        </div>
      </div>

      {/* External LLM Configuration */}
      <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 space-y-4">
        <h2 className="text-sm font-bold text-white flex items-center gap-2">
          <Key className="w-4 h-4 text-emerald-400" />
          <span>LLM Provider Keys (Optional)</span>
        </h2>
        <p className="text-xs text-slate-400">
          The platform operates completely locally with grounded synthesis. You may optionally supply a Google Gemini API key for external generation.
        </p>

        <div className="text-xs space-y-3">
          <div>
            <label className="text-slate-400 block mb-1 font-medium">Google Gemini API Key</label>
            <input
              type="password"
              placeholder="AIzaSy..."
              value={geminiKey}
              onChange={(e) => setGeminiKey(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-lg p-3 text-white font-mono placeholder-slate-600"
            />
          </div>
        </div>
      </div>

      {/* Save Button */}
      <div className="flex justify-end">
        <button
          onClick={handleSave}
          className="flex items-center gap-2 px-6 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs transition shadow-lg shadow-emerald-600/20"
        >
          <Save className="w-4 h-4" />
          <span>Save Preferences</span>
        </button>
      </div>
    </div>
  );
};
