import React, { useState } from 'react';
import { Sidebar } from './components/Sidebar';
import { Navbar } from './components/Navbar';
import { Dashboard } from './pages/Dashboard';
import { JobSearch } from './pages/JobSearch';
import { CandidateProfile } from './pages/CandidateProfile';
import { CareerAssistant } from './pages/CareerAssistant';
import { SkillIntelligence } from './pages/SkillIntelligence';
import { JobTracker } from './pages/JobTracker';
import { EvaluationLab } from './pages/EvaluationLab';
import { Settings } from './pages/Settings';
import { JobDetailModal } from './pages/JobDetailModal';
import { Job } from './types';
import { getJobById, triggerIngestion } from './api';

export function App() {
  const [currentTab, setCurrentTab] = useState<string>('dashboard');
  const [selectedJob, setSelectedJob] = useState<Job | null>(null);
  const [agentContextJobId, setAgentContextJobId] = useState<number | undefined>(undefined);
  const [isRefreshing, setIsRefreshing] = useState(false);

  const handleSelectJob = async (jobId: number) => {
    try {
      const job = await getJobById(jobId);
      setSelectedJob(job);
    } catch (err) {
      console.error('Error fetching job details:', err);
    }
  };

  const handleOpenAgentWithJob = (jobId: number) => {
    setAgentContextJobId(jobId);
    setCurrentTab('assistant');
  };

  const handleSyncPipeline = async () => {
    try {
      setIsRefreshing(true);
      await triggerIngestion();
      alert('Pipeline synced with external and curated sources!');
    } catch (err) {
      console.error(err);
    } finally {
      setIsRefreshing(false);
    }
  };

  return (
    <div className="flex h-screen bg-slate-950 text-slate-100 font-sans antialiased overflow-hidden">
      {/* Sidebar Navigation */}
      <Sidebar currentTab={currentTab} setCurrentTab={setCurrentTab} />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0 h-screen overflow-hidden">
        {/* Top Navbar */}
        <Navbar onRefresh={handleSyncPipeline} isRefreshing={isRefreshing} />

        {/* Dynamic Page Views */}
        <main className="flex-1 overflow-y-auto p-6 md:p-8">
          <div className="max-w-7xl mx-auto pb-12">
            {currentTab === 'dashboard' && (
              <Dashboard
                onSelectJob={handleSelectJob}
                onNavigate={(tab) => setCurrentTab(tab)}
              />
            )}
            {currentTab === 'search' && <JobSearch onSelectJob={handleSelectJob} />}
            {currentTab === 'profile' && <CandidateProfile />}
            {currentTab === 'assistant' && (
              <CareerAssistant initialJobId={agentContextJobId} />
            )}
            {currentTab === 'skills' && <SkillIntelligence />}
            {currentTab === 'tracker' && <JobTracker onSelectJob={handleSelectJob} />}
            {currentTab === 'evaluation' && <EvaluationLab />}
            {currentTab === 'settings' && <Settings />}
          </div>
        </main>
      </div>

      {/* Job Detail Modal */}
      {selectedJob && (
        <JobDetailModal
          job={selectedJob}
          onClose={() => setSelectedJob(null)}
          onOpenAgentWithJob={handleOpenAgentWithJob}
        />
      )}
    </div>
  );
}

export default App;
