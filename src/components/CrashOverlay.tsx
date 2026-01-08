import React from 'react';
import { useScenario } from '../ScenarioContext';

export const CrashOverlay = () => {
    const { crashDetails, toggleAidaptiv, resetAnalysis } = useScenario();

    if (!crashDetails) return null;

    return (
        <div className="absolute inset-0 z-50 bg-black/90 flex flex-col items-center justify-center p-8 backdrop-blur-md animate-fade-in">
            {/* Warning Icon & Header */}
            <div className="flex flex-col items-center mb-8 animate-bounce-short">
                <div className="w-24 h-24 rounded-full bg-red-500/20 flex items-center justify-center border-4 border-red-500 shadow-[0_0_50px_rgba(239,68,68,0.5)] mb-6">
                    <svg className="w-12 h-12 text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                    </svg>
                </div>
                <h1 className="text-5xl font-black text-white tracking-tight mb-2 uppercase">System Failure</h1>
                <p className="text-xl text-red-400 font-mono tracking-widest uppercase">{crashDetails.reason || "Out of Memory Exception"}</p>
            </div>

            {/* Stats Grid */}
            <div className="grid grid-cols-3 gap-6 w-full max-w-4xl mb-10">
                {/* Processed Docs */}
                <div className="bg-white/5 border border-white/10 p-6 rounded-2xl flex flex-col items-center text-center backdrop-blur-sm">
                    <span className="text-xs text-gray-400 uppercase tracking-widest font-bold mb-2">Progress Halted</span>
                    <span className="text-4xl font-bold text-white mb-1">
                        {crashDetails.processed_documents}<span className="text-gray-500 text-2xl">/{crashDetails.total_documents}</span>
                    </span>
                    <span className="text-sm text-gray-500">Documents Processed</span>
                </div>

                {/* VRAM Usage */}
                <div className="bg-red-500/10 border border-red-500/30 p-6 rounded-2xl flex flex-col items-center text-center shadow-[0_0_30px_rgba(239,68,68,0.1)]">
                    <span className="text-xs text-red-400 uppercase tracking-widest font-bold mb-2">VRAM Critical</span>
                    <span className="text-4xl font-bold text-red-500 mb-1">
                        {crashDetails.memory_snapshot.unified_gb.toFixed(1)}<span className="text-sm align-top ml-1">GB</span>
                    </span>
                    <span className="text-sm text-red-300">Memory Limit Exceeded</span>
                </div>

                {/* Required */}
                <div className="bg-white/5 border border-white/10 p-6 rounded-2xl flex flex-col items-center text-center backdrop-blur-sm">
                    <span className="text-xs text-gray-400 uppercase tracking-widest font-bold mb-2">Required Capacity</span>
                    <span className="text-4xl font-bold text-white mb-1">
                        ~{crashDetails.required_vram_gb.toFixed(0)}<span className="text-sm align-top ml-1">GB</span>
                    </span>
                    <span className="text-sm text-gray-500">Estimated Workload</span>
                </div>
            </div>

            {/* Actions */}
            <div className="flex flex-col items-center gap-4">
                <button
                    onClick={() => {
                        toggleAidaptiv();
                        resetAnalysis();
                    }}
                    className="group relative px-10 py-5 bg-gradient-to-r from-emerald-600 to-teal-600 rounded-xl shadow-lg hover:shadow-emerald-500/30 transition-all transform hover:scale-105 active:scale-95"
                >
                    <div className="absolute inset-0 bg-white/20 rounded-xl opacity-0 group-hover:opacity-100 transition-opacity" />
                    <div className="flex items-center gap-3">
                        <span className="text-2xl">⚡</span>
                        <div className="flex flex-col items-start">
                            <span className="text-xs font-bold text-emerald-100 uppercase tracking-wider">Recommended Solution</span>
                            <span className="text-2xl font-bold text-white tracking-wide">Enable aiDAPTIV+</span>
                        </div>
                    </div>
                </button>

                <button
                    onClick={resetAnalysis}
                    className="text-gray-500 hover:text-white transition-colors text-sm font-medium mt-4 border-b border-transparent hover:border-gray-500 pb-0.5"
                >
                    Reset & Try Again
                </button>
            </div>
        </div>
    );
};
