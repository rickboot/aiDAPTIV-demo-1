import React, { useEffect, useState } from 'react';
import { useScenario } from '../ScenarioContext';

export const HardwareMonitor = () => {
    const { systemState, performance, toggleAidaptiv, showHardwareMonitor, isSimulationRunning } = useScenario();

    // Local state for smooth fade-in/out
    const [visible, setVisible] = useState(false);

    useEffect(() => {
        if (showHardwareMonitor) {
            setVisible(true);
        } else {
            const timer = setTimeout(() => setVisible(false), 300); // Wait for fade out
            return () => clearTimeout(timer);
        }
    }, [showHardwareMonitor]);


    const vramPercent = Math.min((systemState.vramUsage / 24) * 100, 100);
    const isCritical = vramPercent > 98;
    const isOOM = systemState.vramUsage >= 24.1; // Check new crash state

    // Render logic for SSD Bar
    const isSsdReady = systemState.isAidaptivEnabled && systemState.vramUsage < 21.6; // <90%
    const isSsdActive = systemState.isAidaptivEnabled && systemState.vramUsage >= 21.6; // >=90%

    // If we shouldn't render at all yet (for initial load)
    if (!showHardwareMonitor && !visible) return null;

    return (
        <div className={`fixed right-6 bottom-6 w-72 z-50 transition-opacity duration-300 ease-in-out ${showHardwareMonitor ? 'opacity-100' : 'opacity-0'}`}>
            <div className="bg-dashboard-card border border-dashboard-border shadow-[0_0_30px_rgba(0,0,0,0.3)] rounded-lg p-5 backdrop-blur-sm">

                {/* Header */}
                <div className="flex justify-between items-center mb-4 border-b border-dashboard-border/50 pb-3">
                    <span className="text-sm font-bold text-text-primary">System Telemetry</span>
                    <div className="flex items-center gap-2">
                        <span className={`w-2 h-2 rounded-full ${systemState.isAidaptivEnabled ? 'bg-accent-success animate-pulse' : 'bg-text-muted'}`}></span>
                        <span className="text-[10px] text-text-muted font-mono tracking-wider">LIVE TELEMETRY</span>
                    </div>
                </div>

                {/* 1. GPU MEMORY */}
                <div className="mb-4">
                    <div className="flex justify-between items-end mb-1">
                        <span className="text-[10px] uppercase font-bold text-text-secondary tracking-wider">GPU Memory</span>
                        <span className={`text-xs font-mono ${isCritical ? 'text-accent-danger font-bold' : 'text-text-primary'}`}>
                            {Math.min(systemState.vramUsage, 24).toFixed(1)} / 24.0 GB
                        </span>
                    </div>
                    <div className="h-2 w-full bg-dashboard-bg rounded-md overflow-hidden border border-white/5">
                        <div
                            className={`h-full rounded-sm transition-all duration-300 ${isCritical ? 'bg-accent-danger' : 'bg-accent-success'}`}
                            style={{ width: `${vramPercent}%` }}
                        />
                    </div>
                </div>

                {/* 2. SYSTEM RAM */}
                <div className="mb-4">
                    <div className="flex justify-between items-end mb-1">
                        <span className="text-[10px] uppercase font-bold text-text-secondary tracking-wider">System RAM</span>
                        <span className="text-xs font-mono text-text-primary">
                            {(systemState.ramUsage || 16).toFixed(1)} / 128.0 GB
                        </span>
                    </div>
                    <div className="h-2 w-full bg-dashboard-bg rounded-md overflow-hidden border border-white/5">
                        <div
                            className="h-full rounded-sm bg-accent-warning transition-all duration-300"
                            style={{ width: `${Math.min(((systemState.ramUsage || 16) / 128) * 100, 100)}%` }}
                        />
                    </div>
                </div>

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
                    </div>
                </div>

                {/* OOM OVERLAY (Crash Screen) */}
                {isOOM && !systemState.isAidaptivEnabled && (
                    <div className="absolute inset-0 bg-dashboard-card/95 backdrop-blur flex flex-col items-center justify-center p-4 border-2 border-accent-danger rounded-lg z-20 animate-pulse">
                        <div className="text-5xl mb-2">⚠️</div>
                        <div className="text-accent-danger font-black text-2xl mb-1 tracking-widest text-center uppercase">Out of Memory</div>
                        <div className="text-text-primary text-xs text-center uppercase tracking-wide px-4">
                            CUDA Kernel Terminated<br />Workload Exceeded VRAM
                        </div>
                    </div>
                )}

            </div>
        </div>
    );
};
