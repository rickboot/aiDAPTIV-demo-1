import type { Scenario, FeedItem, WorldModelItem } from './types';

// SCENARIO 1: PMM Competitive Intelligence (DEFAULT)
// Initial Feed (Static history)
const PMM_INITIAL_FEED: FeedItem[] = [
    { id: 'p-0', source: 'AI_Agent', author: '@AI_Agent', content: 'Monitoring active data pipelines for Q1 2026...', timestamp: '2h ago', badge: 'WAITING' },
];

export const SCENARIOS: Scenario[] = [
    {
        id: 'pmm_war_room',
        title: 'PMM Competitive Intelligence',
        subtitle: 'Real-time competitor analysis across visual & technical sources',
        description: 'Competitor Analysis',
        initialFeed: PMM_INITIAL_FEED
    },
    // ... (Keep other scenarios for completeness if needed, or simplify) ...
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

export const MOCK_FEED = PMM_INITIAL_FEED;

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

// Success Report Data
export const SUCCESS_REPORT = {
    title: "Analysis Complete",
    mainInsight: "Competitor Market Pivot Detected",
    finding: "3 major competitors are quietly shifting from RAG to Agentic Architectures.",
    evidence: [
        "Visual: 12 new 'reasoning' UI patterns detected.",
        "Technical: 8 citations of 'Multi-Step Reasoning' in recent whitepapers.",
        "Timeline: All changes occurred within the last 14 days."
    ],
    implication: "Immediate risk of feature gap in Q1 2026. Recommendation: Acceleration of Agentic Roadmap.",
    stats: {
        contextProcessed: "460 GB",
        ssdOffload: "220 GB",
        gpuUtil: "98%"
    }
};

// Start metrics (increment from here)
export const INITIAL_METRICS = {
    key_topics: 0,
    patterns_detected: 0,
    insights_generated: 0,
    critical_flags: 0
};
