export type SourceType = 'news' | 'social_media' | 'report' | 'sensor_log' | 'AI_Agent';

export type BadgeType = 'PROCESSING' | 'ACTIVE' | 'COMPLETE' | 'ANALYZING' | 'WAITING' | 'WARNING';

export interface FeedItem {
    id: string;
    source: SourceType;
    author: string;
    content: string;
    timestamp: string;
    badge: string;
}

export type WorldModelStatus = 'vram' | 'ssd_cache' | 'pending';

export interface WorldModelItem {
    id: string;
    type: 'screenshot' | 'pdf_embedding' | 'code';
    title: string;
    memorySize: number; // in MB
    lastAccessed: number;
    status: WorldModelStatus;
}

export interface SystemState {
    vramUsage: number; // in GB
    ramUsage: number; // in GB
    ssdUsage: number; // in GB
    isAidaptivEnabled: boolean;
    modelName: string;
}

export interface PerformanceMetrics {
    ttft_ms: number;
    tokens_per_second: number;
    latency_ms: number;
    status: 'optimal' | 'degraded' | 'critical';
    degradation_percent: number;
}

export interface ImpactSummaryData {
    documents_processed: number;
    total_documents: number;
    context_size_gb: number;
    memory_saved_gb: number;
    estimated_cost_local: number;
    estimated_cost_cloud: number;
    estimated_monthly_cost: number;
    time_minutes: number;
    time_without_aidaptiv: number;
}

export interface ImpactSummaryEvent {
    type: 'impact_summary';
    data: ImpactSummaryData;
}

// Re-export other event types if they were missing or implicit
export interface ThoughtEvent { type: 'thought'; data: any; }
export interface MemoryEvent { type: 'memory'; data: any; }
export interface DocumentEvent { type: 'document'; data: any; }
export interface PerformanceEvent { type: 'performance'; data: any; }
export interface StatusEvent { type: 'status'; message: string; }
export interface CompleteEvent { type: 'complete'; data: any; }

export interface CrashData {
    reason: string;
    processed_documents: number;
    total_documents: number;
    required_vram_gb: number;
    memory_snapshot?: any;
}

export interface CrashEvent {
    type: 'crash';
    data: CrashData;
}

export interface Scenario {
    id: string;
    title: string;
    subtitle: string;
    description: string;
    initialFeed: FeedItem[];
}
