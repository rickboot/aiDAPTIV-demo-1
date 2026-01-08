import React, { useState } from 'react';
import { useScenario } from '../ScenarioContext';
import { SCENARIOS, SUCCESS_REPORT } from '../mockData';
import type { BadgeType } from '../types';
import { SettingsModal } from './SettingsModal';
import { AboutModal } from './AboutModal';
import { AboutAidaptivModal } from './AboutAidaptivModal';

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


const StatusBadge = ({ type }: { type: BadgeType }) => {
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
const SuccessOverlay = ({ onClose }: { onClose: () => void }) => (
    <div className="absolute inset-0 bg-dashboard-bg/95 backdrop-blur-md z-50 flex items-center justify-center animate-fade-in text-white p-8">
        <div className="max-w-4xl w-full bg-[#1e293b] border border-emerald-500/30 rounded-2xl shadow-[0_0_50px_rgba(16,185,129,0.2)] p-10 flex flex-col items-center">

            <div className="w-20 h-20 rounded-full bg-emerald-500/20 flex items-center justify-center mb-6 ring-4 ring-emerald-500/20">
                <svg className="w-10 h-10 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" /></svg>
            </div>

            <h2 className="text-3xl font-bold text-white mb-2">{SUCCESS_REPORT.title}</h2>
            <div className="text-emerald-400 font-mono text-sm tracking-widest uppercase mb-8">{SUCCESS_REPORT.mainInsight}</div>

            <div className="grid grid-cols-2 gap-10 w-full mb-10">
                <div className="space-y-4">
                    <h3 className="text-sm font-bold text-gray-400 uppercase tracking-widest border-b border-gray-700 pb-2">Key Finding</h3>
                    <p className="text-lg leading-relaxed font-light">{SUCCESS_REPORT.finding}</p>
                    <ul className="space-y-2">
                        {SUCCESS_REPORT.evidence.map((line, i) => (
                            <li key={i} className="flex items-start gap-2 text-sm text-gray-300">
                                <span className="text-emerald-500 mt-1">▸</span> {line}
                            </li>
                        ))}
                    </ul>
                </div>

                <div className="space-y-4">
                    <h3 className="text-sm font-bold text-gray-400 uppercase tracking-widest border-b border-gray-700 pb-2">Memory Performance</h3>

                    {/* MEMORY STATS */}
                    <div className="bg-black/30 p-4 rounded-xl border border-gray-700 space-y-4">
                        <div className="flex justify-between items-center">
                            <span className="text-gray-400 text-sm">Total Context</span>
                            <span className="text-white font-mono font-bold text-xl">{SUCCESS_REPORT.stats.contextProcessed}</span>
                        </div>
                        <div className="flex justify-between items-center">
                            <span className="text-gray-400 text-sm">GPU Usage</span>
                            <span className="text-amber-400 font-mono font-bold">{SUCCESS_REPORT.stats.gpuUtil} (Capped)</span>
                        </div>

                        {/* HERO METRIC */}
                        <div className="bg-[#a855f7]/20 p-3 rounded-lg border border-[#a855f7]/50 flex justify-between items-center shadow-[0_0_15px_rgba(168,85,247,0.3)]">
                            <span className="text-[#e9d5ff] font-bold text-sm">aiDAPTIV+ SSD Offload</span>
                            <span className="text-white font-mono font-bold text-xl">{SUCCESS_REPORT.stats.ssdOffload}</span>
                        </div>
                    </div>

                    <div className="text-xs text-gray-500 italic text-center">
                        Without aiDAPTIV+, analysis would have failed at 24GB.
                    </div>
                </div>
            </div>

            <div className="flex gap-4">
                <button onClick={onClose} className="px-8 py-3 rounded-xl bg-gray-700 hover:bg-gray-600 text-white font-bold shadow-lg transition-all transform hover:scale-105">
                    Close
                </button>
            </div>
        </div>
    </div>
);


export const WarRoomDisplay = () => {
    const {
        feed, worldModel, systemState, metrics, performance, currentActivity,
        isAnalysisRunning, startAnalysis, stopAnalysis,
        isSuccess, isComplete, showResults, closeResults,
        activeScenario, tier
    } = useScenario();

    return (
        <div className="flex h-screen bg-dashboard-bg font-sans overflow-hidden relative">
            <Sidebar />

            <div className="flex-1 flex flex-col h-screen overflow-hidden relative">
                {/* SUCCESS OVERLAY */}
                {isSuccess && <SuccessOverlay onClose={closeResults} />}

                {/* MAIN DASHBOARD CONTENT */}
                <div className="flex-1 overflow-y-auto p-6 space-y-6 scroll-smooth">

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
                        <StatCard title="COMPETITORS TRACKED" value={metrics.competitors} trend="Active" color="neutral" icon="🎯" />
                        <StatCard title="VISUAL UPDATES" value={metrics.visuals} trend="+127 today" color="cyan" icon="📸" />
                        <StatCard title="PAPERS ANALYZED" value={metrics.papers} trend="+18 new" color="emerald" icon="📄" />
                        <StatCard title="SIGNALS DETECTED" value={metrics.signals} trend={metrics.signals > 0 ? "Pivots found" : "Monitoring..."} color="amber" icon="⚠️" />
                    </div>

                    <div className="grid grid-cols-12 gap-6 h-[560px]">
                        {/* AI REASONING CHAIN */}
                        <div className="col-span-12 lg:col-span-7 bg-dashboard-card rounded-lg border border-dashboard-border/50 flex flex-col shadow-sm overflow-hidden">
                            {/* ... Header ... */}
                            <div className="p-4 border-b border-dashboard-border/50 flex justify-between items-center bg-dashboard-card">
                                <h3 className="font-bold text-text-primary text-xs uppercase tracking-widest">AI Reasoning Chain</h3>
                                <div className="flex gap-2">
                                    <span className={`w-2 h-2 rounded-full ${isAnalysisRunning ? 'bg-accent-primary animate-pulse' : 'bg-dashboard-border'}`}></span>
                                </div>
                            </div>
                            <div className="flex-1 overflow-y-auto p-4 space-y-3 bg-dashboard-bg/20 scroll-smooth flex flex-col-reverse"> {/* Reverse col for auto scroll (naive) - actually mapped order matters */}
                                {/* Map normal order, assuming new items unshift to top in Context */}
                                {feed.map(item => (
                                    <div key={item.id} className="p-4 rounded-lg border border-dashboard-border/50 bg-dashboard-card/80 hover:bg-white/[0.03] transition-colors group shadow-sm animate-fade-in-up">
                                        {/* ... Item content ... */}
                                        <div className="flex justify-between items-center mb-2">
                                            <div className="flex items-center gap-2">
                                                <span className="text-xs font-bold text-blue-400">{item.author}</span>
                                                <span className="text-[10px] text-text-muted">{item.timestamp}</span>
                                            </div>
                                            <StatusBadge type={item.badge} />
                                        </div>
                                        <div className="text-xs text-text-primary whitespace-pre-wrap font-mono leading-relaxed opacity-90 pl-2 border-l-2 border-dashboard-border group-hover:border-accent-primary transition-colors">
                                            {item.content}
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>

                        {/* DATA SOURCES GRID */}
                        <div className="col-span-12 lg:col-span-5 bg-dashboard-card rounded-lg border border-dashboard-border/50 flex flex-col shadow-sm overflow-hidden">
                            {/* ... Header ... */}
                            <div className="p-4 border-b border-dashboard-border/50 flex justify-between items-center bg-dashboard-card">
                                <h3 className="font-bold text-text-primary text-xs uppercase tracking-widest">Data Sources</h3>
                                <div className="flex gap-4 text-xs font-mono">
                                    <span className="text-text-secondary">PROCESSED: <strong className="text-emerald-400">{worldModel.filter(i => i.status === 'vram').length}</strong> / 96</span>
                                </div>
                            </div>

                            <div className="flex-1 p-4 overflow-y-auto bg-dashboard-bg/30">
                                <div className="space-y-1">
                                    {worldModel.map((item, i) => (
                                        <div
                                            key={item.id}
                                            className={`px-3 py-2 rounded-lg transition-all duration-300 flex items-center justify-between border ${item.status === 'vram'
                                                ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-200'
                                                : 'bg-dashboard-card/20 border-transparent text-text-muted opacity-50'
                                                } ${isAnalysisRunning && item.status === 'pending' && i === worldModel.findIndex(x => x.status === 'pending')
                                                    ? '!opacity-100 !bg-blue-500/10 !border-blue-500/50 !text-blue-200 shadow-[0_0_10px_rgba(59,130,246,0.3)]'
                                                    : ''
                                                }`}
                                        >
                                            {/* Left: Type icon and filename */}
                                            <div className="flex items-center gap-2 flex-1 min-w-0">
                                                <span className="text-base shrink-0">
                                                    {item.type === 'screenshot' ? '🖥️' : '📄'}
                                                </span>
                                                <div className="flex flex-col min-w-0">
                                                    <span className="text-xs font-mono truncate">{item.title}</span>
                                                    <span className="text-[10px] opacity-60">
                                                        {item.type === 'screenshot' ? 'Visual' : 'Document'}
                                                    </span>
                                                </div>
                                            </div>

                                            {/* Right: Size and status */}
                                            <div className="flex items-center gap-3 shrink-0">
                                                <span className="text-[10px] font-mono opacity-70">
                                                    {item.memorySize.toFixed(1)}KB
                                                </span>
                                                <div className={`w-2 h-2 rounded-full ${item.status === 'vram'
                                                    ? 'bg-emerald-500 shadow-[0_0_4px_#34d399]'
                                                    : 'bg-gray-600'
                                                    }`} />
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        </div>

                    </div>
                </div>

            </div>
        </div>
    );
};

const StatCard = ({ title, value, trend, color, icon }: any) => {

    const colors: any = {
        cyan: 'text-cyan-400',
        emerald: 'text-emerald-400',
        amber: 'text-amber-400',
        neutral: 'text-white'
    };

    return (
        <div className="bg-dashboard-card p-2.5 rounded-lg border border-dashboard-border/50 shadow-sm relative overflow-hidden group hover:-translate-y-0.5 transition-transform duration-300">
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
