import { createContext, useContext, useState, useEffect, useRef, type ReactNode } from 'react';
import type { FeedItem, SystemState, PerformanceMetrics, Scenario, WorldModelItem, CrashData, CrashEvent, ImpactSummaryData } from './types';
import { SCENARIOS, INITIAL_METRICS } from './mockData';

interface Metrics {
    key_topics: number;
    patterns_detected: number;
    insights_generated: number;
    critical_flags: number;
}

interface ScenarioContextType {
    feed: FeedItem[];
    worldModel: WorldModelItem[];
    systemState: SystemState;
    metrics: Metrics;
    performance: PerformanceMetrics;
    currentActivity: string;
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
    backendConnected: boolean;
    backendError: string | null;
}

const ScenarioContext = createContext<ScenarioContextType | undefined>(undefined);

const WS_URL = 'ws://localhost:8000/ws/analysis';

export const ScenarioProvider = ({ children }: { children: ReactNode }) => {
    // STATE
    const [activeScenario, setActiveScenarioState] = useState<Scenario>(SCENARIOS[0]); // CES 2026 is now the only scenario
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
    const [impactSummary, setImpactSummary] = useState<ImpactSummaryData | null>(null);
    const [backendConnected, setBackendConnected] = useState(true);
    const [backendError, setBackendError] = useState<string | null>(null);

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
        setSystemState(prev => ({ ...prev, vramUsage: 0, ramUsage: 16.0, ssdUsage: 0 }));
        setWorldModel([]); // Clear to repopulate dynamically
        setFeed(activeScenario.initialFeed);
        setMetrics(INITIAL_METRICS);
        setPerformance(INITIAL_PERFORMANCE);
        setCurrentActivity('Idle');
    };


    const toggleMonitor = () => setShowHardwareMonitor(prev => !prev);

    const setTier = (newTier: 'lite' | 'large') => {
        if (!isAnalysisRunning) {
            setTierState(newTier);
        }
    };

    const toggleAidaptiv = () => {
        console.log('toggleAidaptiv called, isAnalysisRunning:', isAnalysisRunning);
        console.log('Current isAidaptivEnabled:', systemState.isAidaptivEnabled);
        if (!isAnalysisRunning) {
            setSystemState(prev => {
                const newState = { ...prev, isAidaptivEnabled: !prev.isAidaptivEnabled };
                console.log('Setting new isAidaptivEnabled:', newState.isAidaptivEnabled);
                return newState;
            });
        } else {
            console.log('Toggle blocked - analysis is running');
        }
    };

    // Load system info on mount
    useEffect(() => {
        const fetchSystemInfo = async () => {
            try {
                const response = await fetch('http://localhost:8000/api/system/info');
                if (response.ok) {
                    const data = await response.json();
                    console.log('Detected System:', data);
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
                    console.log('Baseline Memory:', data);
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

    // Fetch capabilities on mount and when aiDAPTIV+ changes
    useEffect(() => {
        const fetchCapabilities = async () => {
            try {
                const response = await fetch(`http://localhost:8000/api/capabilities?aidaptiv_enabled=${systemState.isAidaptivEnabled}`);
                if (response.ok) {
                    const data = await response.json();
                    console.log('Capabilities:', data);
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

        if (activeScenario.id.includes('large')) {
            await new Promise(resolve => setTimeout(resolve, 1000)); // Simulate connection delay for large
        }

        // Connect to WebSocket
        console.log('Connecting to WebSocket:', WS_URL);
        const ws = new WebSocket(WS_URL);
        wsRef.current = ws;

        ws.onopen = () => {
            console.log('WebSocket connected');

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

            console.log('Sending simulation params:', params);
            ws.send(JSON.stringify(params));
        };

        ws.onmessage = (event) => {
            const message = JSON.parse(event.data);
            console.log('Received event:', message.type, message.data);

            handleWebSocketMessage(message);
        };

        ws.onerror = (error) => {
            console.error('WebSocket error:', error);
        };

        ws.onclose = () => {
            console.log('WebSocket disconnected');
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
                if (message.data.documents) {
                    const initialModel = message.data.documents.map((doc: any, index: number) => {
                        // Detect type from filename
                        let type = 'text_document';
                        if (doc.name.endsWith('.png') || doc.name.endsWith('.jpg') || doc.name.endsWith('.jpeg')) {
                            type = 'screenshot';
                        } else if (doc.name.includes('video') || doc.name.includes('transcript')) {
                            type = 'video_transcript';
                        }

                        return {
                            id: `doc-${index}`,
                            type: type,
                            title: doc.name,
                            memorySize: doc.size_kb || 50, // Show actual size from backend immediately
                            lastAccessed: Date.now(),
                            status: 'pending'
                        };
                    });
                    setWorldModel(initialModel);
                }
                break;

            case 'thought':
                // Add thought to feed
                setCurrentActivity('AI Reasoning...');
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
                setSystemState(prev => ({
                    ...prev,
                    vramUsage: message.data.unified_gb,
                    totalMemory: message.data.unified_total_gb || 16,
                    ramUsage: message.data.unified_gb, // Deprecated field, keep in sync or ignore
                    ssdUsage: message.data.virtual_gb,
                    context_tokens: message.data.context_tokens || 0,
                    kv_cache_gb: message.data.kv_cache_gb || 0,
                    model_weights_gb: message.data.model_weights_gb || 0,
                    loaded_model: message.data.loaded_model || prev.loaded_model
                }));
                break;

            case 'document':
                // Update world model - mark document as processed
                setCurrentActivity(`Processing: ${message.data.name}`);
                setWorldModel(prev => {
                    const newModel = [...prev];
                    const index = message.data.index;

                    // Map category to display type
                    const getFileType = (category: string) => {
                        switch (category) {
                            case 'competitor': return 'screenshot';
                            case 'paper': return 'pdf_embedding';
                            case 'image': return 'screenshot'; // Images show as screenshots
                            case 'video': return 'video_transcript';
                            case 'dossier':
                            case 'news':
                            case 'social':
                            case 'documentation':
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
                        // Update existing entry
                        newModel[index] = {
                            ...newModel[index],
                            title: message.data.name,
                            type: getFileType(message.data.category),
                            memorySize: message.data.size_kb || 50,
                            status: 'processing',
                            lastAccessed: Date.now()
                        };
                    }
                    return newModel;
                });
                break;

            case 'document_status':
                console.log('Received document_status:', message.data);
                setWorldModel(prev => {
                    const newModel = [...prev];
                    const { index, status } = message.data;
                    if (newModel[index]) {
                        console.log(`Updating doc ${index} status to ${status}`);
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
                break;

            case 'metric':
                // Update metrics - names match 1:1 with backend
                setMetrics(prev => ({
                    ...prev,
                    [message.data.name]: message.data.value
                }));
                break;

            case 'complete':
                // Analysis complete - preserve final elapsed time
                setCurrentActivity('Analysis complete');
                console.log('Simulation complete:', message.data);

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
                console.log('Simulation crashed:', crashEvent.data);
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
            backendConnected,
            backendError
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
