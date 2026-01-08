export type SourceType = 'news' | 'social_media' | 'report' | 'sensor_log' | 'AI_Agent';

export type BadgeType = 'PROCESSING' | 'ACTIVE' | 'COMPLETE' | 'ANALYZING' | 'WAITING' | 'WARNING';

export interface FeedItem {
    id: string;
    source: SourceType;
    author: string;
    content: string;
    timestamp: string;
    badge: BadgeType;
}

export type WorldModelStatus = 'vram' | 'ssd_cache' | 'pending';

export interface WorldModelItem {
    id: string;
    type: 'pdf_embedding' | 'screenshot';
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

export interface Scenario {
    id: string;
    title: string;
    subtitle: string;
    description: string;
    initialFeed: FeedItem[];
}
