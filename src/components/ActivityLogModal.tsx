import React from 'react';
import { useScenario } from '../ScenarioContext';

interface ActivityLogEntry {
    timestamp: string;
    activity: string;
    type: 'status' | 'document' | 'rag_storage' | 'rag_retrieval' | 'thought' | 'metric' | 'error';
}

interface ActivityLogModalProps {
    isOpen: boolean;
    onClose: () => void;
    activityLog: ActivityLogEntry[];
}

export const ActivityLogModal: React.FC<ActivityLogModalProps> = ({ isOpen, onClose, activityLog }) => {
    const logEndRef = React.useRef<HTMLDivElement>(null);

    // Auto-scroll to bottom when new entries are added
    React.useEffect(() => {
        if (logEndRef.current) {
            logEndRef.current.scrollIntoView({ behavior: 'smooth' });
        }
    }, [activityLog]);

    if (!isOpen) return null;

    const getActivityIcon = (type: string) => {
        switch (type) {
            case 'status': return '📊';
            case 'document': return '📄';
            case 'rag_storage': return '📦';
            case 'rag_retrieval': return '🔍';
            case 'thought': return '💭';
            case 'metric': return '📈';
            case 'error': return '❌';
            default: return 'ℹ️';
        }
    };

    const getActivityColor = (type: string) => {
        switch (type) {
            case 'status': return 'text-blue-400';
            case 'document': return 'text-cyan-400';
            case 'rag_storage': return 'text-emerald-400';
            case 'rag_retrieval': return 'text-purple-400';
            case 'thought': return 'text-yellow-400';
            case 'metric': return 'text-green-400';
            case 'error': return 'text-red-400';
            default: return 'text-gray-400';
        }
    };

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm" onClick={onClose}>
            <div 
                className="bg-dashboard-card border border-dashboard-border/50 rounded-xl shadow-2xl w-[90vw] max-w-4xl h-[80vh] flex flex-col"
                onClick={(e) => e.stopPropagation()}
            >
                {/* Header */}
                <div className="flex items-center justify-between p-6 border-b border-dashboard-border/50">
                    <div>
                        <h2 className="text-xl font-bold text-text-primary">Activity Log</h2>
                        <p className="text-sm text-text-secondary mt-1">{activityLog.length} entries</p>
                    </div>
                    <button
                        onClick={onClose}
                        className="text-text-muted hover:text-text-primary transition-colors p-2 hover:bg-dashboard-bg rounded-lg"
                    >
                        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                        </svg>
                    </button>
                </div>

                {/* Log Entries */}
                <div className="flex-1 overflow-y-auto p-6 space-y-3">
                    {activityLog.length === 0 ? (
                        <div className="text-center text-text-muted py-12">
                            <p>No activity logged yet</p>
                        </div>
                    ) : (
                        activityLog.map((entry, index) => {
                            const date = new Date(entry.timestamp);
                            const timeStr = date.toLocaleTimeString('en-US', { 
                                hour12: false, 
                                hour: '2-digit', 
                                minute: '2-digit', 
                                second: '2-digit',
                                fractionalSecondDigits: 3
                            });

                            return (
                                <div
                                    key={index}
                                    className="flex items-start gap-3 p-3 rounded-lg bg-dashboard-bg/50 border border-dashboard-border/30 hover:bg-dashboard-bg transition-colors"
                                >
                                    <div className={`text-lg shrink-0 ${getActivityColor(entry.type)}`}>
                                        {getActivityIcon(entry.type)}
                                    </div>
                                    <div className="flex-1 min-w-0">
                                        <div className="flex items-center gap-2 mb-1">
                                            <span className="text-xs font-mono text-text-muted">{timeStr}</span>
                                            <span className={`text-xs font-bold uppercase px-2 py-0.5 rounded ${getActivityColor(entry.type)} bg-opacity-10`}>
                                                {entry.type}
                                            </span>
                                        </div>
                                        <div className="text-sm text-text-primary break-words">
                                            {entry.activity}
                                        </div>
                                    </div>
                                </div>
                            );
                        })
                    )}
                    <div ref={logEndRef} />
                </div>

                {/* Footer */}
                <div className="p-4 border-t border-dashboard-border/50 flex items-center justify-between text-xs text-text-muted">
                    <div className="flex items-center gap-4">
                        <span>📊 Status</span>
                        <span>📄 Document</span>
                        <span>📦 RAG Storage</span>
                        <span>🔍 RAG Retrieval</span>
                        <span>💭 Thought</span>
                        <span>📈 Metric</span>
                    </div>
                    <button
                        onClick={() => {
                            if (logEndRef.current) {
                                logEndRef.current.scrollIntoView({ behavior: 'smooth' });
                            }
                        }}
                        className="text-blue-400 hover:text-blue-300 transition-colors"
                    >
                        Scroll to bottom
                    </button>
                </div>
            </div>
        </div>
    );
};
