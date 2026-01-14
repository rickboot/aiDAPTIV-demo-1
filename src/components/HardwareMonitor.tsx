import React, { useEffect, useState, useRef } from 'react';
import { useScenario } from '../ScenarioContext';

export const HardwareMonitor = () => {
    const { systemState, performance, toggleAidaptiv, showHardwareMonitor, crashDetails, tier, toggleMonitor } = useScenario();

    // Local state for smooth fade-in/out
    const [visible, setVisible] = useState(false);

    // Draggable Logic
    const [position, setPosition] = useState({ x: -1, y: -1 }); // -1 indicates not set (use default)
    const [isDragging, setIsDragging] = useState(false);
    const dragOffset = useRef({ x: 0, y: 0 });

    // 1. Load position from storage on mount
    useEffect(() => {
        const savedPos = localStorage.getItem('telemetry_pos');
        if (savedPos) {
            try {
                setPosition(JSON.parse(savedPos));
            } catch (e) { console.error("Failed to parse telemetry pos", e); }
        } else {
            // Default bottom-right (calculated roughly)
            // We'll let CSS handle the initial position if state is -1, then capture it on first drag
            // OR simpler: just set a default that matches "bottom-6 right-6"
            setPosition({
                x: window.innerWidth - 320, // 288px width + padding
                y: window.innerHeight - 500 // rough height
            });
        }
    }, []);

    // 2. Visibility Timer
    useEffect(() => {
        if (showHardwareMonitor) {
            setVisible(true);
        } else {
            const timer = setTimeout(() => setVisible(false), 300); // Wait for fade out
            return () => clearTimeout(timer);
        }
    }, [showHardwareMonitor]);

    // 3. Drag Handlers
    const handleMouseDown = (e: React.MouseEvent) => {
        setIsDragging(true);
        // Calculate offset from the top-left of the element
        dragOffset.current = {
            x: e.clientX - position.x,
            y: e.clientY - position.y
        };
    };

    const handleMouseMove = (e: MouseEvent) => {
        if (!isDragging) return;
        const newX = e.clientX - dragOffset.current.x;
        const newY = e.clientY - dragOffset.current.y;
        setPosition({ x: newX, y: newY });
    };

    const handleMouseUp = () => {
        if (isDragging) {
            setIsDragging(false);
            localStorage.setItem('telemetry_pos', JSON.stringify(position));
        }
    };

    // Global mouse listeners for drag
    useEffect(() => {
        if (isDragging) {
            window.addEventListener('mousemove', handleMouseMove);
            window.addEventListener('mouseup', handleMouseUp);
        } else {
            window.removeEventListener('mousemove', handleMouseMove);
            window.removeEventListener('mouseup', handleMouseUp);
        }
        return () => {
            window.removeEventListener('mousemove', handleMouseMove);
            window.removeEventListener('mouseup', handleMouseUp);
        };
    }, [isDragging, position]); // Re-bind with latest position if needed, though ref implies we don't need pos in dep


    const { impactSummary, worldModel, isAnalysisRunning, totalDocuments } = useScenario();
    const {
        documents_processed: impactProcessed = 0,
        total_documents: impactTotal = 0,
        memory_saved_gb = 0,
        estimated_cost_local = 0,
        estimated_cost_cloud = 0,
        time_minutes = 0,
        time_without_aidaptiv = 0
    } = impactSummary || {};

    // Use world model to get live counts if impactSummary isn't ready
    const liveProcessed = worldModel.filter(d => d.status === 'vram').length;
    const liveTotal = worldModel.length;

    const displayProcessed = impactSummary ? impactProcessed : liveProcessed;
    const displayTotal = impactSummary ? impactTotal : liveTotal;


    // If we shouldn't render at all yet (for initial load)
    if (!showHardwareMonitor && !visible) return null;

    // Use dynamic total memory from backend (psutil), defaulting to 16 if not set
    const totalMem = systemState.totalMemory || 16;

    const vramPercent = Math.min((systemState.vramUsage / totalMem) * 100, 100);
    const isCritical = vramPercent > 95;
    const isOOM = systemState.vramUsage >= totalMem;
    // SSD logic triggers when VRAM is "full" or close to it
    const ssdThreshold = totalMem * 0.9;
    const isSsdReady = systemState.isAidaptivEnabled && systemState.vramUsage < ssdThreshold;
    const isSsdActive = systemState.isAidaptivEnabled && systemState.vramUsage >= ssdThreshold;

    return (
        <div
            style={{
                left: position.x === -1 ? undefined : position.x,
                top: position.y === -1 ? undefined : position.y,
                right: position.x === -1 ? '1.5rem' : 'auto', // Fallback to right-6
                bottom: position.y === -1 ? '1.5rem' : 'auto' // Fallback to bottom-6
            }}
            className={`fixed w-64 z-50 transition-opacity duration-300 ease-in-out ${showHardwareMonitor ? 'opacity-100' : 'opacity-0'} ${isDragging ? 'cursor-grabbing select-none' : ''}`}
        >
            <div className="bg-dashboard-card border border-dashboard-border shadow-[0_0_30px_rgba(0,0,0,0.3)] rounded-lg backdrop-blur-sm overflow-hidden">

                {/* Header - DRAGGABLE HANDLE */}
                <div
                    onMouseDown={handleMouseDown}
                    className="bg-black/20 px-3 py-2 flex justify-between items-center border-b border-dashboard-border/50 cursor-grab active:cursor-grabbing text-text-primary hover:text-white transition-colors"
                >
                    <div className="flex items-center gap-2">
                        <svg className="w-3 h-3 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 8h16M4 16h16" /></svg>
                        <span className="text-sm font-bold">System Telemetry</span>
                    </div>

                    <div className="flex items-center gap-3">
                        <div className="flex items-center gap-2">
                            <span className={`w-2 h-2 rounded-full ${systemState.isAidaptivEnabled ? 'bg-accent-success animate-pulse' : 'bg-text-muted'}`}></span>
                            <span className="text-[10px] text-text-muted font-mono tracking-wider">LIVE</span>
                        </div>
                        {/* Close Button */}
                        <button
                            onMouseDown={(e) => e.stopPropagation()} // Prevent drag start
                            onClick={toggleMonitor}
                            className="text-text-muted hover:text-white transition-colors p-1 rounded hover:bg-white/10"
                        >
                            <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" /></svg>
                        </button>
                    </div>
                </div>

                <div className="p-4 pt-5">
                    {/* 1. PRIMARY MEMORY (Generic Label) */}
                    <div className="mb-6">
                        <div className="flex justify-between items-end mb-1">
                            {/* Agnostic Label: "Memory Usage" or "System Memory" covers generic PC/Mac */}
                            <span className="text-[10px] uppercase font-bold text-text-secondary tracking-wider">System Memory</span>
                            <span className={`text-xs font-mono ${isCritical ? 'text-accent-danger font-bold' : 'text-text-primary'}`}>
                                {Math.min(systemState.vramUsage, totalMem).toFixed(1)} / {totalMem.toFixed(1)} GB
                            </span>
                        </div>
                        <div className="h-2 w-full bg-dashboard-bg rounded-md overflow-hidden border border-white/5">
                            <div
                                className={`h-full rounded-sm transition-all duration-300 ${isCritical ? 'bg-accent-danger' : 'bg-accent-success'}`}
                                style={{ width: `${vramPercent}%` }}
                            />
                        </div>
                    </div>

                    {/* REMOVED REDUNDANT SYSTEM RAM BAR */}

                    {/* 3. SSD CACHE (Dynamic Logic) */}
                    <div className="mb-6">
                        <div className="flex justify-between items-end mb-1">
                            <span className="text-[10px] uppercase font-bold text-text-secondary tracking-wider">SSD Cache (aiDAPTIV+)</span>

                            {/* Dynamic Status Text */}
                            {!systemState.isAidaptivEnabled && (
                                <span className="text-[10px] text-text-muted italic">Disabled</span>
                            )}
                            {isSsdReady && (
                                <span className="text-[10px] text-[#a855f7] font-semibold">0.0 GB (Standby)</span>
                            )}
                            {isSsdActive && (
                                <span className="text-xs font-mono text-[#a855f7] font-bold animate-pulse">
                                    {systemState.ssdUsage.toFixed(1)} GB (Flowing)
                                </span>
                            )}
                        </div>

                        <div className="h-2 w-full bg-dashboard-bg rounded-md overflow-hidden border border-white/5 relative">
                            {/* Bar */}
                            <div
                                className={`h-full rounded-sm transition-all duration-300 relative overflow-hidden ${!systemState.isAidaptivEnabled ? 'w-0' :
                                    isSsdReady ? 'w-full opacity-20 bg-[#a855f7]' : // Ghost bar when ready
                                        'bg-gradient-to-r from-[#8b5cf6] to-[#7c3aed] animate-flow-stripe' // Flowing when active
                                    }`}
                                style={{
                                    width: isSsdReady ? '100%' : `${Math.min(systemState.ssdUsage, 100)}%`
                                }}
                            />
                        </div>
                    </div>

                    {/* 4. PERFORMANCE METRICS */}
                    <div className="pt-4 border-t border-dashboard-border/30">
                        <div className="text-[10px] uppercase font-bold text-text-secondary tracking-wider mb-3">LLM Performance</div>

                        <div className="space-y-2">
                            {/* TTFT */}
                            <div className="flex justify-between items-center">
                                <span className="text-[9px] text-text-muted uppercase tracking-wide">TTFT</span>
                                <span className={`text-xs font-mono font-semibold ${performance.ttft_ms < 500 ? 'text-emerald-400' :
                                    performance.ttft_ms < 1000 ? 'text-amber-400' : 'text-red-400'
                                    }`}>
                                    {performance.ttft_ms}ms
                                </span>
                            </div>

                            {/* Tokens/sec */}
                            <div className="flex justify-between items-center">
                                <span className="text-[9px] text-text-muted uppercase tracking-wide">Speed</span>
                                <span className={`text-xs font-mono font-semibold ${performance.tokens_per_second > 35 ? 'text-emerald-400' :
                                    performance.tokens_per_second > 20 ? 'text-amber-400' : 'text-red-400'
                                    }`}>
                                    {performance.tokens_per_second.toFixed(1)} tok/s
                                </span>
                            </div>

                            {/* Latency */}
                            <div className="flex justify-between items-center">
                                <span className="text-[9px] text-text-muted uppercase tracking-wide">Latency</span>
                                <span className={`text-xs font-mono font-semibold ${performance.latency_ms < 30 ? 'text-emerald-400' :
                                    performance.latency_ms < 60 ? 'text-amber-400' : 'text-red-400'
                                    }`}>
                                    {performance.latency_ms}ms
                                </span>
                            </div>

                            {/* Status Badge */}
                            <div className="flex justify-between items-center pt-1">
                                <span className="text-[9px] text-text-muted uppercase tracking-wide">Status</span>
                                <span className={`text-[9px] font-bold uppercase px-2 py-0.5 rounded ${performance.status === 'optimal' ? 'bg-emerald-500/20 text-emerald-400' :
                                    performance.status === 'degraded' ? 'bg-amber-500/20 text-amber-400' :
                                        'bg-red-500/20 text-red-400'
                                    }`}>
                                    {performance.status}
                                </span>
                            </div>

                            {/* Elapsed Time */}
                            <div className="flex justify-between items-center pt-1">
                                <span className="text-[9px] text-text-muted uppercase tracking-wide">Elapsed</span>
                                <span className="text-xs font-mono font-semibold text-cyan-400">
                                    {Math.floor((useScenario().elapsedSeconds || 0) / 60)}:{String((useScenario().elapsedSeconds || 0) % 60).padStart(2, '0')}
                                </span>
                            </div>
                        </div>
                    </div>

                    {/* 5. CONTEXT & KV CACHE */}
                    <div className="pt-4 border-t border-dashboard-border/30 mt-4">
                        <div className="flex justify-between items-center mb-3">
                            <div className="text-[10px] uppercase font-bold text-text-secondary tracking-wider">Context & Cache</div>
                            {isAnalysisRunning && displayTotal > 0 && (
                                <div className="text-[9px] font-mono text-emerald-400">
                                    {(displayProcessed / displayTotal * 100).toFixed(0)}% Ingested
                                </div>
                            )}
                        </div>
                        <div className="space-y-2">
                            {/* Loaded Model */}
                            {systemState.loaded_model && (
                                <div className="flex justify-between items-center">
                                    <span className="text-[9px] text-text-muted uppercase tracking-wide">Loaded Model</span>
                                    <span className="text-xs font-mono font-semibold text-purple-400">
                                        {systemState.loaded_model}
                                    </span>
                                </div>
                            )}

                            {/* Context Size */}
                            <div className="flex justify-between items-center">
                                <span className="text-[9px] text-text-muted uppercase tracking-wide">Context</span>
                                <span className="text-xs font-mono font-semibold text-purple-400">
                                    {(systemState.context_tokens || 0).toLocaleString()} tokens
                                </span>
                            </div>

                            {/* KV Cache */}
                            <div className="flex justify-between items-center">
                                <span className="text-[9px] text-text-muted uppercase tracking-wide">KV Cache</span>
                                <span className="text-xs font-mono font-semibold text-purple-400">
                                    {(systemState.kv_cache_gb || 0).toFixed(2)} GB
                                </span>
                            </div>

                            {/* Model Weights */}
                            <div className="flex justify-between items-center">
                                <span className="text-[9px] text-text-muted uppercase tracking-wide">Model</span>
                                <span className="text-xs font-mono font-semibold text-blue-400">
                                    {(systemState.model_weights_gb || 0).toFixed(1)} GB
                                </span>
                            </div>

                            {/* Memory Breakdown Bar */}
                            <div className="pt-1">
                                <div className="h-1.5 bg-dashboard-bg rounded-full overflow-hidden flex">
                                    <div
                                        className="bg-blue-500"
                                        style={{ width: `${(((systemState as any).model_weights_gb || 0) / totalMem) * 100}%` }}
                                        title="Model Weights"
                                    />
                                    <div
                                        className="bg-purple-500"
                                        style={{ width: `${(((systemState as any).kv_cache_gb || 0) / totalMem) * 100}%` }}
                                        title="KV Cache"
                                    />
                                </div>
                                <div className="flex gap-3 mt-1">
                                    <div className="flex items-center gap-1">
                                        <div className="w-2 h-2 bg-blue-500 rounded-sm"></div>
                                        <span className="text-[8px] text-text-muted">Model</span>
                                    </div>
                                    <div className="flex items-center gap-1">
                                        <div className="w-2 h-2 bg-purple-500 rounded-sm"></div>
                                        <span className="text-[8px] text-text-muted">Cache</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* 6. aiDAPTIV+ IMPACT (Business Metrics) */}
                    <div className="pt-4 border-t border-dashboard-border/30 mt-4">
                        <div className="text-[10px] uppercase font-bold text-text-secondary tracking-wider mb-3">aiDAPTIV+ Impact</div>

                        <div className="space-y-2">
                            {/* Cost Savings */}
                            <div className="flex justify-between items-center">
                                <span className="text-[9px] text-text-muted uppercase tracking-wide">Cloud Cost Saved</span>
                                <span className="text-xs font-mono font-semibold text-emerald-400">
                                    ${(estimated_cost_cloud - estimated_cost_local).toFixed(2)}
                                </span>
                            </div>

                            {/* Speed Gain */}
                            <div className="flex justify-between items-center">
                                <span className="text-[9px] text-text-muted uppercase tracking-wide">Time Saved</span>
                                <span className="text-xs font-mono font-semibold text-blue-400">
                                    {tier === 'large' && systemState.isAidaptivEnabled && impactSummary
                                        ? `${(time_without_aidaptiv - time_minutes).toFixed(1)}m`
                                        : '0.0m'}
                                </span>
                            </div>

                            {/* Offloaded Data */}
                            <div className="flex justify-between items-center">
                                <span className="text-[9px] text-text-muted uppercase tracking-wide">SSD Offload</span>
                                <span className="text-xs font-mono font-semibold text-amber-400">
                                    {memory_saved_gb.toFixed(1)} GB
                                </span>
                            </div>

                        </div>
                    </div>

                    {/* OOM OVERLAY (Crash Screen) */}
                    {isOOM && !systemState.isAidaptivEnabled && (
                        <div className="absolute inset-0 bg-dashboard-card/95 backdrop-blur flex flex-col items-center justify-center p-4 border-2 border-accent-danger rounded-lg z-20">
                            <div className="text-5xl mb-2 animate-bounce">⚠️</div>
                            <div className="text-accent-danger font-black text-2xl mb-1 tracking-widest text-center uppercase">Out of Memory</div>

                            <div className="space-y-2 w-full mb-4">
                                <div className="bg-black/40 p-2 rounded border border-white/10">
                                    <div className="flex justify-between text-xs mb-1">
                                        <span className="text-text-secondary">Progress</span>
                                        <span className="text-text-primary">
                                            {crashDetails?.processed_documents || 0} / {crashDetails?.total_documents || totalDocuments || worldModel.length} Docs
                                        </span>
                                    </div>
                                    <div className="h-1.5 w-full bg-dashboard-bg rounded-full overflow-hidden">
                                        <div
                                            className="h-full bg-red-500 transition-all duration-1000"
                                            style={{ width: `${((crashDetails?.processed_documents || 0) / (crashDetails?.total_documents || 1)) * 100}%` }}
                                        ></div>
                                    </div>
                                </div>

                                <div className="bg-black/40 p-2 rounded border border-white/10">
                                    <div className="flex justify-between text-xs">
                                        <span className="text-text-secondary">VRAM</span>
                                        <span className="text-red-400 font-bold">16.1 GB (CRITICAL)</span>
                                    </div>
                                </div>
                            </div>

                            <div className="text-text-muted text-[10px] text-center mb-4">
                                Workload requires ~{crashDetails?.required_vram_gb || 32}GB VRAM.<br />
                                Hardware limit exceeded.
                            </div>

                            <button
                                onClick={() => {
                                    toggleAidaptiv();
                                    // We might want to trigger a reset/restart here,
                                    // but for now just toggling will imply the user should try again
                                }}
                                className="bg-accent-success hover:bg-emerald-400 text-white text-xs font-bold py-2 px-4 rounded shadow-[0_0_15px_rgba(16,185,129,0.4)] animate-pulse flex items-center gap-2 transition-colors"
                            >
                                <span>⚡</span> ENABLE aiDAPTIV+
                            </button>
                        </div>
                    )}

                </div> {/* End Content Body */}
            </div>
        </div>
    );
};
