import React, { useState, useEffect } from 'react';
import {
  Upload,
  User,
  Briefcase,
  GraduationCap,
  FolderGit2,
  Zap,
  CheckCircle2,
  Plus,
  Trash2,
  Save,
  FileText,
  AlertCircle,
} from 'lucide-react';
import { CandidateProfileSchema, CandidateSkill } from '../types';
import { getProfile, updateProfile, uploadResume } from '../api';

export const CandidateProfile: React.FC = () => {
  const [profile, setProfile] = useState<CandidateProfileSchema | null>(null);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [newSkillName, setNewSkillName] = useState('');
  const [newSkillCat, setNewSkillCat] = useState('Frameworks');

  useEffect(() => {
    loadProfile();
  }, []);

  const loadProfile = async () => {
    try {
      setLoading(true);
      const data = await getProfile();
      setProfile(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    try {
      setUploading(true);
      setMessage(null);
      const resp = await uploadResume(file);
      setProfile(resp.structured_profile);
      setMessage('Resume successfully uploaded and parsed into structured intelligence!');
      setTimeout(() => setMessage(null), 4000);
    } catch (err: any) {
      console.error(err);
      setMessage(err.response?.data?.detail || 'Failed to parse resume.');
    } finally {
      setUploading(false);
    }
  };

  const handleSaveProfile = async () => {
    if (!profile) return;
    try {
      setLoading(true);
      const updated = await updateProfile(profile);
      setProfile(updated);
      setMessage('Profile updated and dense vector embeddings re-indexed!');
      setTimeout(() => setMessage(null), 3000);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleAddSkill = () => {
    if (!newSkillName.trim() || !profile) return;
    const newSkill: CandidateSkill = {
      name: newSkillName.trim(),
      category: newSkillCat,
      is_explicit: true,
      confidence: 1.0,
    };
    setProfile({
      ...profile,
      skills: [...profile.skills, newSkill],
    });
    setNewSkillName('');
  };

  const handleRemoveSkill = (index: number) => {
    if (!profile) return;
    const updated = [...profile.skills];
    updated.splice(index, 1);
    setProfile({ ...profile, skills: updated });
  };

  if (loading && !profile) {
    return <div className="p-12 text-center text-slate-400">Loading candidate profile...</div>;
  }

  return (
    <div className="space-y-8 animate-in fade-in duration-200">
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-black text-white tracking-tight">Candidate Profile Intelligence</h1>
          <p className="text-xs text-slate-400 mt-1">
            Structured candidate extraction with explicit qualification demarcation and vector indexing.
          </p>
        </div>
        <button
          onClick={handleSaveProfile}
          className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs transition shadow-lg shadow-emerald-600/20"
        >
          <Save className="w-4 h-4" />
          <span>Save Changes & Re-embed</span>
        </button>
      </div>

      {message && (
        <div className="bg-emerald-500/10 border border-emerald-500/20 rounded-xl p-4 text-xs text-emerald-300 flex items-center gap-2.5">
          <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
          <span>{message}</span>
        </div>
      )}

      {/* Resume Upload Dropzone */}
      <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 space-y-4">
        <h2 className="text-sm font-bold text-white flex items-center gap-2">
          <Upload className="w-4 h-4 text-emerald-400" />
          <span>Upload Resume (PDF, DOCX, TXT)</span>
        </h2>
        <div className="border-2 border-dashed border-slate-700 hover:border-emerald-500/50 rounded-xl p-8 text-center transition bg-slate-950/40 relative">
          <input
            type="file"
            accept=".pdf,.txt,.docx"
            onChange={handleFileUpload}
            disabled={uploading}
            className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
          />
          <div className="space-y-2 pointer-events-none">
            <FileText className="w-8 h-8 mx-auto text-emerald-400" />
            <div className="text-sm font-semibold text-slate-200">
              {uploading ? 'Parsing and extracting structured entities...' : 'Click or drag and drop your resume file here'}
            </div>
            <div className="text-xs text-slate-500 font-mono">Max size: 5MB • Formats: PDF, Plain Text, DOCX</div>
          </div>
        </div>
      </div>

      {profile && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left Column: Personal info & Summary */}
          <div className="space-y-6">
            <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 space-y-4">
              <h3 className="text-sm font-bold text-white flex items-center gap-2">
                <User className="w-4 h-4 text-emerald-400" />
                <span>Candidate Information</span>
              </h3>
              <div className="space-y-3 text-xs">
                <div>
                  <label className="text-slate-400 block mb-1 font-medium">Full Name</label>
                  <input
                    type="text"
                    value={profile.full_name}
                    onChange={(e) => setProfile({ ...profile, full_name: e.target.value })}
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-white"
                  />
                </div>
                <div>
                  <label className="text-slate-400 block mb-1 font-medium">Email</label>
                  <input
                    type="email"
                    value={profile.email || ''}
                    onChange={(e) => setProfile({ ...profile, email: e.target.value })}
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-white"
                  />
                </div>
                <div>
                  <label className="text-slate-400 block mb-1 font-medium">Experience Level</label>
                  <select
                    value={profile.experience_level}
                    onChange={(e) => setProfile({ ...profile, experience_level: e.target.value })}
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-white"
                  >
                    <option value="entry">Entry Level</option>
                    <option value="mid">Mid Level</option>
                    <option value="senior">Senior</option>
                    <option value="lead">Staff / Lead</option>
                  </select>
                </div>
                <div>
                  <label className="text-slate-400 block mb-1 font-medium">Total Years of Experience</label>
                  <input
                    type="number"
                    step="0.5"
                    value={profile.total_years_experience}
                    onChange={(e) => setProfile({ ...profile, total_years_experience: parseFloat(e.target.value) || 0 })}
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-white font-mono"
                  />
                </div>
              </div>
            </div>

            <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 space-y-3">
              <h3 className="text-sm font-bold text-white">Professional Summary</h3>
              <textarea
                rows={4}
                value={profile.summary}
                onChange={(e) => setProfile({ ...profile, summary: e.target.value })}
                className="w-full bg-slate-950 border border-slate-800 rounded-lg p-3 text-xs text-slate-200 leading-relaxed"
              />
            </div>
          </div>

          {/* Right Column: Skills Management & Work History */}
          <div className="lg:col-span-2 space-y-6">
            {/* Skills Taxonomy Section */}
            <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-sm font-bold text-white flex items-center gap-2">
                    <Zap className="w-4 h-4 text-emerald-400" />
                    <span>Skills & Competencies ({profile.skills.length})</span>
                  </h3>
                  <p className="text-xs text-slate-400 mt-0.5">
                    Green = explicitly stated in resume. Indigo = inferred from project descriptions.
                  </p>
                </div>
              </div>

              {/* Add Skill form */}
              <div className="flex gap-2">
                <input
                  type="text"
                  placeholder="Add skill (e.g. PyTorch, Rust, Kubernetes)..."
                  value={newSkillName}
                  onChange={(e) => setNewSkillName(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleAddSkill()}
                  className="bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-xs text-white flex-1"
                />
                <select
                  value={newSkillCat}
                  onChange={(e) => setNewSkillCat(e.target.value)}
                  className="bg-slate-950 border border-slate-800 rounded-lg px-2.5 py-2 text-xs text-slate-300"
                >
                  <option value="Languages">Languages</option>
                  <option value="Frameworks">Frameworks</option>
                  <option value="AI/ML">AI/ML</option>
                  <option value="Cloud/DevOps">Cloud/DevOps</option>
                  <option value="Databases">Databases</option>
                </select>
                <button
                  onClick={handleAddSkill}
                  className="px-3 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold flex items-center gap-1"
                >
                  <Plus className="w-3.5 h-3.5" />
                  <span>Add</span>
                </button>
              </div>

              {/* Skill chips */}
              <div className="flex flex-wrap gap-2 pt-2">
                {profile.skills.map((s, idx) => (
                  <span
                    key={`${s.name}-${idx}`}
                    className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-lg text-xs font-medium border ${
                      s.is_explicit
                        ? 'bg-emerald-500/10 text-emerald-300 border-emerald-500/30'
                        : 'bg-indigo-500/10 text-indigo-300 border-indigo-500/30'
                    }`}
                  >
                    <span>{s.name}</span>
                    <button
                      onClick={() => handleRemoveSkill(idx)}
                      className="text-slate-400 hover:text-rose-400 transition ml-1"
                    >
                      <Trash2 className="w-3 h-3" />
                    </button>
                  </span>
                ))}
              </div>
            </div>

            {/* Experience Section */}
            <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 space-y-4">
              <h3 className="text-sm font-bold text-white flex items-center gap-2">
                <Briefcase className="w-4 h-4 text-emerald-400" />
                <span>Extracted Work Experience ({profile.experience.length})</span>
              </h3>
              <div className="space-y-4">
                {profile.experience.map((exp, i) => (
                  <div key={i} className="p-4 rounded-xl bg-slate-950/60 border border-slate-800/80 space-y-2">
                    <div className="flex justify-between items-start">
                      <div>
                        <div className="font-bold text-sm text-white">{exp.role}</div>
                        <div className="text-xs text-emerald-400 font-semibold">{exp.company}</div>
                      </div>
                    </div>
                    <p className="text-xs text-slate-300 whitespace-pre-line leading-relaxed">{exp.description}</p>
                    {exp.technologies && exp.technologies.length > 0 && (
                      <div className="flex flex-wrap gap-1 pt-1">
                        {exp.technologies.map((t) => (
                          <span key={t} className="px-2 py-0.5 rounded text-[10px] bg-slate-800 text-slate-400 font-mono">
                            {t}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>

            {/* Education Section */}
            <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 space-y-4">
              <h3 className="text-sm font-bold text-white flex items-center gap-2">
                <GraduationCap className="w-4 h-4 text-emerald-400" />
                <span>Education</span>
              </h3>
              <div className="space-y-3">
                {profile.education.map((edu, i) => (
                  <div key={i} className="p-4 rounded-xl bg-slate-950/60 border border-slate-800/80">
                    <div className="font-bold text-sm text-white">{edu.degree}</div>
                    <div className="text-xs text-slate-400">{edu.institution} {edu.graduation_year ? `(${edu.graduation_year})` : ''}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
