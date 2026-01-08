import { useScenario } from '../ScenarioContext';

interface ImpactMetricsProps {
    className?: string;
}

export const ImpactMetrics = ({ className = '' }: ImpactMetricsProps) => {
    const { impactSummary, tier, systemState } = useScenario();

    // Default zero state if no data yet
    const {
        documents_processed = 0,
        total_documents = 0,
        context_size_gb = 0,
        memory_saved_gb = 0,
        estimated_cost_local = 0,
        estimated_cost_cloud = 0,
        estimated_monthly_cost = 0,
        time_minutes = 0,
        time_without_aidaptiv = 0
    } = impactSummary || {};

    const isSuccess = impactSummary ? documents_processed === total_documents : true; // Default to "good" state visually before run
    const aidaptivEnabled = systemState.isAidaptivEnabled;

    return (
        <div className={`bg-gradient-to-br from-dashboard-card to-dashboard-card/80 rounded-lg border-2 ${isSuccess ? 'border-emerald-500/50' : 'border-red-500/50'} p-6 shadow-xl ${className}`}>
            {/* Header */}
            <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-bold text-text-primary uppercase tracking-wider">Analysis Impact</h3>
                <div className={`px-3 py-1 rounded-full text-xs font-bold ${isSuccess ? 'bg-emerald-500/20 text-emerald-400' : 'bg-red-500/20 text-red-400'}`}>
                    {isSuccess ? '✓ SUCCESS' : '✗ FAILED'}
                </div>
            </div>

            {/* Metrics Grid */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {/* Documents Processed */}
                <div className="bg-dashboard-bg/50 rounded-lg p-3 border border-dashboard-border/30">
                    <div className="text-[10px] text-text-muted uppercase tracking-widest mb-1">Documents</div>
                    <div className={`text-2xl font-bold ${isSuccess ? 'text-emerald-400' : 'text-red-400'}`}>
                        {documents_processed}/{total_documents}
                    </div>
                    <div className="text-[9px] text-text-secondary mt-1">
                        {isSuccess ? 'All processed' : 'Crashed'}
                    </div>
                </div>

                {/* Context Size */}
                <div className="bg-dashboard-bg/50 rounded-lg p-3 border border-dashboard-border/30">
                    <div className="text-[10px] text-text-muted uppercase tracking-widest mb-1">Context</div>
                    <div className="text-2xl font-bold text-cyan-400">
                        {context_size_gb.toFixed(2)}GB
                    </div>
                    <div className="text-[9px] text-text-secondary mt-1">
                        Total managed
                    </div>
                </div>

                {/* Memory Saved */}
                {aidaptivEnabled && memory_saved_gb > 0 && (
                    <div className="bg-dashboard-bg/50 rounded-lg p-3 border border-dashboard-border/30">
                        <div className="text-[10px] text-text-muted uppercase tracking-widest mb-1">Offloaded</div>
                        <div className="text-2xl font-bold text-amber-400">
                            {memory_saved_gb.toFixed(2)}GB
                        </div>
                        <div className="text-[9px] text-text-secondary mt-1">
                            To SSD
                        </div>
                    </div>
                )}

                {/* Cost Comparison */}
                <div className="bg-dashboard-bg/50 rounded-lg p-3 border border-dashboard-border/30">
                    <div className="text-[10px] text-text-muted uppercase tracking-widest mb-1">Monthly Cost</div>
                    <div className="text-2xl font-bold text-emerald-400">
                        ${estimated_monthly_cost.toLocaleString()}
                    </div>
                    <div className="text-[9px] text-text-secondary mt-1">
                        Infrastructure
                    </div>
                </div>

                {/* Time */}
                <div className="bg-dashboard-bg/50 rounded-lg p-3 border border-dashboard-border/30">
                    <div className="text-[10px] text-text-muted uppercase tracking-widest mb-1">Time</div>
                    <div className="text-2xl font-bold text-blue-400">
                        {time_minutes.toFixed(1)}m
                    </div>
                    <div className="text-[9px] text-text-secondary mt-1">
                        {aidaptivEnabled && tier === 'large' ? `vs ${time_without_aidaptiv.toFixed(0)}m` : 'Completed'}
                    </div>
                </div>
            </div>

            {/* Value Proposition */}
            {aidaptivEnabled && tier === 'large' && isSuccess && (
                <div className="mt-4 p-3 bg-emerald-500/10 border border-emerald-500/30 rounded-lg">
                    <div className="text-xs text-emerald-300 font-semibold">
                        ⚡ aiDAPTIV+ enabled processing {total_documents} documents with {memory_saved_gb.toFixed(0)}GB offloaded to SSD,
                        saving ${(estimated_cost_cloud - estimated_cost_local).toFixed(0)} vs cloud GPU
                    </div>
                </div>
            )}

            {/* Failure Message - only show if we actually have a result */}
            {impactSummary && !isSuccess && (
                <div className="mt-4 p-3 bg-red-500/10 border border-red-500/30 rounded-lg">
                    <div className="text-xs text-red-300 font-semibold">
                        ❌ Analysis failed at document {documents_processed}/{total_documents}.
                        Enable aiDAPTIV+ to process large datasets without OOM crashes.
                    </div>
                </div>
            )}
        </div>
    );
};
