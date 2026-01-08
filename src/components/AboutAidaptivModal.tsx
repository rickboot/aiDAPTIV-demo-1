interface AboutAidaptivModalProps {
    isOpen: boolean;
    onClose: () => void;
}

export const AboutAidaptivModal = ({ isOpen, onClose }: AboutAidaptivModalProps) => {
    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center animate-fade-in overflow-y-auto p-4" onClick={onClose}>
            <div className="bg-[#1e293b] border border-emerald-500/30 rounded-2xl shadow-2xl shadow-emerald-500/10 w-full max-w-4xl my-8" onClick={(e) => e.stopPropagation()}>

                {/* Header */}
                <div className="flex justify-between items-center p-6 pb-4 border-b border-emerald-500/20 bg-gradient-to-r from-emerald-500/5 to-transparent">
                    <div>
                        <h2 className="text-2xl font-bold text-white flex items-center gap-3">
                            <span className="text-3xl">⚡</span>
                            About aiDAPTIV+
                        </h2>
                        <p className="text-sm text-emerald-300/80 mt-1">Intelligent SSD Memory Management for AI Workloads</p>
                    </div>
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
                <div className="p-6 space-y-6 text-text-primary max-h-[70vh] overflow-y-auto">

                    {/* What is aiDAPTIV+ */}
                    <div>
                        <h3 className="text-lg font-bold text-white mb-3 flex items-center gap-2">
                            <span className="text-emerald-400">🎯</span> What is aiDAPTIV+?
                        </h3>
                        <p className="text-sm leading-relaxed mb-3">
                            <strong>aiDAPTIV+</strong> is Phison's intelligent memory management technology that enables AI workloads to exceed physical RAM limits
                            by intelligently offloading data to high-speed NVMe SSD storage.
                        </p>
                        <p className="text-sm leading-relaxed text-text-secondary">
                            Think of it as "smart virtual memory" specifically optimized for AI/ML workloads. Unlike traditional OS-level swapping,
                            aiDAPTIV+ understands AI memory access patterns and makes intelligent decisions about what to keep in RAM vs. what to offload to SSD.
                        </p>
                    </div>

                    {/* The Problem */}
                    <div className="bg-red-500/10 border border-red-500/30 rounded-xl p-4">
                        <h3 className="text-lg font-bold text-white mb-3 flex items-center gap-2">
                            <span className="text-red-400">⚠️</span> The Problem: Memory Bottleneck
                        </h3>
                        <div className="space-y-3 text-sm">
                            <div>
                                <div className="font-semibold text-red-200 mb-1">AI Models Are Memory-Hungry</div>
                                <div className="text-red-300/80">
                                    Modern LLMs require massive amounts of memory:<br />
                                    • <strong>Model weights:</strong> 4-70GB depending on model size<br />
                                    • <strong>KV cache:</strong> Grows with context length (0.5GB per 10K tokens)<br />
                                    • <strong>Activations:</strong> Intermediate computation results<br />
                                    • <strong>Embeddings:</strong> Document vectors for RAG systems
                                </div>
                            </div>
                            <div>
                                <div className="font-semibold text-red-200 mb-1">Consumer Hardware Limits</div>
                                <div className="text-red-300/80">
                                    • MacBook Air M4: <strong>16GB unified memory</strong> (shared between CPU/GPU)<br />
                                    • Larger contexts = Better AI, but quickly exceed available RAM<br />
                                    • Traditional solution: Expensive RAM upgrades or cloud GPUs ($$$)
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* How aiDAPTIV+ Works */}
                    <div className="bg-emerald-500/10 border border-emerald-500/30 rounded-xl p-4">
                        <h3 className="text-lg font-bold text-white mb-3 flex items-center gap-2">
                            <span className="text-emerald-400">⚙️</span> How aiDAPTIV+ Works
                        </h3>
                        <div className="space-y-4 text-sm">
                            <div>
                                <div className="font-semibold text-emerald-200 mb-2">1. Intelligent Monitoring</div>
                                <div className="text-emerald-300/80">
                                    Continuously monitors unified memory pressure on Apple Silicon. When memory usage crosses a threshold (e.g., 70%),
                                    aiDAPTIV+ activates and begins analyzing memory access patterns.
                                </div>
                            </div>
                            <div>
                                <div className="font-semibold text-emerald-200 mb-2">2. Smart Offloading</div>
                                <div className="text-emerald-300/80">
                                    Identifies "cold" data that hasn't been accessed recently:<br />
                                    • Older KV cache entries<br />
                                    • Inactive document embeddings<br />
                                    • Intermediate activations from previous layers<br />
                                    <br />
                                    This data is compressed and moved to a dedicated SSD cache area.
                                </div>
                            </div>
                            <div>
                                <div className="font-semibold text-emerald-200 mb-2">3. Fast Retrieval</div>
                                <div className="text-emerald-300/80">
                                    When offloaded data is needed again, aiDAPTIV+ fetches it from SSD at NVMe speeds (7GB/s+).
                                    This is <strong>much faster</strong> than traditional OS swapping because:
                                    <br />• Direct NVMe access (bypasses OS overhead)
                                    <br />• Predictive prefetching based on AI access patterns
                                    <br />• Optimized compression for AI data types
                                </div>
                            </div>
                            <div>
                                <div className="font-semibold text-emerald-200 mb-2">4. Transparent Operation</div>
                                <div className="text-emerald-300/80">
                                    The AI application doesn't need to be modified. aiDAPTIV+ works at the system level,
                                    presenting a "virtual memory pool" that appears larger than physical RAM.
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Benefits */}
                    <div>
                        <h3 className="text-lg font-bold text-white mb-3 flex items-center gap-2">
                            <span className="text-blue-400">✨</span> Key Benefits
                        </h3>
                        <div className="grid grid-cols-2 gap-3 text-sm">
                            <div className="bg-dashboard-card border border-dashboard-border rounded-lg p-3">
                                <div className="font-semibold text-blue-200 mb-1 flex items-center gap-2">
                                    <span>💰</span> Cost Savings
                                </div>
                                <div className="text-text-secondary text-xs">
                                    Run larger AI models on consumer hardware. No need for expensive RAM upgrades or cloud GPU rentals.
                                </div>
                            </div>
                            <div className="bg-dashboard-card border border-dashboard-border rounded-lg p-3">
                                <div className="font-semibold text-blue-200 mb-1 flex items-center gap-2">
                                    <span>🚀</span> Better Performance
                                </div>
                                <div className="text-text-secondary text-xs">
                                    Maintains optimal speed even under memory pressure. TTFT stays low, token generation stays fast.
                                </div>
                            </div>
                            <div className="bg-dashboard-card border border-dashboard-border rounded-lg p-3">
                                <div className="font-semibold text-blue-200 mb-1 flex items-center gap-2">
                                    <span>📈</span> Larger Contexts
                                </div>
                                <div className="text-text-secondary text-xs">
                                    Process 15x more documents in this demo (18 → 268). Analyze entire codebases, long documents, massive datasets.
                                </div>
                            </div>
                            <div className="bg-dashboard-card border border-dashboard-border rounded-lg p-3">
                                <div className="font-semibold text-blue-200 mb-1 flex items-center gap-2">
                                    <span>🛡️</span> Crash Prevention
                                </div>
                                <div className="text-text-secondary text-xs">
                                    No more OOM errors. Workloads that would crash without aiDAPTIV+ complete successfully.
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* How It's Used in This Demo */}
                    <div className="bg-purple-500/10 border border-purple-500/30 rounded-xl p-4">
                        <h3 className="text-lg font-bold text-white mb-3 flex items-center gap-2">
                            <span className="text-purple-400">🎬</span> How It's Used in This Demo
                        </h3>
                        <div className="space-y-3 text-sm">
                            <div>
                                <div className="font-semibold text-purple-200 mb-1">Simulated Behavior (Current)</div>
                                <div className="text-purple-300/80">
                                    <strong>Note:</strong> aiDAPTIV+ is not yet implemented in this demo—it's <strong>simulated</strong> to demonstrate the concept.<br /><br />

                                    The demo shows:<br />
                                    • <strong>Lite tier (18 docs, 10GB):</strong> Fits in 16GB RAM → Always succeeds<br />
                                    • <strong>Large tier without aiDAPTIV+ (268 docs, 19GB):</strong> Exceeds 16GB → Crashes at 76%<br />
                                    • <strong>Large tier with aiDAPTIV+ (268 docs, 19GB):</strong> Offloads to SSD → Completes successfully
                                </div>
                            </div>
                            <div>
                                <div className="font-semibold text-purple-200 mb-1">Future Implementation</div>
                                <div className="text-purple-300/80">
                                    When aiDAPTIV+ is integrated:<br />
                                    • Real-time monitoring of actual unified memory usage<br />
                                    • Automatic offloading of LLM KV cache and embeddings to Phison SSD<br />
                                    • Performance metrics will reflect real TTFT/latency improvements<br />
                                    • Large-tier analysis will genuinely run on 16GB hardware
                                </div>
                            </div>
                            <div className="bg-amber-500/10 border border-amber-500/30 rounded-lg p-3">
                                <div className="flex items-start gap-2 text-amber-200">
                                    <svg className="w-5 h-5 shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                                    </svg>
                                    <div className="text-xs">
                                        <strong>Try it yourself:</strong> Toggle aiDAPTIV+ in Settings, then run the large tier.
                                        Watch the System Telemetry panel to see SSD cache activate and performance metrics stay optimal!
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Tech Specs */}
                    <div className="text-xs text-text-muted border-t border-dashboard-border/30 pt-4">
                        <strong>Technology:</strong> Phison aiDAPTIV+ | <strong>Target Platform:</strong> Apple Silicon (M1/M2/M3/M4) |
                        <strong> SSD:</strong> Phison E31T NVMe Controller | <strong>Speed:</strong> 7GB/s sequential read
                    </div>

                </div>

                {/* Footer */}
                <div className="p-6 pt-4 border-t border-dashboard-border/50 flex justify-end">
                    <button
                        onClick={onClose}
                        className="px-6 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-bold transition-colors shadow-lg shadow-emerald-500/20"
                    >
                        Got It
                    </button>
                </div>

            </div>
        </div>
    );
};
