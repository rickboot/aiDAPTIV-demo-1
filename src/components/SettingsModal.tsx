import { useScenario } from '../ScenarioContext';

interface SettingsModalProps {
    isOpen: boolean;
    onClose: () => void;
}

export const SettingsModal = ({ isOpen, onClose }: SettingsModalProps) => {
    const { tier, setTier, isAnalysisRunning, toggleAidaptiv, systemState } = useScenario();

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center animate-fade-in" onClick={onClose}>
            <div className="bg-[#1e293b] border border-dashboard-border rounded-2xl shadow-2xl w-full max-w-2xl p-8 m-4" onClick={(e) => e.stopPropagation()}>

                {/* Header */}
                <div className="flex justify-between items-center mb-6 pb-4 border-b border-dashboard-border/50">
                    <h2 className="text-2xl font-bold text-white">Settings</h2>
                    <button
                        onClick={onClose}
                        className="w-8 h-8 rounded-lg hover:bg-white/10 flex items-center justify-center text-text-secondary hover:text-white transition-colors"
                    >
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                        </svg>
                    </button>
                </div>

                {/* Content */}
                <div className="space-y-6">

                    {/* Simulation Tier */}
                    <div>
                        <label className="block text-sm font-bold text-text-secondary uppercase tracking-widest mb-3">
                            Simulation Tier
                        </label>
                        <div className="grid grid-cols-2 gap-4">
                            <button
                                onClick={() => setTier('lite')}
                                disabled={isAnalysisRunning}
                                className={`p-4 rounded-xl border-2 transition-all ${tier === 'lite'
                                    ? 'border-blue-500 bg-blue-500/10 shadow-lg shadow-blue-500/20'
                                    : 'border-dashboard-border hover:border-blue-500/50 bg-dashboard-card'
                                    } ${isAnalysisRunning ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
                            >
                                <div className="flex items-center gap-3 mb-2">
                                    <div className={`w-5 h-5 rounded-full border-2 flex items-center justify-center ${tier === 'lite' ? 'border-blue-500 bg-blue-500' : 'border-text-secondary'
                                        }`}>
                                        {tier === 'lite' && (
                                            <div className="w-2 h-2 rounded-full bg-white"></div>
                                        )}
                                    </div>
                                    <span className={`font-bold ${tier === 'lite' ? 'text-white' : 'text-text-primary'}`}>
                                        Lite
                                    </span>
                                </div>
                                <div className="text-xs text-text-secondary space-y-1 text-left">
                                    <div>• 18 documents</div>
                                    <div>• 15 seconds</div>
                                    <div>• 10GB memory</div>
                                    <div className="text-emerald-400 font-semibold">✓ Always succeeds</div>
                                </div>
                            </button>

                            <button
                                onClick={() => setTier('large')}
                                disabled={isAnalysisRunning}
                                className={`p-4 rounded-xl border-2 transition-all ${tier === 'large'
                                    ? 'border-blue-500 bg-blue-500/10 shadow-lg shadow-blue-500/20'
                                    : 'border-dashboard-border hover:border-blue-500/50 bg-dashboard-card'
                                    } ${isAnalysisRunning ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
                            >
                                <div className="flex items-center gap-3 mb-2">
                                    <div className={`w-5 h-5 rounded-full border-2 flex items-center justify-center ${tier === 'large' ? 'border-blue-500 bg-blue-500' : 'border-text-secondary'
                                        }`}>
                                        {tier === 'large' && (
                                            <div className="w-2 h-2 rounded-full bg-white"></div>
                                        )}
                                    </div>
                                    <span className={`font-bold ${tier === 'large' ? 'text-white' : 'text-text-primary'}`}>
                                        Large
                                    </span>
                                </div>
                                <div className="text-xs text-text-secondary space-y-1 text-left">
                                    <div>• 268 documents</div>
                                    <div>• 30 seconds</div>
                                    <div>• 19GB memory</div>
                                    <div className="text-amber-400 font-semibold">⚠️ Requires aiDAPTIV+</div>
                                </div>
                            </button>
                        </div>
                    </div>

                    {/* aiDAPTIV+ Toggle */}
                    <div>
                        <label className="block text-sm font-bold text-text-secondary uppercase tracking-widest mb-3">
                            aiDAPTIV+ Technology
                        </label>
                        <button
                            onClick={toggleAidaptiv}
                            disabled={isAnalysisRunning}
                            className={`w-full p-4 rounded-xl border-2 transition-all flex items-center justify-between ${systemState.isAidaptivEnabled
                                ? 'border-emerald-500 bg-emerald-500/10 shadow-lg shadow-emerald-500/20'
                                : 'border-dashboard-border hover:border-emerald-500/50 bg-dashboard-card'
                                } ${isAnalysisRunning ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
                        >
                            <div className="flex items-center gap-3">
                                <div className={`w-12 h-6 rounded-full transition-all ${systemState.isAidaptivEnabled ? 'bg-emerald-500' : 'bg-gray-600'
                                    }`}>
                                    <div className={`w-5 h-5 rounded-full bg-white shadow-md transform transition-transform ${systemState.isAidaptivEnabled ? 'translate-x-6' : 'translate-x-0.5'
                                        } mt-0.5`} />
                                </div>
                                <div className="text-left">
                                    <div className={`font-bold ${systemState.isAidaptivEnabled ? 'text-white' : 'text-text-primary'}`}>
                                        {systemState.isAidaptivEnabled ? 'aiDAPTIV+ Enabled' : 'aiDAPTIV+ Disabled'}
                                    </div>
                                    <div className="text-xs text-text-secondary">
                                        {systemState.isAidaptivEnabled
                                            ? 'SSD offload active for large workloads'
                                            : 'Enable to prevent out-of-memory crashes'
                                        }
                                    </div>
                                </div>
                            </div>
                            {systemState.isAidaptivEnabled && (
                                <span className="relative flex h-3 w-3">
                                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                                    <span className="relative inline-flex rounded-full h-3 w-3 bg-emerald-400"></span>
                                </span>
                            )}
                        </button>
                    </div>

                    {/* Info Box */}
                    <div className="bg-blue-500/10 border border-blue-500/30 rounded-xl p-4">
                        <div className="flex gap-3">
                            <svg className="w-5 h-5 text-blue-400 shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                            </svg>
                            <div className="text-sm text-blue-200">
                                <div className="font-semibold mb-1">Tier Selection</div>
                                <div className="text-blue-300/80">
                                    Choose <strong>Lite</strong> for quick demos. Choose <strong>Large</strong> to showcase aiDAPTIV+ preventing out-of-memory crashes with SSD offload.
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Locked During Simulation */}
                    {isAnalysisRunning && (
                        <div className="bg-amber-500/10 border border-amber-500/30 rounded-xl p-4">
                            <div className="flex gap-3">
                                <svg className="w-5 h-5 text-amber-400 shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                                </svg>
                                <div className="text-sm text-amber-200">
                                    Settings are locked during analysis. Stop the analysis to make changes.
                                </div>
                            </div>
                        </div>
                    )}

                </div>

                {/* Footer */}
                <div className="mt-8 pt-6 border-t border-dashboard-border/50 flex justify-end">
                    <button
                        onClick={onClose}
                        className="px-6 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-bold transition-colors shadow-lg shadow-blue-500/20"
                    >
                        Done
                    </button>
                </div>

            </div>
        </div>
    );
};
