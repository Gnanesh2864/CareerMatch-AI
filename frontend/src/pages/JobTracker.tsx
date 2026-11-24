import React, { useState, useEffect } from 'react';
import {
  Briefcase,
  Bookmark,
  Send,
  Calendar,
  Award,
  XCircle,
  Clock,
  MapPin,
  ExternalLink,
  Edit3,
  CheckCircle2,
} from 'lucide-react';
import { TrackedApplication, TrackerAnalytics } from '../types';
import { getTrackedApplications, updateApplicationStatus, getTrackerAnalytics } from '../api';

interface JobTrackerProps {
  onSelectJob: (jobId: number) => void;
}

export const JobTracker: React.FC<JobTrackerProps> = ({ onSelectJob }) => {
  const [applications, setApplications] = useState<TrackedApplication[]>([]);
  const [analytics, setAnalytics] = useState<TrackerAnalytics | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<string>('all');

  useEffect(() => {
    loadTrackerData();
  }, []);

  const loadTrackerData = async () => {
    try {
      setLoading(true);
      const [apps, stats] = await Promise.all([
        getTrackedApplications(),
        getTrackerAnalytics(),
      ]);
      setApplications(apps);
      setAnalytics(stats);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleStatusChange = async (jobId: number, newStatus: string) => {
    try {
      await updateApplicationStatus(jobId, newStatus);
      loadTrackerData();
    } catch (err) {
      console.error(err);
    }
  };

  const stages = [
    { id: 'all', label: 'All Jobs', count: applications.length },
    { id: 'saved', label: 'Saved', count: applications.filter((a) => a.status === 'saved').length, icon: Bookmark, color: 'text-indigo-400' },
    { id: 'applied', label: 'Applied', count: applications.filter((a) => a.status === 'applied').length, icon: Send, color: 'text-emerald-400' },
    { id: 'interview', label: 'Interviewing', count: applications.filter((a) => a.status === 'interview').length, icon: Calendar, color: 'text-amber-400' },
    { id: 'offer', label: 'Offers', count: applications.filter((a) => a.status === 'offer').length, icon: Award, color: 'text-teal-400' },
    { id: 'rejected', label: 'Archived', count: applications.filter((a) => a.status === 'rejected').length, icon: XCircle, color: 'text-rose-400' },
  ];

  const filteredApps = activeTab === 'all'
    ? applications
    : applications.filter((a) => a.status === activeTab);

  return (
    <div className="space-y-6 animate-in fade-in duration-200">
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-black text-white tracking-tight">Application Tracker & Lifecycle</h1>
          <p className="text-xs text-slate-400 mt-1">
            Real-time pipeline analytics and application stage management.
          </p>
        </div>
      </div>

      {/* Analytics Funnel Cards */}
      {analytics && (
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
          {stages.slice(1).map((st) => (
            <div key={st.id} className="p-4 rounded-xl bg-slate-900 border border-slate-800 space-y-1">
              <div className="text-xs text-slate-400 font-medium">{st.label}</div>
              <div className="text-xl font-black text-white font-mono">{st.count}</div>
            </div>
          ))}
        </div>
      )}

      {/* Stage Filter Tabs */}
      <div className="flex gap-2 border-b border-slate-800 pb-3 overflow-x-auto">
        {stages.map((st) => (
          <button
            key={st.id}
            onClick={() => setActiveTab(st.id)}
            className={`flex items-center gap-2 px-3.5 py-2 rounded-lg text-xs font-semibold transition shrink-0 ${
              activeTab === st.id
                ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                : 'text-slate-400 hover:text-white hover:bg-slate-800/60'
            }`}
          >
            <span>{st.label}</span>
            <span className={`text-[10px] font-mono px-1.5 py-0.2 rounded ${
              activeTab === st.id ? 'bg-emerald-500/20 text-emerald-300' : 'bg-slate-800 text-slate-400'
            }`}>
              {st.count}
            </span>
          </button>
        ))}
      </div>

      {/* Applications List */}
      <div className="space-y-3">
        {filteredApps.map((app) => (
          <div
            key={app.application_id}
            className="p-5 rounded-2xl bg-slate-900 border border-slate-800 flex flex-col md:flex-row md:items-center justify-between gap-4 hover:border-slate-700 transition"
          >
            <div className="space-y-1.5 flex-1">
              <div className="flex items-center gap-2">
                <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">{app.company}</span>
                <span className="text-slate-600">•</span>
                <span className="text-xs text-slate-400 flex items-center gap-1">
                  <MapPin className="w-3 h-3 text-slate-500" />
                  {app.location}
                </span>
                <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-slate-800 text-slate-300">
                  {app.remote_status}
                </span>
              </div>

              <h3
                onClick={() => onSelectJob(app.job_id)}
                className="text-base font-bold text-white hover:text-emerald-400 transition cursor-pointer"
              >
                {app.title}
              </h3>

              {app.notes && (
                <div className="text-xs text-slate-300 bg-slate-950/60 p-2 rounded-lg border border-slate-800/60 italic">
                  Note: "{app.notes}"
                </div>
              )}
            </div>

            {/* Stage Selector & Actions */}
            <div className="flex items-center gap-3 shrink-0">
              <div className="space-y-1">
                <label className="text-[10px] text-slate-500 font-mono block">STAGE</label>
                <select
                  value={app.status}
                  onChange={(e) => handleStatusChange(app.job_id, e.target.value)}
                  className="bg-slate-950 border border-slate-800 rounded-lg px-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-emerald-500 font-semibold"
                >
                  <option value="saved">Saved</option>
                  <option value="applied">Applied</option>
                  <option value="interview">Interviewing</option>
                  <option value="offer">Offer Received</option>
                  <option value="rejected">Rejected / Archived</option>
                </select>
              </div>

              <button
                onClick={() => onSelectJob(app.job_id)}
                className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium border border-slate-700 transition mt-4"
              >
                View Details
              </button>
            </div>
          </div>
        ))}

        {filteredApps.length === 0 && !loading && (
          <div className="text-center py-12 rounded-2xl bg-slate-900 border border-slate-800 text-slate-400">
            No applications in this category. Search jobs to save or track them!
          </div>
        )}
      </div>
    </div>
  );
};
