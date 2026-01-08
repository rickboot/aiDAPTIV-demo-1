interface AboutModalProps {
    isOpen: boolean;
    onClose: () => void;
}

export const AboutModal = ({ isOpen, onClose }: AboutModalProps) => {
    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center animate-fade-in overflow-y-auto p-4" onClick={onClose}>
            <div className="bg-[#1e293b] border border-dashboard-border rounded-2xl shadow-2xl w-full max-w-4xl my-8" onClick={(e) => e.stopPropagation()}>

                {/* Header */}
                <div className="flex justify-between items-center p-6 pb-4 border-b border-dashboard-border/50">
                    <h2 className="text-2xl font-bold text-white">About This Demo</h2>
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

                    {/* Overview */}
                    <div>
                        <h3 className="text-lg font-bold text-white mb-2 flex items-center gap-2">
                            <span className="text-blue-400">🎯</span> System Overview
                        </h3>
                        <p className="text-sm leading-relaxed">
                            This demo simulates a <strong>Product Marketing Manager</strong> using an <strong>agentic AI system</strong> to analyze competitive intelligence.
                            It demonstrates how aiDAPTIV+ enables large-scale AI workloads by intelligently managing memory through SSD offloading.
                        </p>
                    </div>

                    {/* AI Architecture */}
                    <div className="bg-blue-500/10 border border-blue-500/30 rounded-xl p-4">
                        <h3 className="text-lg font-bold text-white mb-3 flex items-center gap-2">
                            <span className="text-blue-400">🤖</span> AI Architecture: Agentic Reasoning
                        </h3>
                        <div className="space-y-3 text-sm">
                            <div>
                                <div className="font-semibold text-blue-200 mb-1">LLM Engine</div>
                                <div className="text-blue-300/80">
                                    • <strong>Model:</strong> Ollama (llama3.1:8b) running locally<br />
                                    • <strong>Context Window:</strong> ~8,000 tokens<br />
                                    • <strong>Mode:</strong> Real-time streaming inference
                                </div>
                            </div>
                            <div>
                                <div className="font-semibold text-blue-200 mb-1">5-Phase Agentic Analysis</div>
                                <div className="text-blue-300/80 space-y-1">
                                    <div><strong>Phase 1:</strong> Document Review - Catalogs available data sources</div>
                                    <div><strong>Phase 2:</strong> Pattern Detection - Identifies UI/architecture changes</div>
                                    <div><strong>Phase 3:</strong> Technical Cross-Reference - Links patterns to research papers</div>
                                    <div><strong>Phase 4:</strong> Social Signal Validation - Corroborates with industry signals</div>
                                    <div><strong>Phase 5:</strong> Synthesis - Generates strategic recommendations</div>
                                </div>
                            </div>
                            <div>
                                <div className="font-semibold text-blue-200 mb-1">Reasoning Chain</div>
                                <div className="text-blue-300/80">
                                    The LLM generates unique analysis each run by reasoning through evidence step-by-step,
                                    citing specific competitors, papers, and signals. This is <em>not</em> pre-scripted—it's authentic AI reasoning.
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Data Flow */}
                    <div>
                        <h3 className="text-lg font-bold text-white mb-3 flex items-center gap-2">
                            <span className="text-emerald-400">📊</span> Data Ingestion & Flow
                        </h3>
                        <div className="space-y-3 text-sm">
                            <div className="bg-dashboard-card border border-dashboard-border rounded-lg p-3">
                                <div className="font-semibold text-emerald-200 mb-2">Input Data (Lite: 18 docs | Large: 268 docs)</div>
                                <div className="grid grid-cols-3 gap-3 text-xs">
                                    <div>
                                        <div className="text-emerald-400 font-bold mb-1">Competitors</div>
                                        <div className="text-text-muted">Product descriptions, UI screenshots, architecture notes</div>
                                    </div>
                                    <div>
                                        <div className="text-emerald-400 font-bold mb-1">Research Papers</div>
                                        <div className="text-text-muted">arXiv papers on agentic AI, RAG, multi-agent systems</div>
                                    </div>
                                    <div>
                                        <div className="text-emerald-400 font-bold mb-1">Social Signals</div>
                                        <div className="text-text-muted">CTO blog posts, conference talks, product announcements</div>
                                    </div>
                                </div>
                            </div>
                            <div className="text-sm">
                                <strong>Processing Flow:</strong>
                                <ol className="list-decimal list-inside space-y-1 mt-2 text-text-secondary">
                                    <li>Documents loaded from <code className="text-xs bg-black/30 px-1 rounded">/documents/pmm/[tier]/</code></li>
                                    <li>Content combined into unified context string (~22K chars for lite, ~180K for large)</li>
                                    <li>Context sent to LLM with phase-specific prompts</li>
                                    <li>LLM streams reasoning back in real-time</li>
                                    <li>Thoughts displayed in UI feed as they're generated</li>
                                </ol>
                            </div>
                        </div>
                    </div>

                    {/* Memory Consumption */}
                    <div className="bg-purple-500/10 border border-purple-500/30 rounded-xl p-4">
                        <h3 className="text-lg font-bold text-white mb-3 flex items-center gap-2">
                            <span className="text-purple-400">💾</span> Memory Consumption & Management
                        </h3>
                        <div className="space-y-3 text-sm">
                            <div>
                                <div className="font-semibold text-purple-200 mb-1">Memory Breakdown</div>
                                <div className="text-purple-300/80">
                                    • <strong>Model Weights:</strong> ~4.7GB (llama3.1:8b quantized)<br />
                                    • <strong>KV Cache:</strong> Grows with context size (~0.5GB per 10K tokens)<br />
                                    • <strong>Working Memory:</strong> Document buffers, embeddings, activations<br />
                                    • <strong>Total (Lite):</strong> ~10GB | <strong>Total (Large):</strong> ~19GB
                                </div>
                            </div>
                            <div>
                                <div className="font-semibold text-purple-200 mb-1">Without aiDAPTIV+ (16GB Limit)</div>
                                <div className="text-purple-300/80">
                                    As memory fills beyond 85%, the system experiences:<br />
                                    • <strong>Memory thrashing</strong> - OS swaps to disk uncontrollably<br />
                                    • <strong>Performance degradation</strong> - TTFT increases from 200ms &rarr; 1200ms<br />
                                    • <strong>Token slowdown</strong> - Speed drops from 45 tok/s &rarr; 15 tok/s<br />
                                    • <strong>OOM crash</strong> - System terminates at &sim;95% memory (large tier)
                                </div>
                            </div>
                            <div>
                                <div className="font-semibold text-purple-200 mb-1">With aiDAPTIV+ Enabled</div>
                                <div className="text-purple-300/80">
                                    • <strong>Intelligent offload</strong> - Cold data moved to SSD cache at 70% threshold<br />
                                    • <strong>Unified memory stays free</strong> - Keeps GPU/CPU memory available for active computation<br />
                                    • <strong>Performance maintained</strong> - TTFT stays ~250ms, speed ~40 tok/s<br />
                                    • <strong>No crashes</strong> - Large tier completes successfully
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Outputs */}
                    <div>
                        <h3 className="text-lg font-bold text-white mb-3 flex items-center gap-2">
                            <span className="text-amber-400">📤</span> System Outputs
                        </h3>
                        <div className="space-y-2 text-sm">
                            <div className="flex items-start gap-2">
                                <span className="text-amber-400 font-bold">•</span>
                                <div><strong>Reasoning Chain:</strong> Real-time LLM thoughts showing analysis progression</div>
                            </div>
                            <div className="flex items-start gap-2">
                                <span className="text-amber-400 font-bold">•</span>
                                <div><strong>Metrics:</strong> Competitors tracked, visual updates, papers analyzed, signals detected</div>
                            </div>
                            <div className="flex items-start gap-2">
                                <span className="text-amber-400 font-bold">•</span>
                                <div><strong>Performance Telemetry:</strong> TTFT, tokens/sec, latency, degradation status</div>
                            </div>
                            <div className="flex items-start gap-2">
                                <span className="text-amber-400 font-bold">•</span>
                                <div><strong>Memory Stats:</strong> Unified memory, virtual memory (SSD cache), system RAM</div>
                            </div>
                            <div className="flex items-start gap-2">
                                <span className="text-amber-400 font-bold">•</span>
                                <div><strong>Final Report:</strong> Strategic findings with evidence and recommendations</div>
                            </div>
                        </div>
                    </div>

                    {/* Error Scenarios */}
                    <div className="bg-red-500/10 border border-red-500/30 rounded-xl p-4">
                        <h3 className="text-lg font-bold text-white mb-3 flex items-center gap-2">
                            <span className="text-red-400">⚠️</span> Error Scenarios
                        </h3>
                        <div className="space-y-3 text-sm">
                            <div>
                                <div className="font-semibold text-red-200 mb-1">Out of Memory (OOM) Crash</div>
                                <div className="text-red-300/80">
                                    <strong>Trigger:</strong> Large tier without aiDAPTIV+ enabled<br />
                                    <strong>Cause:</strong> 19GB workload exceeds 16GB unified memory limit<br />
                                    <strong>Behavior:</strong> Crashes at 76% progress with "CUDA Kernel Terminated" error<br />
                                    <strong>Solution:</strong> Enable aiDAPTIV+ to offload to SSD cache
                                </div>
                            </div>
                            <div>
                                <div className="font-semibold text-red-200 mb-1">Ollama Connection Failure</div>
                                <div className="text-red-300/80">
                                    <strong>Trigger:</strong> Ollama server not running or model not pulled<br />
                                    <strong>Behavior:</strong> Falls back to pre-scripted canned responses<br />
                                    <strong>Solution:</strong> Start Ollama with <code className="text-xs bg-black/30 px-1 rounded">ollama serve</code> and pull model
                                </div>
                            </div>
                            <div>
                                <div className="font-semibold text-red-200 mb-1">Performance Degradation</div>
                                <div className="text-red-300/80">
                                    <strong>Trigger:</strong> Memory pressure &gt; 85% without aiDAPTIV+<br />
                                    <strong>Behavior:</strong> Status changes to "degraded" or "critical", TTFT/latency increase<br />
                                    <strong>Impact:</strong> Slower analysis, poor user experience<br />
                                    <strong>Solution:</strong> Enable aiDAPTIV+ to maintain optimal performance
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Tech Stack */}
                    <div className="text-xs text-text-muted border-t border-dashboard-border/30 pt-4">
                        <strong>Tech Stack:</strong> React + TypeScript (Frontend) | FastAPI + Python (Backend) | Ollama + llama3.1:8b (LLM) | WebSocket (Real-time streaming)
                    </div>

                </div>

                {/* Footer */}
                <div className="p-6 pt-4 border-t border-dashboard-border/50 flex justify-end">
                    <button
                        onClick={onClose}
                        className="px-6 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-bold transition-colors shadow-lg shadow-blue-500/20"
                    >
                        Got It
                    </button>
                </div>

            </div>
        </div>
    );
};
