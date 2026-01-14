import { createContext, useContext, useState, useEffect, useRef, type ReactNode } from 'react';
import type { FeedItem, SystemState, PerformanceMetrics, Scenario, WorldModelItem, CrashData, CrashEvent, ImpactSummaryData, RAGStorageEvent, RAGRetrievalEvent } from './types';
import { SCENARIOS, INITIAL_METRICS } from './mockData';

interface Metrics {
    key_topics: number;
    patterns_detected: number;
    insights_generated: number;
    critical_flags: number;
}

interface ActivityLogEntry {
    timestamp: string;
    activity: string;
    type: 'status' | 'document' | 'rag_storage' | 'rag_retrieval' | 'thought' | 'metric' | 'error';
}

interface ScenarioContextType {
    feed: FeedItem[];
    worldModel: WorldModelItem[];
    systemState: SystemState;
    metrics: Metrics;
    performance: PerformanceMetrics;
    currentActivity: string;
    activityLog: ActivityLogEntry[];
    toggleAidaptiv: () => void;
    activeScenario: Scenario;
    setActiveScenario: (id: string) => void;
    isAnalysisRunning: boolean;
    analysisState: 'running' | 'completed' | 'idle' | 'crashed';
    crashDetails: CrashData | null;
    startAnalysis: () => Promise<void>;
    stopAnalysis: () => void;
    showHardwareMonitor: boolean;
    toggleMonitor: () => void;
    isComplete: boolean;
    resetAnalysis: () => void;
    tier: 'lite' | 'large';
    setTier: (tier: 'lite' | 'large') => void;
    currentTier: string;
    enabledFeatures: string[];
    upgradeMessage: string;
    elapsedSeconds: number;
    impactSummary: ImpactSummaryData | null;
    totalDocuments: number; // Dynamic total from backend
    backendConnected: boolean;
    backendError: string | null;
    ollamaConnected: boolean;
    ollamaError: string | null;
}

const ScenarioContext = createContext<ScenarioContextType | undefined>(undefined);

const WS_URL = 'ws://localhost:8000/ws/analysis';

