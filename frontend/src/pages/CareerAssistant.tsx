import React, { useState } from 'react';
import {
  Bot,
  Send,
  Sparkles,
  ChevronDown,
  ChevronUp,
  Cpu,
  Clock,
  CheckCircle2,
  ListTodo,
  FileSearch,
  Scale,
  BrainCircuit,
} from 'lucide-react';
import { AgentStepTrace, AgentRunResponse } from '../types';
import { runAgentWorkflow, chatAssistant } from '../api';

interface Message {
  sender: 'user' | 'assistant';
  content: string;
  steps?: AgentStepTrace[];
  toolsUsed?: string[];
  citations?: any[];
  timestamp: string;
}

interface CareerAssistantProps {
  initialJobId?: number;
}

export const CareerAssistant: React.FC<CareerAssistantProps> = ({ initialJobId }) => {
  const [messages, setMessages] = useState<Message[]>([
    {
      sender: 'assistant',
      content:
        "Hello Alex! I am your CareerMatch AI intelligence agent. I have access to 14 specialized career tools, " +
        "your extracted resume profile, and verified live job opportunities. You can ask me questions about your fit, " +
        "or select one of the autonomous workflows below.",
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [openTraces, setOpenTraces] = useState<Record<number, boolean>>({});

  const handleSend = async (customPrompt?: string) => {
    const textToSend = customPrompt || input;
    if (!textToSend.trim() || loading) return;

    const userMsg: Message = {
      sender: 'user',
      content: textToSend,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    setMessages((prev) => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    try {
      // Execute multi-step agent workflow
      const result: AgentRunResponse = await runAgentWorkflow(textToSend, initialJobId);
      const assistantMsg: Message = {
        sender: 'assistant',
        content: result.response,
        steps: result.steps,
        toolsUsed: result.tools_used,
        citations: result.evidence_citations,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      };
      setMessages((prev) => [...prev, assistantMsg]);
    } catch (err) {
      console.error(err);
      setMessages((prev) => [
        ...prev,
        {
          sender: 'assistant',
          content: 'An error occurred while executing the agent workflow. Please try again.',
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const toggleTrace = (idx: number) => {
    setOpenTraces((prev) => ({ ...prev, [idx]: !prev[idx] }));
  };

  const workflows = [
    {
      title: 'Top Ranked Jobs & Skill Gaps',
      icon: FileSearch,
      prompt: 'Find the top 10 jobs for my profile, rank them, explain the top match and identify my biggest skill gaps.',
    },
    {
      title: 'Compare Saved Positions',
      icon: Scale,
      prompt: 'Compare three saved jobs and recommend which best aligns with my goals, providing evidence and tradeoffs.',
    },
    {
      title: 'Market Gap Learning Plan',
      icon: BrainCircuit,
      prompt: 'Identify the skills required by my target jobs, calculate gaps against my profile and create a prioritized preparation plan.',
    },
    {
      title: 'Interview & Application Prep',
      icon: ListTodo,
      prompt: 'Prepare me for this job by analyzing the description, my resume, gaps, checklist, and likely interview questions.',
    },
  ];

  return (
    <div className="h-[calc(100vh-8.5rem)] flex flex-col bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden shadow-2xl animate-in fade-in duration-200">
      {/* Top Bar */}
      <div className="p-4 border-b border-slate-800 bg-slate-950/60 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400">
            <Bot className="w-5 h-5" />
          </div>
          <div>
            <div className="text-sm font-bold text-white flex items-center gap-2">
              <span>CareerMatch Agentic Orchestrator</span>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300">
                14 Tools Active
              </span>
            </div>
            <div className="text-[11px] text-slate-400">Multi-step autonomous execution with grounded IR evidence</div>
          </div>
        </div>
      </div>

      {/* Suggested Workflows Quick Pills */}
      <div className="p-3 border-b border-slate-800/80 bg-slate-950/30 flex gap-2 overflow-x-auto">
        {workflows.map((wf) => {
          const Icon = wf.icon;
          return (
            <button
              key={wf.title}
              onClick={() => handleSend(wf.prompt)}
              disabled={loading}
              className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-800/80 hover:bg-slate-700/80 text-slate-300 text-xs font-medium border border-slate-700/60 transition shrink-0 hover:text-white"
            >
              <Icon className="w-3.5 h-3.5 text-emerald-400" />
              <span>{wf.title}</span>
            </button>
          );
        })}
      </div>

      {/* Chat Messages */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6">
        {messages.map((m, idx) => (
          <div
            key={idx}
            className={`flex flex-col ${m.sender === 'user' ? 'items-end' : 'items-start'} space-y-2`}
          >
            <div
              className={`max-w-2xl rounded-2xl p-4 text-sm leading-relaxed ${
                m.sender === 'user'
                  ? 'bg-emerald-600 text-white rounded-tr-none shadow-md'
                  : 'bg-slate-950/80 border border-slate-800 text-slate-200 rounded-tl-none shadow-md'
              }`}
            >
              {/* Message Content */}
              <div className="whitespace-pre-line">{m.content}</div>

              {/* Collapsible Agent Execution Trace */}
              {m.steps && m.steps.length > 0 && (
                <div className="mt-4 pt-3 border-t border-slate-800/80">
                  <button
                    onClick={() => toggleTrace(idx)}
                    className="flex items-center gap-1.5 text-xs text-emerald-400 hover:text-emerald-300 font-mono font-medium transition"
                  >
                    <Cpu className="w-3.5 h-3.5" />
                    <span>
                      {openTraces[idx] ? 'Hide' : 'View'} Agent Execution Trace ({m.steps.length} Tool Steps)
                    </span>
                    {openTraces[idx] ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
                  </button>

                  {openTraces[idx] && (
                    <div className="mt-3 space-y-2.5 font-mono text-xs bg-slate-900 p-3 rounded-xl border border-slate-800">
                      {m.steps.map((st) => (
                        <div key={st.step_number} className="border-l-2 border-emerald-500 pl-2.5 py-0.5 space-y-1">
                          <div className="flex items-center justify-between text-[11px]">
                            <span className="text-emerald-400 font-bold">
                              Step {st.step_number}: {st.tool_name}
                            </span>
                            <span className="text-slate-500 flex items-center gap-1">
                              <Clock className="w-3 h-3" />
                              {st.execution_time_ms}ms
                            </span>
                          </div>
                          <div className="text-[11px] text-slate-400">{st.thought}</div>
                          <div className="text-[10px] text-slate-500 bg-slate-950 p-1.5 rounded border border-slate-800/60 truncate">
                            Result: {st.tool_output_summary}
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </div>

            <div className="text-[10px] text-slate-500 px-1 font-mono">{m.timestamp}</div>
          </div>
        ))}

        {loading && (
          <div className="flex items-center gap-2 text-slate-400 text-xs font-mono p-4 bg-slate-950/60 rounded-xl border border-slate-800/60 w-fit">
            <Sparkles className="w-4 h-4 text-emerald-400 animate-spin" />
            <span>Agent planning and executing tool sequences...</span>
          </div>
        )}
      </div>

      {/* Input Bar */}
      <div className="p-4 border-t border-slate-800 bg-slate-950/80">
        <div className="flex gap-3">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSend()}
            placeholder="Ask questions about jobs, compare positions, or ask for preparation steps..."
            className="flex-1 bg-slate-900 border border-slate-800 rounded-xl px-4 py-3 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-emerald-500 transition"
          />
          <button
            onClick={() => handleSend()}
            disabled={loading || !input.trim()}
            className="px-5 py-3 rounded-xl bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-white font-bold text-sm transition shadow-lg shadow-emerald-600/20 shrink-0"
          >
            <Send className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
};
