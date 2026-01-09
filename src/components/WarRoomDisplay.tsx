import React, { useState } from 'react';
import { useScenario } from '../ScenarioContext';
import { SCENARIOS, SUCCESS_REPORT } from '../mockData';

import { SettingsModal } from './SettingsModal';
import { AboutModal } from './AboutModal';
import { AboutAidaptivModal } from './AboutAidaptivModal';

import { CrashOverlay } from './CrashOverlay';

const Sidebar = () => {
    const { toggleMonitor, showHardwareMonitor, activeScenario, setActiveScenario, isAnalysisRunning } = useScenario();
    const [showSettings, setShowSettings] = useState(false);
    const [showAbout, setShowAbout] = useState(false);
    const [showAboutAidaptiv, setShowAboutAidaptiv] = useState(false);

    return (
        <div className="w-[238px] bg-dashboard-card flex flex-col border-r border-dashboard-border/50 shrink-0 z-20 shadow-lg">
            {/* Logo Area */}
            <div className="h-[70px] flex items-center justify-center border-b border-dashboard-border/50 px-6">
                <h1 className="text-xl font-bold text-text-primary tracking-tight">aiDAPTIV+ <span className="text-accent-primary">Demo</span></h1>
            </div>

            {/* Navigation */}
            <div className="flex-1 overflow-y-auto py-6">

                {/* SECTION 1: SCENARIOS */}
                <div className="text-[11px] font-bold text-text-secondary uppercase tracking-wider mb-3 px-6">Scenarios</div>
                <div className="flex flex-col gap-1 px-3">
                    {SCENARIOS.map(scenario => (
                        <div
                            key={scenario.id}
                            onClick={() => !isAnalysisRunning && setActiveScenario(scenario.id)}
                            className={`p-3 rounded-lg border cursor-pointer transition-all hover:bg-dashboard-bg group relative overflow-hidden ${activeScenario.id === scenario.id
                                ? 'bg-[#1e3a8a] border-transparent shadow-md'
                                : isAnalysisRunning ? 'opacity-50 cursor-not-allowed' : 'bg-transparent border-transparent'
                                }`}
                        >
                            <div className="flex items-start gap-3 relative z-10">
                                {/* Radio Circle */}
                                <div className={`mt-0.5 w-4 h-4 rounded-full border flex items-center justify-center shrink-0 ${activeScenario.id === scenario.id
                                    ? 'border-white bg-white'
                                    : 'border-text-secondary'
                                    }`}>
                                    {activeScenario.id === scenario.id && <div className="w-1.5 h-1.5 rounded-full bg-accent-primary" />}
                                </div>

                                <div>
                                    <div className={`text-sm font-bold leading-tight ${activeScenario.id === scenario.id ? 'text-white' : 'text-text-primary group-hover:text-white'}`}>
                                        {scenario.title}
                                    </div>
                                    <div className={`text-xs italic mt-1 leading-tight ${activeScenario.id === scenario.id ? 'text-blue-200' : 'text-text-muted'}`}>
                                        {scenario.subtitle}
                                    </div>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>

                {/* SEPARATOR */}
                <div className="my-6 mx-4 border-t border-dashboard-border/50" />

                {/* SECTION 2: UTILITIES */}
                <div className="flex flex-col gap-1 px-3">
                    <NavItem
                        icon="cpu"
                        label="System Telemetry"
                        active={showHardwareMonitor}
                        onClick={toggleMonitor}
                    />
                    <NavItem icon="settings" label="Settings" onClick={() => setShowSettings(true)} />
                    <NavItem icon="info" label="About Demo" onClick={() => setShowAbout(true)} />
                    <NavItem icon="zap" label="About aiDAPTIV+" onClick={() => setShowAboutAidaptiv(true)} />
                </div>
            </div>

            {/* User Account - Bottom of Sidebar */}
            <div className="border-t border-dashboard-border/50 p-4">
                <div className="flex items-center gap-3">
                    <div className="w-9 h-9 rounded-full bg-accent-info/20 border border-accent-info text-accent-info flex items-center justify-center font-bold text-sm">
                        DM
                    </div>
                    <div>
                        <div className="text-sm font-semibold text-text-primary">Demo Mode</div>
                    </div>
                </div>
            </div>

            {/* Settings Modal */}
            <SettingsModal isOpen={showSettings} onClose={() => setShowSettings(false)} />
            {/* About Modal */}
            <AboutModal isOpen={showAbout} onClose={() => setShowAbout(false)} />
            {/* About aiDAPTIV+ Modal */}
            <AboutAidaptivModal isOpen={showAboutAidaptiv} onClose={() => setShowAboutAidaptiv(false)} />
        </div>
    );
};

const NavItem = ({ active, icon, label, onClick }: { active?: boolean, icon: string, label: string, onClick?: () => void }) => {
    // Icons
    const icons: any = {
        cpu: <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z" /></svg>,
        settings: <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" /><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /></svg>,
        info: <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>,
        zap: <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" /></svg>
    };

    return (
        <div
            onClick={onClick}
            className={`px-3 py-3 rounded-lg cursor-pointer flex items-center gap-3 transition-colors ${active
                ? 'bg-[#1e3a8a] text-white font-bold'
                : 'text-text-secondary hover:text-text-primary hover:bg-dashboard-bg'
                }`}>
            {icons[icon]}
            <span className="text-sm">{label}</span>
        </div>
    );
};


// STAT CARD COMPONENT
const StatCard = ({ title, value, trend, color, icon }: any) => {

    const colors: any = {
        cyan: 'text-cyan-400',
        emerald: 'text-emerald-400',
        amber: 'text-amber-400',
        neutral: 'text-white'
    };

    return (
        <div className="bg-dashboard-card p-2.5 rounded-lg border border-dashboard-border/50 shadow-sm relative overflow-hidden group">
            <div className="relative z-10">
                <div className="flex justify-between mb-1">
                    <h4 className="text-[9px] font-bold text-text-muted uppercase tracking-widest">{title}</h4>
                    <span className="text-base grayscale opacity-50">{icon}</span>
                </div>
                <div className="flex items-end justify-between">
                    <div className={`text-2xl font-bold ${colors[color]} tracking-tight transition-all duration-300`}>{value}</div>
                    <div className="mb-0.5 text-[9px] font-medium bg-white/5 px-1.5 py-0.5 rounded text-white/70">{trend}</div>
                </div>
            </div>
        </div>
    )
}

const StatusBadge = ({ type }: { type: string }) => {
    switch (type) {
        case 'PROCESSING':
            return <span className="px-2.5 py-1 rounded-xl bg-blue-500/10 border border-blue-500/30 text-[10px] font-bold text-blue-500 tracking-wider">PROCESSING</span>;
        case 'ACTIVE':
            return <span className="px-2.5 py-1 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-[10px] font-bold text-emerald-500 tracking-wider flex items-center gap-2"><span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse-ring"></span>ACTIVE</span>;
        case 'COMPLETE':
            return <span className="px-2.5 py-1 rounded-xl bg-green-500/10 border border-green-500/30 text-[10px] font-bold text-green-500 tracking-wider">✓ COMPLETE</span>;
        case 'ANALYZING':
            return <span className="px-2.5 py-1 rounded-xl bg-cyan-500/10 border border-cyan-500/30 text-[10px] font-bold text-cyan-500 tracking-wider flex items-center gap-1">ANALYZING <span className="animate-dot-typing"></span></span>;
        case 'WAITING':
            return <span className="px-2.5 py-1 rounded-xl bg-gray-500/10 border border-gray-500/30 text-[10px] font-bold text-gray-500 tracking-wider">WAITING</span>;
        case 'WARNING':
            return <span className="px-2.5 py-1 rounded-xl bg-amber-500/10 border border-amber-500/30 text-[10px] font-bold text-amber-500 tracking-wider flex items-center gap-1">⚠️ MEMORY PRESSURE</span>;
        default: return null;
    }
}

// SUCCESS OVERLAY
// SUCCESS OVERLAY
const SuccessOverlay = ({ onClose }: { onClose: () => void }) => {
    const { metrics } = useScenario();

    return (
        <div className="absolute inset-0 bg-dashboard-bg/95 backdrop-blur-md z-50 flex items-center justify-center animate-fade-in text-white p-8">
            <div className="max-w-5xl w-full bg-[#1e293b] border border-blue-500/30 rounded-2xl shadow-[0_0_50px_rgba(59,130,246,0.15)] p-0 overflow-hidden flex flex-col">

                {/* Report Header */}
                <div className="bg-slate-800/50 p-8 border-b border-dashboard-border flex justify-between items-start">
                    <div>
                        <div className="flex items-center gap-3 mb-2">
                            <div className="px-2 py-1 bg-blue-500/20 text-blue-400 text-[10px] font-bold uppercase tracking-widest rounded-md border border-blue-500/20">
                                CONFIDENTIAL
                            </div>
                            <div className="text-text-muted text-xs uppercase tracking-wider">
                                GENERATED: {new Date().toLocaleDateString()}
                            </div>
                        </div>
                        <h2 className="text-3xl font-bold text-white tracking-tight">Strategic Intelligence Report</h2>
                        <div className="text-blue-300/80 mt-1">Target: Competitive Landscape Q1 2026</div>
                    </div>
                    <div className="text-right">
                        <div className="text-4xl font-black text-emerald-400 tracking-tighter">HIGH</div>
                        <div className="text-xs font-bold text-text-secondary uppercase tracking-widest">THREAT LEVEL DETECTED</div>
                    </div>
                </div>

                <div className="flex flex-1">
                    {/* Left: Key Insights */}
                    <div className="w-2/3 p-8 border-r border-dashboard-border">
                        <h3 className="text-xs font-bold text-text-muted uppercase tracking-widest mb-6 flex items-center gap-2">
                            <span className="w-1.5 h-1.5 bg-accent-primary rounded-full"></span> Executive Summary
                        </h3>

                        <div className="mb-8">
                            <div className="text-xl font-light leading-relaxed text-white mb-4">
                                {SUCCESS_REPORT.finding}
                            </div>
                            <div className="p-4 bg-blue-500/10 border-l-4 border-blue-500 rounded-r-lg">
                                <div className="text-xs font-bold text-blue-300 uppercase mb-1">Strategic Implication</div>
                                <div className="text-sm text-blue-100/80 leading-relaxed">
                                    {SUCCESS_REPORT.implication}
                                </div>
                            </div>
                        </div>

                        <h3 className="text-xs font-bold text-text-muted uppercase tracking-widest mb-4">Supporting Evidence</h3>
                        <ul className="space-y-3">
                            {SUCCESS_REPORT.evidence.map((line, i) => (
                                <li key={i} className="flex items-start gap-3 text-sm text-gray-300 group">
                                    <span className="text-blue-500 mt-1.5 text-[10px]">●</span>
                                    <span className="group-hover:text-white transition-colors">{line}</span>
                                </li>
                            ))}
                        </ul>
                    </div>

                    {/* Right: Metrics & Actions */}
                    <div className="w-1/3 bg-slate-800/20 p-8 flex flex-col">

                        <h3 className="text-xs font-bold text-text-muted uppercase tracking-widest mb-6">Analysis Scope</h3>

                        <div className="space-y-4 mb-8">
                            <div className="flex justify-between items-center p-3 bg-dashboard-bg rounded-lg border border-dashboard-border/50">
                                <span className="text-sm text-text-secondary">Key Topics</span>
                                <span className="font-mono font-bold text-white">{metrics.key_topics}</span>
                            </div>
                            <div className="flex justify-between items-center p-3 bg-dashboard-bg rounded-lg border border-dashboard-border/50">
                                <span className="text-sm text-text-secondary">Patterns Detected</span>
                                <span className="font-mono font-bold text-white">{metrics.patterns_detected}</span>
                            </div>
                            <div className="flex justify-between items-center p-3 bg-dashboard-bg rounded-lg border border-dashboard-border/50">
                                <span className="text-sm text-text-secondary">Insights Generated</span>
                                <span className="font-mono font-bold text-white">{metrics.insights_generated}</span>
                            </div>
                            <div className="flex justify-between items-center p-3 bg-dashboard-bg rounded-lg border border-dashboard-border/50">
                                <span className="text-sm text-text-secondary">Critical Flags</span>
                                <span className="font-mono font-bold text-white text-amber-400">{metrics.critical_flags}</span>
                            </div>
                        </div>

                        <div className="mt-auto space-y-3">
                            <button className="w-full py-3 rounded-lg bg-blue-600 hover:bg-blue-500 text-white font-bold text-sm shadow-lg transition-all flex items-center justify-center gap-2">
                                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" /></svg>
                                EXPORT REPORT
                            </button>
                            <button onClick={onClose} className="w-full py-3 rounded-lg bg-transparent border border-gray-600 hover:bg-gray-700 text-text-secondary hover:text-white font-bold text-sm transition-all">
                                CLOSE
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};


export const WarRoomDisplay = () => {
    const {
        feed, worldModel, systemState, metrics, performance, currentActivity,
        isAnalysisRunning, startAnalysis, stopAnalysis,
        isSuccess, isComplete, showResults, closeResults,
        activeScenario, tier, impactSummary
    } = useScenario();

    const activeFileRef = React.useRef<HTMLDivElement>(null);
    const scrollContainerRef = React.useRef<HTMLDivElement>(null);
    const messagesEndRef = React.useRef<HTMLDivElement>(null);
    const [focusedThoughtId, setFocusedThoughtId] = React.useState<string | null>(null);
    const [dataFilter, setDataFilter] = React.useState<'ALL' | 'LIVE' | 'ARCHIVE'>('ALL');

    // Auto-scroll effect for Data Grid (only if ALL or LIVE)
    React.useEffect(() => {
        if (isAnalysisRunning && activeFileRef.current && (dataFilter === 'ALL' || dataFilter === 'LIVE')) {
            activeFileRef.current.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
    }, [worldModel, isAnalysisRunning, dataFilter]);

    // Auto-scroll effect for Reasoning Chain
    React.useEffect(() => {
        if (messagesEndRef.current) {
            messagesEndRef.current.scrollIntoView({ behavior: 'auto' });
        }
        // DEBUG LOG
        console.log('Current Feed:', feed);
    }, [feed]);

    return (
        <div className="flex h-screen bg-dashboard-bg font-sans overflow-hidden relative">
            <Sidebar />

            <div className="flex-1 flex flex-col h-screen overflow-hidden relative">
                {/* SUCCESS OVERLAY */}
                {isSuccess && <SuccessOverlay onClose={closeResults} />}

                {/* CRASH OVERLAY */}
                {/* @ts-ignore - isCrashed is definitely in context, adding fallback just in case */}
                {/* We need to update useScenario return type if TS complains, but for now assuming it's there or will be added */}
                {/* Actually, let's just use it. If TS errors, I will fix types.ts or ScenarioContext.tsx */}
                <CrashOverlay />

                {/* MAIN DASHBOARD CONTENT */}
                <div className="flex-1 overflow-hidden p-6 flex flex-col space-y-6">

                    {/* Page Title & Trigger */}
                    <div className="flex justify-between items-end">
                        <div>
                            <h2 className="text-xl font-bold text-text-primary">{activeScenario.title}</h2>
                            <div className="text-sm text-text-secondary mt-1 flex items-center gap-2">
                                <span className="w-1.5 h-1.5 bg-accent-primary rounded-full"></span>
                                <span className="italic">{activeScenario.subtitle}</span>
                            </div>
                        </div>
                        {isComplete && !isSuccess ? (
                            <button
                                onClick={showResults}
                                className="h-12 px-8 rounded-xl shadow-lg transition-all flex items-center gap-3 font-bold text-base tracking-wide transform active:scale-95 duration-300 bg-emerald-600 hover:bg-emerald-500 text-white shadow-emerald-500/30 ring-1 ring-emerald-400/50 animate-pulse"
                            >
                                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                                </svg>
                                VIEW RESULTS
                            </button>
                        ) : (
                            <button
                                onClick={isAnalysisRunning ? stopAnalysis : startAnalysis}
                                className={`h-12 px-8 rounded-xl shadow-lg transition-all flex items-center gap-3 font-bold text-base tracking-wide transform active:scale-95 duration-300 ${isAnalysisRunning
                                    ? 'bg-red-500 hover:bg-red-600 text-white shadow-red-500/30'
                                    : 'bg-blue-600 hover:bg-blue-500 text-white shadow-blue-500/30 ring-1 ring-blue-400/50'
                                    }`}
                            >
                                {isAnalysisRunning ? (
                                    <>
                                        <div className="w-3 h-3 bg-white rounded-sm" /> STOP ANALYSIS
                                    </>
                                ) : (
                                    <>
                                        <div className="w-0 h-0 border-t-[6px] border-t-transparent border-l-[10px] border-l-white border-b-[6px] border-b-transparent ml-1" /> START ANALYSIS
                                    </>
                                )}
                            </button>
                        )}
                    </div>

                    {/* CURRENT ACTIVITY STATUS - Compact */}
                    <div className="bg-dashboard-card border border-dashboard-border/50 rounded-lg p-2.5">
                        <div className="flex items-center gap-3">
                            <div className={`w-2 h-2 rounded-full ${isAnalysisRunning
                                ? 'bg-blue-500 animate-pulse shadow-[0_0_8px_rgba(59,130,246,0.8)]'
                                : 'bg-gray-600'
                                }`} />
                            <div className="flex-1">
                                <div className="text-[10px] uppercase font-bold text-text-secondary tracking-wider mb-0.5">
                                    Current Activity
                                </div>
                                <div className={`text-sm font-medium ${isAnalysisRunning ? 'text-blue-300' : 'text-text-muted'
                                    }`}>
                                    {currentActivity}
                                </div>
                            </div>
                        </div>
                    </div>





                    {/* DYNAMIC WIDGETS ROW - Compact */}
                    <div className="grid grid-cols-4 gap-4">
                        <StatCard title="KEY TOPICS" value={metrics.key_topics} trend="Active" color="neutral" icon="🧩" />
                        <StatCard title="PATTERNS DETECTED" value={metrics.patterns_detected} trend="Rising" color="cyan" icon="🔍" />
                        <StatCard title="INSIGHTS GENERATED" value={metrics.insights_generated} trend="New findings" color="emerald" icon="💡" />
                        <StatCard title="CRITICAL FLAGS" value={metrics.critical_flags} trend={metrics.critical_flags > 0 ? "Issues found" : "Clean"} color="amber" icon="⚠️" />
                    </div>

                    <div className="grid grid-cols-12 gap-6 flex-1 min-h-0">
                        {/* AI REASONING CHAIN */}
                        <div className="col-span-12 lg:col-span-7 bg-dashboard-card rounded-lg border border-dashboard-border/50 flex flex-col shadow-sm overflow-hidden">
                            {/* ... Header ... */}
                            <div className="p-4 border-b border-dashboard-border/50 flex justify-between items-center bg-dashboard-card">
                                <h3 className="font-bold text-text-primary text-xs uppercase tracking-widest">AI Reasoning Chain</h3>
                                <div className="flex gap-2">
                                    <span className={`w-2 h-2 rounded-full ${isAnalysisRunning ? 'bg-accent-primary animate-pulse' : 'bg-dashboard-border'}`}></span>
                                </div>
                            </div>
                            <div className="flex-1 overflow-y-auto p-4 space-y-3 bg-dashboard-bg/20">
                                {feed.map(item => (
                                    <div
                                        key={item.id}
                                        onClick={() => setFocusedThoughtId(focusedThoughtId === item.id ? null : item.id)}
                                        className={`rounded-lg transition-all cursor-pointer group animate-fade-in-up ${focusedThoughtId === item.id
                                            ? 'bg-blue-900/40 border border-blue-500/50 shadow-[0_0_15px_rgba(59,130,246,0.2)]'
                                            : 'border border-transparent hover:bg-white/[0.03]'
                                            } ${item.parentId ? 'ml-6 border-l-2 border-l-dashboard-border/50 pl-4 py-2' : 'p-3 my-1'}`}
                                    >
                                        {/* TOOL USE ITEM */}
                                        {item.stepType === 'tool_use' ? (
                                            <div className="flex items-start gap-3 text-xs bg-black/20 p-2 rounded border border-white/5 font-mono text-cyan-300/90">
                                                <span className="mt-0.5">🔧</span>
                                                <div className="flex flex-col gap-1 w-full">
                                                    <div className="flex justify-between w-full">
                                                        <span className="font-bold">TOOL: {item.tools?.[0] || 'Unknown'}</span>
                                                        <span className="text-[9px] opacity-50">{item.timestamp}</span>
                                                    </div>
                                                    <span className="text-white/60">{item.content}</span>
                                                </div>
                                            </div>
                                        ) : (
                                            /* STANDARD THOUGHT / PLAN / ACTION */
                                            <>
                                                <div className="flex justify-between items-center mb-1">
                                                    <div className="flex items-center gap-2">
                                                        <span className={`text-[10px] font-bold uppercase tracking-wider ${item.stepType === 'plan' ? 'text-purple-400' :
                                                            item.stepType === 'action' ? 'text-amber-400' :
                                                                item.stepType === 'observation' ? 'text-emerald-400' :
                                                                    'text-blue-400'
                                                            }`}>
                                                            {item.stepType?.toUpperCase() || 'THOUGHT'}
                                                        </span>
                                                        <span className="text-[10px] text-cyan-200/60 font-mono tracking-tight">{item.author}</span>
                                                        <span className="text-[10px] text-text-muted opacity-50">{item.timestamp}</span>
                                                    </div>
                                                    <StatusBadge type={item.badge} />
                                                </div>
                                                <div className={`text-xs whitespace-pre-wrap font-mono leading-relaxed transition-colors ${focusedThoughtId === item.id
                                                    ? 'text-white'
                                                    : 'text-text-primary opacity-90'
                                                    }`}>
                                                    {item.content}
                                                </div>
                                                {/* Related Docs Pill */}
                                                {item.relatedDocIds && item.relatedDocIds.length > 0 && (
                                                    <div className="mt-2 flex gap-1 flex-wrap">
                                                        {item.relatedDocIds.map(docId => (
                                                            <span key={docId} className="px-1.5 py-0.5 rounded bg-white/5 border border-white/10 text-[9px] text-text-muted font-mono hover:text-white hover:border-white/30 transition-colors">
                                                                📄 {docId}
                                                            </span>
                                                        ))}
                                                    </div>
                                                )}
                                            </>
                                        )}
                                    </div>
                                ))}
                                <div ref={messagesEndRef} />
                            </div>
                        </div>

                        {/* DATA SOURCES GRID */}
                        <div className="col-span-12 lg:col-span-5 bg-dashboard-card rounded-lg border border-dashboard-border/50 flex flex-col shadow-sm overflow-hidden">
                            {/* ... Header ... */}
                            <div className="p-4 border-b border-dashboard-border/50 flex flex-col gap-3 bg-dashboard-card z-10">
                                <div className="flex justify-between items-center">
                                    <h3 className="font-bold text-text-primary text-xs uppercase tracking-widest">Data Sources</h3>
                                    <div className="flex gap-4 text-xs font-mono">
                                        <span className="text-text-secondary">PROCESSED: <strong className="text-emerald-400">{worldModel.filter(i => i.status === 'vram').length}</strong> / {impactSummary?.total_documents || (tier === 'large' ? 268 : 18)}</span>
                                    </div>
                                </div>
                                {/* Filter Toolbar */}
                                <div className="flex gap-1 p-1 bg-dashboard-bg/50 rounded-lg">
                                    {['ALL', 'LIVE', 'ARCHIVE'].map(f => (
                                        <button
                                            key={f}
                                            onClick={() => setDataFilter(f as any)}
                                            className={`flex-1 py-1.5 text-[10px] font-bold rounded-md transition-all ${dataFilter === f
                                                ? 'bg-blue-600 text-white shadow-sm'
                                                : 'text-text-muted hover:text-text-primary hover:bg-white/5'
                                                }`}
                                        >
                                            {f}
                                        </button>
                                    ))}
                                </div>
                            </div>

                            <div className="flex-1 p-4 overflow-y-auto bg-dashboard-bg/30" ref={scrollContainerRef}>
                                <div className="space-y-1">
                                    {worldModel.filter(item => {
                                        if (dataFilter === 'ALL') return true;
                                        if (dataFilter === 'LIVE') return item.status === 'pending' || (isAnalysisRunning && item.status === 'vram' && worldModel.findIndex(x => x.id === item.id) === worldModel.findIndex(x => x.status === 'pending') - 1); // Show pending + just finished
                                        if (dataFilter === 'ARCHIVE') return item.status === 'vram';
                                        return true;
                                    }).map((item, i) => {
                                        // Determine if this is the "active" item (first pending item)
                                        const pendingIndex = worldModel.findIndex(x => x.status === 'pending');
                                        const isActualActive = isAnalysisRunning && item.id === worldModel[pendingIndex]?.id;
                                        const isProcessed = item.status === 'vram';

                                        return (
                                            <div
                                                key={item.id}
                                                ref={isActualActive ? activeFileRef : null}
                                                className={`px-3 py-2 rounded-lg transition-all duration-300 flex items-center justify-between border group ${isProcessed
                                                    ? 'bg-emerald-500/5 border-emerald-500/20 text-emerald-200 hover:bg-emerald-500/10'
                                                    : isActualActive
                                                        ? 'bg-blue-500/20 border-blue-500/50 text-blue-100 shadow-[0_0_15px_rgba(59,130,246,0.2)] scale-[1.02]'
                                                        : 'bg-dashboard-card/20 border-transparent text-text-muted opacity-40 hover:opacity-70'
                                                    }`}
                                            >
                                                {/* Left: Type icon and filename */}
                                                <div className="flex items-center gap-3 flex-1 min-w-0">
                                                    <div className={`w-8 h-8 rounded flex items-center justify-center text-lg ${isActualActive ? 'bg-blue-500/20 animate-bounce' : 'bg-black/20'
                                                        }`}>
                                                        {item.type === 'screenshot' ? '🖥️' : '📄'}
                                                    </div>

                                                    <div className="flex flex-col min-w-0">
                                                        <span className={`text-xs font-mono truncate ${isActualActive ? 'font-bold text-white' : ''}`}>{item.title}</span>
                                                        <div className="flex items-center gap-2 mt-0.5">
                                                            <span className={`text-[9px] font-bold px-1.5 py-px rounded ${item.type === 'screenshot'
                                                                ? 'bg-purple-500/20 text-purple-300'
                                                                : 'bg-amber-500/20 text-amber-300'
                                                                }`}>
                                                                {item.type === 'screenshot' ? 'IMG' : 'DOC'}
                                                            </span>
                                                            <span className="text-[9px] opacity-50 font-mono">{item.memorySize.toFixed(1)}KB</span>
                                                        </div>
                                                    </div>
                                                </div>

                                                {/* Right: Size and status */}
                                                <div className="flex items-center gap-3 shrink-0">
                                                    {/* Quick View Button (Visible on Hover) */}
                                                    <button className="opacity-0 group-hover:opacity-100 transition-opacity p-1.5 rounded bg-white/10 hover:bg-white/20 text-[10px] font-bold text-white">
                                                        VIEW
                                                    </button>

                                                    {isActualActive ? (
                                                        <div className="w-2 h-2 rounded-full bg-blue-500 animate-ping" />
                                                    ) : (
                                                        <div className={`w-2 h-2 rounded-full ${isProcessed
                                                            ? 'bg-emerald-500 shadow-[0_0_4px_#34d399]'
                                                            : 'bg-gray-600'
                                                            }`} />
                                                    )}
                                                </div>
                                            </div>
                                        )
                                    })}
                                </div>
                            </div>
                        </div>

                    </div>
                </div>

            </div>
        </div>
    );
};