export const ScenarioProvider = ({ children }: { children: ReactNode }) => {
    // STATE
    const [activeScenario, setActiveScenarioState] = useState<Scenario>(SCENARIOS[0]); // Marketing Intelligence scenario
    const [feed, setFeed] = useState<FeedItem[]>(activeScenario.initialFeed);
    const [worldModel, setWorldModel] = useState<WorldModelItem[]>([]); // Start empty, populate dynamically
    const [metrics, setMetrics] = useState<Metrics>(INITIAL_METRICS);

    const [isAnalysisRunning, setIsAnalysisRunning] = useState(false);
    const [isComplete, setIsComplete] = useState(false);
    const [isCrashed, setIsCrashed] = useState(false);

    const [showHardwareMonitor, setShowHardwareMonitor] = useState(true); // Enabled by default for dev
    const [tier, setTierState] = useState<'lite' | 'large'>('lite'); // Default to lite for faster demos

    // Multi-modal tier state
    const [currentTier, setCurrentTier] = useState<string>('text_only');
    const [enabledFeatures, setEnabledFeatures] = useState<string[]>(['text_analysis']);
    const [upgradeMessage, setUpgradeMessage] = useState<string>('');

    // Elapsed time tracking
    const [elapsedSeconds, setElapsedSeconds] = useState(0);
    const [analysisStartTime, setAnalysisStartTime] = useState<number | null>(null);

    const INITIAL_PERFORMANCE: PerformanceMetrics = {
        ttft_ms: 0,
        tokens_per_second: 0,
        latency_ms: 0,
        status: 'optimal',
        degradation_percent: 0
    };
    const [performance, setPerformance] = useState<PerformanceMetrics>(INITIAL_PERFORMANCE);

    const [crashDetails, setCrashDetails] = useState<CrashData | null>(null);

    const [currentActivity, setCurrentActivity] = useState<string>('Idle');
    const [activityLog, setActivityLog] = useState<ActivityLogEntry[]>([]);
    const [impactSummary, setImpactSummary] = useState<ImpactSummaryData | null>(null);
    const [totalDocuments, setTotalDocuments] = useState<number>(0); // Dynamic total from backend init event
    const [backendConnected, setBackendConnected] = useState(true);
    const [backendError, setBackendError] = useState<string | null>(null);
    const [ollamaConnected, setOllamaConnected] = useState(true);
    const [ollamaError, setOllamaError] = useState<string | null>(null);

    // Define INITIAL_SYSTEM_STATE
    const INITIAL_SYSTEM_STATE: SystemState = {
        vramUsage: 0,
        totalMemory: 16,
        ramUsage: 0, // Changed from 16.0 to 0 as per instruction's implied change
        ssdUsage: 0,
        isAidaptivEnabled: true,  // ENABLED BY DEFAULT FOR DEVELOPMENT
        context_tokens: 0,
        kv_cache_gb: 0,
        model_weights_gb: 0,
        loaded_model: 'llama3.1:8b',  // Track which model is loaded
        modelName: 'Llama-3-70B' // Keep existing modelName
    };
    const [systemState, setSystemState] = useState<SystemState>(INITIAL_SYSTEM_STATE);

    // WebSocket ref
    const wsRef = useRef<WebSocket | null>(null);
    // Track if analysis has started (more reliable than checking state in closure)
    const analysisStartedRef = useRef<boolean>(false);
    // Track if first document has been processed (to ignore stale Ollama values from previous runs)
    const firstDocumentProcessedRef = useRef<boolean>(false);

    // ACTIONS
    const setActiveScenario = (id: string) => {
        const found = SCENARIOS.find(s => s.id === id);
        if (found) {
            setActiveScenarioState(found);

            // Derive tier
            const newTier = found.id.includes('large') ? 'large' : 'lite';
            setTierState(newTier);

            // Auto-enable aiDAPTIV+ for Large scenarios so demo succeeds by default
            if (newTier === 'large') {
                setSystemState(prev => ({ ...prev, isAidaptivEnabled: true }));
            }

            resetAnalysis();
            setFeed(found.initialFeed);
        }
    };

    const resetAnalysis = () => {
        // Close existing WebSocket if any
        if (wsRef.current) {
            wsRef.current.close();
            wsRef.current = null;
        }

        setIsAnalysisRunning(false);
        setCrashDetails(null);
        analysisStartedRef.current = false; // Reset analysis started flag
        firstDocumentProcessedRef.current = false; // Reset first document processed flag
        // Reset all memory-related values including context and KV cache
        setSystemState(prev => ({ 
            ...prev, 
            vramUsage: 0, 
            ramUsage: 16.0, 
            ssdUsage: 0,
            context_tokens: 0,
            kv_cache_gb: 0,
            model_weights_gb: 0
        }));
        setWorldModel([]); // Clear to repopulate dynamically
        setTotalDocuments(0); // Reset total documents count
        setFeed(activeScenario.initialFeed);
        setMetrics(INITIAL_METRICS);
        setPerformance(INITIAL_PERFORMANCE);
        setCurrentActivity('Idle');
        setActivityLog([]);
    };


    const toggleMonitor = () => setShowHardwareMonitor(prev => !prev);

    const setTier = (newTier: 'lite' | 'large') => {
        if (!isAnalysisRunning) {
            setTierState(newTier);
        }
    };

    const toggleAidaptiv = () => {
        if (!isAnalysisRunning) {
            setSystemState(prev => ({
                ...prev,
                isAidaptivEnabled: !prev.isAidaptivEnabled
            }));
        }
    };

    // Load system info on mount
    useEffect(() => {
        const fetchSystemInfo = async () => {
            try {
                const response = await fetch('http://localhost:8000/api/system/info');
                if (response.ok) {
                    const data = await response.json();
                    setSystemState(prev => ({
                        ...prev,
                        totalMemory: data.memory_gb,
                        modelName: data.model
                    }));
                }
            } catch (error) {
                console.error('Failed to fetch system info:', error);
                setBackendConnected(false);
                setBackendError('Backend not responding. Make sure the backend server is running on port 8000.');
            }
        };
        fetchSystemInfo();
    }, []);

    // Load current memory usage on mount (baseline before analysis)
    useEffect(() => {
        const fetchCurrentMemory = async () => {
            try {
                const response = await fetch('http://localhost:8000/api/memory/current');
                if (response.ok) {
                    const data = await response.json();
                    setSystemState(prev => ({
                        ...prev,
                        vramUsage: data.unified_gb,
                        ramUsage: data.unified_gb,
                        ssdUsage: data.virtual_gb
                    }));
                }
            } catch (error) {
                console.error('Failed to fetch current memory:', error);
                setBackendConnected(false);
                setBackendError('Backend not responding. Make sure the backend server is running on port 8000.');
            }
        };
        fetchCurrentMemory();
    }, []);

    // Check Ollama status on mount and when backend connects
    useEffect(() => {
        // Only check Ollama if backend is connected
        if (!backendConnected) {
            setOllamaConnected(true); // Reset to avoid stale errors
            setOllamaError(null);
            return;
        }

        const checkOllamaStatus = async () => {
            try {
                const response = await fetch('http://localhost:8000/api/ollama/status');
                if (response.ok) {
                    const data = await response.json();
                    if (data.enabled && !data.available) {
                        setOllamaConnected(false);
                        setOllamaError(data.message || 'Ollama is not available');
                    } else {
                        setOllamaConnected(true);
                        setOllamaError(null);
                    }
                } else {
                    // If backend returns error, assume Ollama check failed
                    setOllamaConnected(false);
                    setOllamaError('Unable to check Ollama status');
                }
            } catch (error) {
                console.error('Failed to check Ollama status:', error);
                setOllamaConnected(false);
                setOllamaError('Unable to check Ollama status. Make sure Ollama is running: ollama serve');
            }
        };
        checkOllamaStatus();
    }, [backendConnected]);

    // Fetch capabilities on mount and when aiDAPTIV+ changes
    useEffect(() => {
        const fetchCapabilities = async () => {
            try {
                const response = await fetch(`http://localhost:8000/api/capabilities?aidaptiv_enabled=${systemState.isAidaptivEnabled}`);
                if (response.ok) {
                    const data = await response.json();
                    setCurrentTier(data.tier);
                    setEnabledFeatures(data.enabled_features || []);
                    setUpgradeMessage(data.upgrade_message || '');
                }
            } catch (error) {
                console.error('Failed to fetch capabilities:', error);
            }
        };
        fetchCapabilities();
    }, [systemState.isAidaptivEnabled]);

    // Elapsed time counter
    useEffect(() => {
        if (!analysisStartTime) {
            return;
        }

        // Only update if analysis is running
        if (!isAnalysisRunning) {
            return;
        }

        const interval = setInterval(() => {
            const elapsed = Math.floor((Date.now() - analysisStartTime) / 1000);
            setElapsedSeconds(elapsed);
        }, 1000);

        return () => clearInterval(interval);
    }, [isAnalysisRunning, analysisStartTime]);

    const startAnalysis = async () => {
        if (isAnalysisRunning) return;
        setIsAnalysisRunning(true);
        setIsComplete(false);
        setCrashDetails(null);
        setCurrentActivity('Initializing analysis...');
        setAnalysisStartTime(Date.now());
        setElapsedSeconds(0);
        analysisStartedRef.current = false; // Reset ref - will be set to true when init event arrives
        firstDocumentProcessedRef.current = false; // Reset - will be set to true when first document is processed
        
        // Reset context and KV cache to 0 before starting (clear any stale values from previous Ollama runs)
        setSystemState(prev => ({
            ...prev,
            context_tokens: 0,
            kv_cache_gb: 0
        }));

        if (activeScenario.id.includes('large')) {
            await new Promise(resolve => setTimeout(resolve, 1000)); // Simulate connection delay for large
        }

        // Connect to WebSocket
        const ws = new WebSocket(WS_URL);
        wsRef.current = ws;

        ws.onopen = () => {
            // Send simulation parameters
            // Determine scenario and tier from activeScenario.id
            let scenario = 'pmm';
            let tier = 'lite';

            if (activeScenario.id === 'ces2026') {
                scenario = 'ces2026';
                tier = 'standard';
            } else if (activeScenario.id.includes('large')) {
                tier = 'large';
            }

            const params = {
                scenario,
                tier,
                aidaptiv_enabled: systemState.isAidaptivEnabled
            };

            ws.send(JSON.stringify(params));
        };

        ws.onmessage = (event) => {
            const message = JSON.parse(event.data);
            handleWebSocketMessage(message);
        };

        ws.onerror = (error) => {
            console.error('WebSocket error:', error);
        };

        ws.onclose = () => {
            setIsAnalysisRunning(false);
        };

    };

    const stopAnalysis = () => {
        if (wsRef.current) {
            wsRef.current.close();
            wsRef.current = null;
        }
        setIsAnalysisRunning(false);
        setCurrentActivity('Analysis stopped');
        setAnalysisStartTime(null);
    };

    // Handle WebSocket messages
    const handleWebSocketMessage = (message: any) => {
        switch (message.type) {
            case 'init':
                // Initialize world model with placeholders - detect type from filename
                analysisStartedRef.current = true; // Mark that analysis has started
                if (message.data.documents) {
                    // Store total document count from backend (dynamic, not hardcoded)
                    const totalFromBackend = message.data.total || message.data.documents.length;
                    
                    const initialModel = message.data.documents.map((doc: any, index: number) => {
                        // Detect type from category (preferred) or filename (fallback)
                        let type = 'text_document';
                        if (doc.category === 'image' || doc.name.endsWith('.png') || doc.name.endsWith('.jpg') || doc.name.endsWith('.jpeg')) {
                            type = 'screenshot';
                        } else if (doc.category === 'documentation' && (doc.name.includes('transcript') || doc.name.includes('video'))) {
                            // Video transcripts are documentation, not video
                            type = 'text_document';
                        } else if (doc.category === 'video') {
                            // Only real video files (not transcripts) should be video_transcript
                            type = 'video_transcript';
                        }

                        return {
                            id: `doc-${index}`,
                            type: type,
                            title: doc.name,
                            category: doc.category, // Store category for later use
                            memorySize: doc.size_kb || 50, // Show actual size from backend immediately
                            lastAccessed: Date.now(),
                            status: 'pending'
                        };
                    });
                    setWorldModel(initialModel);
                    // Store total documents count from backend for use throughout the app
                    setTotalDocuments(totalFromBackend);
                }
                break;

            case 'thought':
                // Add thought to feed
                setCurrentActivity('AI Reasoning...');
                // Add to activity log (truncate long thoughts)
                const thoughtPreview = message.data.text.length > 100 
                    ? message.data.text.substring(0, 100) + '...'
                    : message.data.text;
                setActivityLog(prev => [...prev, {
                    timestamp: message.data.timestamp || new Date().toISOString(),
                    activity: `💭 ${message.data.author || '@AI_Analyst'}: ${thoughtPreview}`,
                    type: 'thought'
                }]);
                const newThought: FeedItem = {
                    id: `ws-${Date.now()}`,
                    source: 'AI_Agent',
                    author: message.data.author || '@AI_Agent',
                    content: message.data.text,
                    timestamp: 'Just now',
                    badge: message.data.status,
                    stepType: message.data.step_type,
                    tools: message.data.tools,
                    parentId: message.data.parent_id,
                    relatedDocIds: message.data.related_doc_ids,
                    dataSource: message.data.source  // Document being analyzed
                };
                setFeed(prev => [newThought, ...prev]);
                break;

            case 'memory':
                // Update system state with memory data
                // Only update context and KV cache after first document is processed (to ignore stale Ollama values)
                setSystemState(prev => {
                    const canShowContext = firstDocumentProcessedRef.current; // Only show after first doc processed
                    
                    return {
                        ...prev,
                        vramUsage: message.data.unified_gb,
                        totalMemory: message.data.unified_total_gb || 16,
                        ramUsage: message.data.unified_gb, // Deprecated field, keep in sync or ignore
                        ssdUsage: message.data.virtual_gb,
                        // Only update context/KV cache after first document processed (ignores stale Ollama values from previous runs)
                        // Model weights can always be shown (it's just the model size, not analysis-specific)
                        context_tokens: canShowContext ? (message.data.context_tokens || 0) : 0,
                        kv_cache_gb: canShowContext ? (message.data.kv_cache_gb || 0) : 0,
                        model_weights_gb: message.data.model_weights_gb || prev.model_weights_gb || 0, // Always show model size if available
                        loaded_model: message.data.loaded_model || prev.loaded_model
                    };
                });
                break;

            case 'document':
                // Mark that first document has been processed (ignore stale Ollama values before this)
                // Only enable context/KV cache display after first document AND a small delay to ensure cache clear completed
                if (!firstDocumentProcessedRef.current) {
                    firstDocumentProcessedRef.current = true;
                    // Reset context/KV cache to 0 when first document arrives (cache should be cleared by now)
                    setSystemState(prev => ({
                        ...prev,
                        context_tokens: 0,
                        kv_cache_gb: 0
                    }));
                }
                // Update world model - mark document as processed
                setCurrentActivity(`Processing: ${message.data.name}`);
                // Add to activity log
                setActivityLog(prev => [...prev, {
                    timestamp: new Date().toISOString(),
                    activity: `📄 Processing document: ${message.data.name} (${message.data.category}, ${message.data.size_kb} KB)`,
                    type: 'document'
                }]);
                setWorldModel(prev => {
                    const newModel = [...prev];
                    const index = message.data.index;

                    // Map category to display type
                    const getFileType = (category: string) => {
                        switch (category) {
                            case 'competitor': return 'screenshot';
                            case 'paper': return 'pdf_embedding';
                            case 'image': return 'screenshot'; // Images show as screenshots
                            case 'video': return 'video_transcript'; // Only for real video files (not transcripts)
                            case 'dossier':
                            case 'news':
                            case 'social':
                            case 'documentation': // Video transcripts are now documentation category
                                return 'text_document';
                            default: return 'text_document';
                        }
                    };

                    // Create entry if it doesn't exist (dynamic sizing)
                    if (!newModel[index]) {
                        newModel[index] = {
                            id: `doc-${index}`,
                            type: getFileType(message.data.category),
                            title: message.data.name,
                            memorySize: message.data.size_kb || 50, // Use actual size from backend
                            lastAccessed: Date.now(),
                            status: 'processing'
                        };
                    } else {
                        // Update existing entry - but don't reset status if already completed
                        const currentStatus = newModel[index].status;
                        newModel[index] = {
                            ...newModel[index],
                            title: message.data.name,
                            type: getFileType(message.data.category),
                            memorySize: message.data.size_kb || 50,
                            // Only set to processing if not already completed (vram)
                            status: currentStatus === 'vram' ? 'vram' : 'processing',
                            lastAccessed: Date.now()
                        };
                    }
                    return newModel;
                });
                break;

            case 'document_status':
                setWorldModel(prev => {
                    const newModel = [...prev];
                    const { index, status } = message.data;
                    if (newModel[index]) {
                        newModel[index] = {
                            ...newModel[index],
                            status: status
                        };
                    } else {
                        console.warn(`Doc ${index} not found in worldModel`);
                    }
                    return newModel;
                });
                break;

            case 'impact_summary':
                setImpactSummary(message.data);
                break;

            case 'performance':
                // Update performance metrics
                setPerformance(message.data);
                break;

            case 'status':
                // Update current activity status
                setCurrentActivity(message.message);
                // Add to activity log
                setActivityLog(prev => [...prev, {
                    timestamp: new Date().toISOString(),
                    activity: message.message,
                    type: 'status'
                }]);
                break;

            case 'metric':
                // Update metrics - names match 1:1 with backend
                setMetrics(prev => ({
                    ...prev,
                    [message.data.name]: message.data.value
                }));
                // Add to activity log
                setActivityLog(prev => [...prev, {
                    timestamp: new Date().toISOString(),
                    activity: `📈 Metric updated: ${message.data.name} = ${message.data.value}`,
                    type: 'metric'
                }]);
                break;

            case 'complete':
                // Analysis complete - preserve final elapsed time
                setCurrentActivity('Analysis complete');

                // Calculate final elapsed time before stopping
                if (analysisStartTime) {
                    const finalElapsed = Math.floor((Date.now() - analysisStartTime) / 1000);
                    setElapsedSeconds(finalElapsed);
                }

                setIsComplete(true);
                setIsAnalysisRunning(false);
                if (wsRef.current) {
                    wsRef.current.close();
                    wsRef.current = null;
                }
                break;

            case 'crash':
                const crashEvent = message as CrashEvent;
                setIsCrashed(true);
                setCrashDetails(crashEvent.data);
                setIsAnalysisRunning(false);
                setSystemState(prev => ({
                    ...prev,
                    vramUsage: 24.1, // Force VRAM spike visualization
                }));
                if (wsRef.current) {
                    wsRef.current.close();
                    wsRef.current = null;
                }
                break;

            case 'rag_storage':
                const ragStorageEvent = message as RAGStorageEvent;
                // Add to feed as a development activity
                setFeed(prev => [{
                    id: `rag_storage_${Date.now()}`,
                    source: 'AI_Agent',
                    author: '@RAG',
                    content: `📦 Stored "${ragStorageEvent.data.document_name}" in Vector DB (${ragStorageEvent.data.tokens} tokens, total: ${ragStorageEvent.data.total_documents_in_db} docs)`,
                    timestamp: ragStorageEvent.data.timestamp,
                    badge: 'COMPLETE',
                    stepType: 'tool_use',
                    tools: ['vector_db']
                }, ...prev]);
                // Add to activity log
                setActivityLog(prev => [...prev, {
                    timestamp: ragStorageEvent.data.timestamp,
                    activity: `📦 Stored "${ragStorageEvent.data.document_name}" in Vector DB (${ragStorageEvent.data.tokens} tokens, total: ${ragStorageEvent.data.total_documents_in_db} docs)`,
                    type: 'rag_storage'
                }]);
                break;

            case 'rag_retrieval':
                const ragRetrievalEvent = message as RAGRetrievalEvent;
                // Add to feed as a development activity
                const retrievalContent = ragRetrievalEvent.data.documents_retrieved > 0
                    ? `🔍 Retrieved ${ragRetrievalEvent.data.documents_retrieved} documents (${ragRetrievalEvent.data.tokens_retrieved}/${ragRetrievalEvent.data.tokens_limit} tokens) from ${ragRetrievalEvent.data.candidates_found} candidates. Excluded ${ragRetrievalEvent.data.excluded_count} duplicates.`
                    : `🔍 No documents retrieved (${ragRetrievalEvent.data.candidates_found} candidates found, all excluded)`;
                setFeed(prev => [{
                    id: `rag_retrieval_${Date.now()}`,
                    source: 'AI_Agent',
                    author: '@RAG',
                    content: retrievalContent,
                    timestamp: ragRetrievalEvent.data.timestamp,
                    badge: 'COMPLETE',
                    stepType: 'tool_use',
                    tools: ['vector_db', 'semantic_search']
                }, ...prev]);
                // Add to activity log
                setActivityLog(prev => [...prev, {
                    timestamp: ragRetrievalEvent.data.timestamp,
                    activity: retrievalContent,
                    type: 'rag_retrieval'
                }]);
                break;

            default:
                console.warn('Unknown message type:', message.type);
        }
    };

    // Cleanup on unmount
    useEffect(() => {
        return () => {
            if (wsRef.current) {
                wsRef.current.close();
            }
        };
    }, []);

    return (
        <ScenarioContext.Provider value={{
            feed,
            worldModel,
            systemState,
            metrics,
            performance,
            currentActivity,
            activityLog,
            toggleAidaptiv,
            activeScenario,
            setActiveScenario,
            isAnalysisRunning,
            analysisState: isAnalysisRunning ? 'running' : (isCrashed ? 'crashed' : (isComplete ? 'completed' : 'idle')),
            crashDetails,
            isComplete,
            startAnalysis,
            stopAnalysis,
            showHardwareMonitor,
            toggleMonitor,
            resetAnalysis,
            tier,
            setTier,
            currentTier,
            enabledFeatures,
            upgradeMessage,
            elapsedSeconds,
            impactSummary,
            totalDocuments,
            backendConnected,
            backendError,
            ollamaConnected,
            ollamaError
        }}>
            {children}
        </ScenarioContext.Provider>
    );
};

export const useScenario = () => {
    const context = useContext(ScenarioContext);
    if (!context) throw new Error('useScenario must be used within a ScenarioProvider');
    return context;
};
