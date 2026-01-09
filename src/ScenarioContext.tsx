import { createContext, useContext, useState, useEffect, useRef, type ReactNode } from 'react';
import type { CompleteEvent, FeedItem, MemoryEvent, PerformanceMetrics, Scenario, StatusEvent, SystemState, ThoughtEvent, PerformanceEvent, ImpactSummaryEvent, ImpactSummaryData, WorldModelItem, CrashEvent, CrashData } from './types';
import { SCENARIOS, INITIAL_WORLD_MODEL, INITIAL_METRICS } from './mockData';

interface Metrics {
    entities_extracted: number;
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
    impactSummary: ImpactSummaryData | null;
    crashDetails: CrashData | null;
    startAnalysis: () => Promise<void>;
    stopAnalysis: () => void;
    showHardwareMonitor: boolean;
    toggleMonitor: () => void;
    isSuccess: boolean;
    isComplete: boolean;
    showResults: () => void;
    closeResults: () => void;
    resetAnalysis: () => void;
    tier: 'lite' | 'large';
    setTier: (tier: 'lite' | 'large') => void;
}

const ScenarioContext = createContext<ScenarioContextType | undefined>(undefined);

const WS_URL = 'ws://localhost:8000/ws/analysis';

export const ScenarioProvider = ({ children }: { children: ReactNode }) => {
    // STATE
    const [activeScenario, setActiveScenarioState] = useState<Scenario>(SCENARIOS[0]);
    const [feed, setFeed] = useState<FeedItem[]>(activeScenario.initialFeed);
    const [worldModel, setWorldModel] = useState<WorldModelItem[]>([]); // Start empty, populate dynamically
    const [metrics, setMetrics] = useState<Metrics>(INITIAL_METRICS);

    const [isAnalysisRunning, setIsAnalysisRunning] = useState(false);
    const [isSuccess, setIsSuccess] = useState(false);
    const [isComplete, setIsComplete] = useState(false);
    const [isCrashed, setIsCrashed] = useState(false);

    const [showHardwareMonitor, setShowHardwareMonitor] = useState(true); // Enabled by default for dev
    const [tier, setTierState] = useState<'lite' | 'large'>('lite'); // Default to lite for faster demos

    const INITIAL_PERFORMANCE: PerformanceMetrics = {
        ttft_ms: 0,
        tokens_per_second: 0,
        latency_ms: 0,
        status: 'optimal',
        degradation_percent: 0
    };
    const [performance, setPerformance] = useState<PerformanceMetrics>(INITIAL_PERFORMANCE);

    const [impactSummary, setImpactSummary] = useState<ImpactSummaryData | null>(null);
    const [crashDetails, setCrashDetails] = useState<CrashData | null>(null);

    const [currentActivity, setCurrentActivity] = useState<string>('Idle');

    const [systemState, setSystemState] = useState<SystemState>({
        vramUsage: 0,
        totalMemory: 16,
        ramUsage: 16.0,
        ssdUsage: 0,
        isAidaptivEnabled: false,
        modelName: 'Llama-3-70B'
    });

    // WebSocket ref
    const wsRef = useRef<WebSocket | null>(null);

    // ACTIONS
    const setActiveScenario = (id: string) => {
        const found = SCENARIOS.find(s => s.id === id);
        if (found) {
            setActiveScenarioState(found);
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
        setIsSuccess(false);
        setIsComplete(false);
        setIsCrashed(false);
        setImpactSummary(null);
        setCrashDetails(null);
        setSystemState(prev => ({ ...prev, vramUsage: 0, ramUsage: 16.0, ssdUsage: 0 }));
        setWorldModel([]); // Clear to repopulate dynamically
        setFeed(activeScenario.initialFeed);
        setMetrics(INITIAL_METRICS);
        setPerformance(INITIAL_PERFORMANCE);
        setCurrentActivity('Idle');
    };

    const showResults = () => {
        setIsSuccess(true);
    };

    const closeResults = () => {
        // Just close the overlay, don't reset anything
        setIsSuccess(false);
        setIsComplete(false);
    };

    const toggleMonitor = () => setShowHardwareMonitor(prev => !prev);

    const setTier = (newTier: 'lite' | 'large') => {
        if (!isAnalysisRunning) {
            setTierState(newTier);
        }
    };

    const toggleAidaptiv = () => {
        if (!isAnalysisRunning) {
            setSystemState(prev => ({ ...prev, isAidaptivEnabled: !prev.isAidaptivEnabled }));
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
            }
        };
        fetchCurrentMemory();
    }, []);

    const startAnalysis = async () => {
        if (isAnalysisRunning) return;
        setIsAnalysisRunning(true);
        setIsComplete(false);
        setIsSuccess(false);
        setIsCrashed(false);
        setImpactSummary(null);
        setCrashDetails(null);
        setCurrentActivity('Initializing analysis...');

        if (tier === 'large') {
            await new Promise(resolve => setTimeout(resolve, 1000)); // Simulate connection delay for large
        }

        // Connect to WebSocket
        console.log('Connecting to WebSocket:', WS_URL);
        const ws = new WebSocket(WS_URL);
        wsRef.current = ws;

        ws.onopen = () => {
            console.log('WebSocket connected');

            // Send simulation parameters
            const params = {
                scenario: activeScenario.id === 'pmm_war_room' ? 'pmm' : activeScenario.id,
                tier: tier,
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
    };

    // Handle WebSocket messages
    const handleWebSocketMessage = (message: any) => {
        switch (message.type) {
            case 'init':
                // Initialize world model with all documents
                if (message.data.documents) {
                    const initialModel = message.data.documents.map((doc: any, index: number) => ({
                        id: `doc-${index}`,
                        type: doc.category === 'competitor' ? 'screenshot' : 'pdf_embedding',
                        title: doc.name,
                        memorySize: 50,
                        lastAccessed: Date.now(),
                        status: 'pending'
                    }));
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
                    relatedDocIds: message.data.related_doc_ids
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
                    model_weights_gb: message.data.model_weights_gb || 0
                }));
                break;

            case 'document':
                // Update world model - mark document as processed
                setCurrentActivity(`Processing: ${message.data.name}`);
                setWorldModel(prev => {
                    const newModel = [...prev];
                    const index = message.data.index;

                    // Create entry if it doesn't exist (dynamic sizing)
                    if (!newModel[index]) {
                        newModel[index] = {
                            id: `doc-${index}`,
                            type: message.data.category === 'competitor' ? 'screenshot' : 'pdf_embedding',
                            title: message.data.name,
                            memorySize: message.data.size_kb || 50, // Use actual size from backend
                            lastAccessed: Date.now(),
                            status: 'vram'
                        };
                    } else {
                        // Update existing entry
                        newModel[index] = {
                            ...newModel[index],
                            title: message.data.name,
                            type: message.data.category === 'competitor' ? 'screenshot' : 'pdf_embedding',
                            memorySize: message.data.size_kb || 50,
                            status: 'vram',
                            lastAccessed: Date.now()
                        };
                    }
                    return newModel;
                });
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
                // Update metrics - map backend names to frontend names
                const metricNameMap: { [key: string]: keyof Metrics } = {
                    'visual_updates': 'visuals',
                    'papers_analyzed': 'papers',
                    'signals_detected': 'signals',
                    'competitors_tracked': 'competitors'
                };

                const frontendMetricName = metricNameMap[message.data.name];
                if (frontendMetricName) {
                    setMetrics(prev => ({
                        ...prev,
                        [frontendMetricName]: message.data.value
                    }));
                }
                break;

            case 'complete':
                // Analysis complete
                setCurrentActivity('Analysis complete');
                console.log('Simulation complete:', message.data);
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

            case 'impact_summary':
                const impactEvent = message as ImpactSummaryEvent;
                setImpactSummary(impactEvent.data);
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
            impactSummary,
            crashDetails,
            startAnalysis,
            stopAnalysis,
            showHardwareMonitor,
            toggleMonitor,
            isSuccess,
            isComplete,
            showResults,
            closeResults,
            resetAnalysis,
            tier,
            setTier
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
