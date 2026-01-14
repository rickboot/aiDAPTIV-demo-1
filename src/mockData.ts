import type { Scenario, FeedItem, WorldModelItem } from './types';

// SCENARIO: Marketing Intelligence (Phison-specific)
const MARKETING_INTEL_INITIAL_FEED: FeedItem[] = [
    { id: 'intel-0', source: 'AI_Agent', author: '@Virtual_PMM', content: 'Marketing intelligence monitoring active. Scanning for AI, DRAM, NAND, OEM, and competitive signals...', timestamp: '1h ago', badge: 'WAITING' },
];

export const SCENARIOS: Scenario[] = [
    {
        id: 'mktg_intelligence_demo',
        title: 'Marketing Intelligence',
        subtitle: 'Competitive Intelligence Analysis',
        description: 'Strategic Intelligence for aiDAPTIV+',
        initialFeed: MARKETING_INTEL_INITIAL_FEED
    }
];

// GRID: 96 Items
export const INITIAL_WORLD_MODEL: WorldModelItem[] = Array.from({ length: 96 }).map((_, i) => {
    const isUI = i < 48;
    return {
        id: `item-${i}`,
        type: isUI ? 'screenshot' : 'pdf_embedding',
        title: isUI ? `Comp_UI_${i + 1}` : `arXiv_2401.${100 + i}`,
        memorySize: 50,
        lastAccessed: Date.now(),
        status: 'pending'
    };
});

export const MOCK_FEED = MARKETING_INTEL_INITIAL_FEED;

// --- NEW DEMO DATA ---

// Dynamic Thoughts Stream (injected during simulation)
export const DEMO_THOUGHTS = [
    { time: 2, content: 'Identifying new UI components in competitor screenshots...', badge: 'PROCESSING' },
    { time: 5, content: 'Detected specific shift: "Chat-first navigation" patterns in Comp A & B.', badge: 'OOM_RISK' }, // Mapping 'OOM_RISK' to 'ANALYZING' later for safety or adding new badge
    { time: 8, content: 'Cross-referencing 48 arXiv papers for "Agentic Pattern" definitions.', badge: 'ACTIVE' },
    { time: 12, content: '⚠️ MEMORY PRESSURE: Visual Embeddings exceeding 24GB VRAM.', badge: 'PROCESSING' },
    { time: 15, content: 'aiDAPTIV+ OFFLOAD TRIGGERED: Moving 220GB cold segments to SSD Cache.', badge: 'ACTIVE' }, // Only show if enabled
    { time: 20, content: 'Correlating technical whitepapers with UI visual changes...', badge: 'ANALYZING' },
    { time: 25, content: 'Pattern Confirmation: 80% certainty on "Agentic Pivot".', badge: 'COMPLETE' }
];


// Start metrics (increment from here)
export const INITIAL_METRICS = {
    key_topics: 0,
    patterns_detected: 0,
    insights_generated: 0,
    critical_flags: 0
};
