# aiDAPTIV+ Demo - Marketing Intelligence Platform

## Business Purpose

**This is a sales demonstration for Phison aiDAPTIV+ SSDs.**

The demo proves that aiDAPTIV+ enables AI workloads that would otherwise crash on memory-constrained systems, eliminating the need for expensive cloud GPU instances.

### Target Audience
- **Primary:** IT Directors, System Architects, Hardware Buyers
- **Secondary:** Business stakeholders evaluating AI infrastructure ROI

### Value Proposition
- **Without aiDAPTIV+:** System runs out of memory (OOM crash), analysis fails
- **With aiDAPTIV+:** Memory seamlessly offloads to SSD, workload completes successfully

---

## What This Demo Does

Simulates an **ongoing marketing intelligence service** that continuously processes market signals through a strategic AI agent. The platform learns over time—as new data is ingested, the vector database grows and analysis quality improves. The demo uses CES 2026 as an example scenario, but the system is designed for continuous intelligence gathering across multiple events and timeframes.

The system:

1. **Ingests large data corpus** - Text documents, images, and video transcripts
2. **Stores data in Vector DB** - ChromaDB for semantic search and RAG retrieval
3. **Performs multi-step agentic reasoning** - Uses multiple LLM models (Llama 3.1, Qwen 2.5, LLaVA) for different tasks
4. **Maintains large context windows** - Demonstrates memory pressure and aiDAPTIV+ value
5. **Real-time telemetry** - Shows actual memory usage, KV cache, and system metrics

The demo uses **real system telemetry** and **real LLM generation** to demonstrate how aiDAPTIV+ enables workloads that would otherwise crash on memory-constrained systems.

### Value Proposition: Control vs Chaos

**Without aiDAPTIV+ (Uncontrolled Swapping):**
- macOS decides what to swap randomly
- Thrashing - constantly swapping active data in/out
- Unpredictable performance, system-wide slowdown, eventual OOM crash

**With aiDAPTIV+ (Intelligent Offloading):**
- Selective offloading of inactive context/embeddings
- Keep hot path (active inference) in RAM, cold data on SSD
- Predictable performance, no crashes, workload completes

**Key Insight:** aiDAPTIV+ doesn't make SSD faster - it makes the workload **completable** by preventing thrashing and avoiding OOM crashes.

---

## Core Architectural Features

This demo showcases four key AI architecture patterns:

### 🤖 **Agentic Workflow**
The system uses a **5-phase agentic reasoning cycle** that mimics how a human analyst would approach intelligence gathering:
1. **Document Review** - Survey available data sources
2. **Pattern Detection** - Identify trends and changes
3. **Technical Cross-Reference** - Link patterns to research papers
4. **Social Signal Validation** - Corroborate with industry signals
5. **Synthesis & Recommendations** - Generate strategic insights

Each phase builds on previous findings, creating a progressive analysis that demonstrates how AI agents can perform complex, multi-step reasoning tasks.

### 🔄 **Multi-Model Architecture**
The system dynamically swaps between **multiple specialized models** based on task requirements:
- **Llama 3.1 8B** - Fast text analysis (dossiers, news, social)
- **Qwen 2.5 14B** - Complex reasoning tasks (synthesis, cross-referencing)
- **LLaVA 13B** - Vision analysis (images, infographics)

Models are loaded/unloaded on-demand, demonstrating real memory pressure and the value of aiDAPTIV+ for managing multiple models.

### 👁️ **Multi-Modal Processing**
The demo processes **multiple data types** simultaneously:
- **Text** - Dossiers, news articles, social posts, video transcripts
- **Images** - Infographics, screenshots, competitor visuals
- **Structured Data** - Metadata, metrics, timestamps

Different models handle different modalities (LLaVA for images, Llama/Qwen for text), showing how modern AI systems combine specialized models for comprehensive analysis.

### 🔍 **RAG (Retrieval-Augmented Generation)**
The system uses **ChromaDB vector database** for semantic search and context augmentation:
- **Document Storage** - All documents are embedded and stored in Vector DB
- **Semantic Retrieval** - Before each analysis, relevant documents are retrieved based on meaning (not keywords)
- **Context Augmentation** - Retrieved documents enhance the current analysis context
- **Memory Efficiency** - Active context is pruned to Vector DB when exceeding RAM limits

This demonstrates how RAG enables AI systems to work with large knowledge bases while maintaining manageable memory footprints.

---

## What's Real vs. Simulated

### ✅ What is REAL
- **System Memory Telemetry:** RAM, Swap, and SSD usage metrics are pulled directly from the OS via `psutil` - these are actual physical measurements
- **LLM Generation:** All AI reasoning text is generated in real-time by local Ollama models (Llama 3.1, Qwen 2.5, LLaVA)
- **Model Loading:** Model weights are actually loaded into memory - model swaps cause real memory pressure
- **Crash Detection:** System crashes are triggered by actual memory exhaustion (swap delta > 2GB), not timers
- **KV Cache Telemetry:** When available, KV cache size is read from Ollama logs/API (falls back to formula-based estimate)
- **Vector Database:** ChromaDB stores and retrieves real document embeddings for RAG
- **Document Content:** Documents are real text files that are actually read and processed

### 🎭 What is SIMULATED
- **Business Metrics:** "Key Topics", "Patterns Detected", "Insights Generated" counters are narrative progress indicators (not extracted from LLM output)
- **KV Cache Estimation:** When Ollama telemetry is unavailable, KV cache is estimated using formulas (not actual measurement)
- **aiDAPTIV+ Offload:** The demo shows how aiDAPTIV+ *would* offload KV cache, but actual hardware offload requires aiDAPTIV+ SSD and driver installation

**Note:** The demo is designed to show real memory pressure and real AI workload behavior. The "simulated" aspects are primarily UI metrics and fallback estimates - the core memory and AI operations are real.

---

## Quick Start

### Prerequisites
- macOS (tested on Apple Silicon)
- 16GB RAM (to demonstrate memory pressure)
- Node.js 18+
- Python 3.9+
- [Ollama](https://ollama.ai) installed

### Installation

```bash
# 1. Install Ollama (if not already installed)
# macOS: brew install ollama
# Or download from https://ollama.ai

# 2. Start Ollama server (in separate terminal)
ollama serve

# 3. Pull required models
ollama pull llama3.1:8b      # Text analysis (all tiers)
ollama pull llava:13b        # Image analysis (standard/pro tiers)
ollama pull qwen2.5:14b       # Complex reasoning (pro tier)

# 4. Install dependencies
npm install
cd backend && pip install -r requirements.txt

# 5. Start services (3 terminals)
# Terminal 1: Backend
cd backend && python3 main.py

# Terminal 2: Frontend
npm run dev
```

### Optional: Live Reddit Feeds

The app can fetch live Reddit posts (no authentication required):

```bash
# Enable live feeds
export DATA_SOURCE_MODE=live

# Or hybrid mode (falls back to files if Reddit fails)
export DATA_SOURCE_MODE=hybrid
```

**What gets fetched:**
- Live posts from: r/LocalLLaMA, r/MachineLearning, r/hardware, r/buildapc, r/artificial
- Filtered by keywords: AI, memory, GPU, LLM, VRAM, RAM, DRAM, NAND, SSD
- No API keys or signup needed (uses public JSON endpoints)

**Optional OAuth setup** (for higher rate limits):
1. Create app at https://www.reddit.com/prefs/apps (select "script" type)
2. Set environment variables:
   ```bash
   export REDDIT_CLIENT_ID=your_client_id
   export REDDIT_CLIENT_SECRET=your_secret
   export REDDIT_USER_AGENT="aiDAPTIV-Demo/1.0"
   ```

**Test connection:**
```bash
python3 tests/test_reddit_simple.py
```

### Running the Demo

1. Open http://localhost:5173
2. Toggle **aiDAPTIV+ ON/OFF** to compare scenarios
3. Click **START ANALYSIS**
4. Watch the Hardware Monitor sidebar to see memory offload in action

---

## Architecture & Tech Stack

### Backend
- **Framework:** FastAPI (Python 3.9+)
- **LLM Engine:** Ollama (local inference)
- **Vector Database:** ChromaDB (RAG/semantic search)
- **Memory Monitoring:** psutil (system metrics)
- **WebSocket:** websockets (real-time streaming)
- **Data Processing:** sentence-transformers (embeddings), Pillow (images)

### Frontend
- **Framework:** React 19 + TypeScript
- **Build Tool:** Vite
- **Styling:** TailwindCSS + @tailwindcss/typography
- **Icons:** lucide-react
- **Markdown:** react-markdown

### AI Models
The demo uses multiple Ollama models dynamically based on task and system tier:

**Standard Tier (16GB+ RAM):**
- **Llama 3.1 8B** - General text analysis (dossiers, news, social signals)
- **LLaVA 13B** - Image analysis (infographics, screenshots, visual intelligence)

**Pro Tier (32GB+ RAM or aiDAPTIV+ enabled):**
- **Llama 3.1 8B** - Text analysis (fast, efficient)
- **LLaVA 13B** - Image and video analysis
- **Qwen 2.5 14B** - Complex reasoning tasks (multi-step analysis, synthesis)

Models are swapped dynamically during analysis based on task requirements and memory availability.

### Infrastructure
- **Communication:** WebSocket (real-time events), REST API (initialization)
- **Data Storage:** ChromaDB (vector embeddings), local filesystem (documents)
- **Memory System:** Hierarchical (RAM → SSD offload → Vector DB)

### Key Features

**"The Two Worlds" UI Design**

**Userland (Business Analyst View)**
- Live AI reasoning chain showing strategic synthesis
- Business metrics (Key Topics, Patterns, Insights, Critical Flags)
- Document processing grid

**Customer Land (IT Buyer View)**
- Real-time memory telemetry (RAM, Swap, SSD offload)
- Model swapping visualization
- Crash scenario when aiDAPTIV+ is disabled

**Technical Capabilities**

- **Real Memory Monitoring:** Uses `psutil` for actual system metrics (RAM, swap, KV cache)
- **Real LLM Generation:** Ollama generates insights in real-time with streaming responses
- **RAG (Retrieval-Augmented Generation):** ChromaDB vector database for semantic search
- **Multi-Model Support:** Dynamic model swapping (LLM, vision, reasoning models)
- **Context Management:** Hierarchical memory system (RAM → SSD → Vector DB)
- **WebSocket Streaming:** Real-time event streaming for live demo experience

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         Frontend (React)                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Dashboard  │  │HardwareMonitor│  │ ImpactMetrics│      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
│         │                  │                  │              │
│         └──────────────────┴──────────────────┘              │
│                            │                                 │
│                   ┌────────▼────────┐                        │
│                   │ ScenarioContext │                        │
│                   └────────┬────────┘                        │
└────────────────────────────┼──────────────────────────────────┘
                             │ WebSocket + REST
┌────────────────────────────▼──────────────────────────────────┐
│                      Backend (FastAPI)                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │   WebSocket  │  │  REST API    │  │MemoryMonitor │       │
│  │   Handler    │  │  Endpoints   │  │  (psutil)    │       │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘       │
│         │                  │                  │               │
│         └──────────────────┴──────────────────┘               │
│                            │                                  │
│         ┌──────────────────┴──────────────────┐              │
│         │                                      │              │
│  ┌──────▼────────┐                    ┌──────▼────────┐      │
│  │ Orchestrator  │                    │ DataSource    │      │
│  │               │                    │ (Static/Live) │      │
│  └──────┬────────┘                    └───────────────┘      │
│         │                                                      │
│         ├──────────────┬──────────────┬──────────────┐        │
│         │              │              │              │        │
│  ┌──────▼──────┐ ┌─────▼──────┐ ┌─────▼──────┐ ┌───▼──────┐ │
│  │ ContextMgr  │ │MemoryTier  │ │ SessionMgr  │ │SGPLoader │ │
│  │ (RAG/Vector)│ │ Manager    │ │ (Persistence)│ │(Strategy)│ │
│  └──────┬──────┘ └────────────┘ └────────────┘ └──────────┘ │
│         │                                                      │
│  ┌──────▼────────┐                                            │
│  │OllamaService  │                                            │
│  └──────┬────────┘                                            │
│         │                                                      │
│  ┌──────▼────────┐                                            │
│  │OllamaTelemetry│                                            │
│  │ (KV Cache)    │                                            │
│  └───────────────┘                                            │
└────────────────────────────────────────────────────────────────┘
                             │ HTTP API
┌────────────────────────────▼───────────────────────────────────┐
│                      Ollama Server                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│  │ llama3.1:8b  │  │qwen2.5:14b   │  │   llava:13b  │        │
│  │   (5GB)      │  │   (9GB)      │  │   (5GB)      │        │
│  └──────────────┘  └──────────────┘  └──────────────┘        │
└────────────────────────────────────────────────────────────────┘
                             │
┌────────────────────────────▼───────────────────────────────────┐
│                    ChromaDB (Vector DB)                       │
│  Document Embeddings (sentence-transformers)                  │
│  Semantic Search & RAG Retrieval                              │
│  Storage: backend/chroma_db/                                   │
└────────────────────────────────────────────────────────────────┘
```

---

## Design Philosophy: "The Two Worlds"

The demo presents two simultaneous perspectives to prove aiDAPTIV+ value:

### 1. Userland (The "Movie")
**Persona:** Business Analyst, Intelligence Officer, Researcher  
**Context:** A "War Room" dashboard for competitive intelligence  
**Goal:** Process massive amounts of data to find competitors, trends, and risks  
**Philosophy:** "I don't care about memory, I don't care about SSDs. I just need to process these 500 PDFs and get answers *now*."

**UI Elements:**
- **Main Dashboard:** The "mission control" interface
- **Reasoning Chain:** The stream of "thought" showing the AI working
- **Data Sources Grid:** The raw material being processed
- **Business Metrics:** Indicators of *value* generated

### 2. Customer Land (The "Reality")
**Persona:** IT Director, System Architect, Hardware Buyer  
**Context:** Observing the system strain under massive workload  
**Goal:** Prevent OOM crashes, reduce cloud costs, enable local large-model inference  
**Philosophy:** "How are they running a 70B model with 128k context on a workstation? Ah, it's aiDAPTIV+."

**UI Elements:**
- **Hardware Monitor (Sidebar):** Real-time system resource "truth"
- **Crash Screen:** The consequence of *not* having the hardware

### Metrics Strategy

**Userland Metrics (Analyst Dashboard)** - Measure Work & Value:
- **KEY TOPICS** - Distinct subjects identified across documents
- **PATTERNS DETECTED** - Recurring trends from correlation
- **INSIGHTS GENERATED** - Actionable conclusions synthesized
- **CRITICAL FLAGS** - High-priority anomalies requiring review

**Customer Land Metrics (Hardware Monitor)** - Measure Pressure & Capacity:
- **Context Tokens** - Volume of data "held in mind" (e.g., 60k / 128k)
- **KV Cache (GB)** - Memory cost of that context (~1GB+ for 60k tokens)
- **Model Weights (GB)** - Baseline model cost
- **Swap / Offload (GB)** - Overflowing memory handled by SSD

---

## Data Sources

### Current Implementation: Offline Files

Documents are **pre-generated offline** and saved to disk. The app loads them from files.

**Document Types:**
- **Dossiers** - Strategic competitor profiles (e.g., `data/realstatic/ces2026/dossier/`)
- **News** - Market announcements (e.g., `data/realstatic/ces2026/news/`)
- **Social** - Reddit/Twitter signals (e.g., `data/realstatic/ces2026/social/`)
- **Images** - Infographics, screenshots (e.g., `data/realstatic/ces2026/images/`)
- **Video Transcripts** - Keynote/demo transcripts (e.g., `data/realstatic/ces2026/video/`)

**Note:** The platform supports multiple scenarios and time periods. CES 2026 is used as an example dataset, but the system is designed for ongoing intelligence gathering across multiple events and timeframes.

**Loading Order:**
1. README (strategic context)
2. Dossiers (competitor intelligence)
3. Live Reddit data (if enabled)
4. News articles
5. Social signals (file-based)
6. Images
7. Video transcripts

**Advantages of Offline Generation:**
- ✅ Deterministic (same seed = same results)
- ✅ No API dependencies (works offline, no keys needed)
- ✅ Fast startup (no generation overhead)
- ✅ Inspectable (can review/edit files before running)
- ✅ Version controlled (files can be committed to git)

### Live Data Sources (Partial Implementation)

**Reddit Integration:**
- Uses public JSON endpoints (no authentication required)
- Fetches posts from: r/LocalLLaMA, r/MachineLearning, r/hardware, r/buildapc, r/artificial
- Filters by keywords: AI, memory, GPU, LLM, VRAM, RAM, DRAM, NAND, SSD
- Excludes: AutoModerator posts, administrative threads, deleted content

**Future Live Sources (Planned):**
- NewsAPI (tech news)
- Twitter/X API (tweets, threads)
- RSS feeds (Ars Technica, TechCrunch)

---

## Key Components

### Backend Components

#### **Orchestrator** (`backend/services/orchestrator.py`)
- Main simulation engine
- Manages event streaming
- Coordinates model swapping
- Implements background telemetry during model loads

#### **MemoryMonitor** (`backend/services/memory_monitor.py`)
- Uses `psutil` to get real system memory
- Tracks baseline swap usage
- Detects crash conditions (swap delta > 2GB)
- **KV Cache Tracking**: Uses `OllamaTelemetry` to get real KV cache stats from Ollama logs/API, falls back to formula-based estimate

#### **OllamaTelemetry** (`backend/services/ollama_telemetry.py`)
- Fetches real KV cache telemetry from Ollama
- **Primary**: Parses Ollama server logs (`~/.ollama/logs/server.log`) for KV buffer size
- **Secondary**: Uses Ollama API `/api/ps` endpoint for `context_length`
- **Fallback**: Formula-based estimate if telemetry unavailable

#### **ChromaDB** (`backend/vector_db/chroma_client.py`)
- Vector database for RAG (Retrieval-Augmented Generation)
- Stores document embeddings using sentence-transformers
- Performs semantic search for context retrieval
- Persistent storage in `backend/chroma_db/`

#### **ContextManager** (`backend/services/context_manager.py`)
- Manages hierarchical memory system (RAM → SSD → Vector DB)
- Handles active context (documents in RAM)
- Prunes context when exceeding threshold (60K tokens)
- Stores documents in ChromaDB for RAG retrieval

#### **OllamaService** (`backend/services/ollama_service.py`)
- Interfaces with Ollama API
- Manages document context building
- Streams LLM responses with accurate token counting
- Handles vision models (LLaVA) for image analysis

### Frontend Components

#### **ScenarioContext** (`src/ScenarioContext.tsx`)
- Global state management
- WebSocket connection handling
- Event processing and state updates

#### **HardwareMonitor** (`src/components/HardwareMonitor.tsx`)
- Real-time memory visualization
- Shows RAM, Swap, Context Tokens, KV Cache, Model Weights
- Updates at 1Hz during simulation

#### **Dashboard** (`src/components/Dashboard.tsx`)
- Main UI container
- Activity feed with markdown rendering
- Metrics cards (Key Topics, Patterns, Insights, Critical Flags)
- Document processing grid

---

## Vector Database & RAG Workflow

The system uses **ChromaDB** as a vector database for RAG (Retrieval-Augmented Generation), enabling semantic search across all processed documents. This creates a hierarchical memory system:

1. **Active Context (RAM)** - Current documents being analyzed (max 60K tokens)
2. **Recent Context (SSD)** - Offloaded by aiDAPTIV+ automatically
3. **Long-term Memory (Vector DB)** - All documents stored with embeddings for semantic retrieval

### How It Works

**Document Storage:**
- All documents are embedded using `all-MiniLM-L6-v2` (384-dimensional vectors)
- Stored in ChromaDB with metadata (category, title, tokens, timestamp)
- Persistent storage in `backend/chroma_db/`

**RAG Retrieval:**
- Before each analysis step, relevant documents are retrieved based on semantic similarity
- Query built from current document batch
- Top-K similar documents retrieved (up to 3K tokens)
- Excludes current batch documents to avoid duplicates

**Context Pruning:**
- When active context exceeds 60K tokens, oldest documents are moved to Vector DB
- Documents remain searchable via semantic search
- Active context reduced to ~54K tokens (90% of limit)

---

## Memory Telemetry

### Real-Time Updates (1Hz)

Memory telemetry updates every second during simulation:

```python
{
    "unified_percent": 66.8,      # RAM usage %
    "unified_gb": 13.2,            # RAM usage GB
    "unified_total_gb": 16.0,      # Total RAM
    "virtual_percent": 60.1,       # Swap usage %
    "virtual_gb": 2.4,             # Swap usage GB
    "virtual_active": true,        # Swap > 100MB
    "context_tokens": 50000,       # Current context size
    "kv_cache_gb": 0.75,           # KV cache size (from Ollama or estimate)
    "model_weights_gb": 5.0,      # Model size
    "loaded_model": "llama3.1:8b"  # Current model
}
```

### KV Cache Telemetry

The KV cache size is tracked using a **multi-tier approach**:

1. **Primary Source: Ollama Server Logs** (`~/.ollama/logs/server.log`)
   - Parses log entries for KV buffer size: `CUDA0 KV buffer size = 224.00 MiB`
   - Most accurate when available

2. **Secondary Source: Ollama API** (`/api/ps` endpoint)
   - Gets `context_length` from running processes
   - Uses context length for improved estimate

3. **Fallback: Formula-Based Estimate**
   - Formula: `(context_tokens / 1000) × 0.015 GB × model_scale_factor`
   - ~15MB per 1000 tokens for 8B model
   - Scales proportionally with model size

---

## Crash Detection

Crash detection is based on actual swap usage:

```python
# Capture baseline swap at start
baseline_swap_gb = psutil.swap_memory().used / (1024**3)

# During simulation
current_swap_gb = psutil.swap_memory().used / (1024**3)
swap_delta = current_swap_gb - baseline_swap_gb

# Crash if swap increased by >2GB without aiDAPTIV+
if not aidaptiv_enabled and swap_delta > 2.0:
    should_crash = True
```

**Why Delta-Based?**
- User's Mac may already have 2-3GB swap in use
- Absolute threshold would false-trigger
- Delta shows swap **caused by the simulation**

---

## API Endpoints

### REST
- `GET /api/health` - Health check
- `GET /api/system/info` - Get system memory/CPU info
- `GET /api/memory/current` - Get current memory usage (baseline)
- `GET /api/scenarios` - List available scenarios
- `POST /api/scenarios/start` - Start simulation (returns WebSocket URL)
- `GET /api/capabilities` - Get tier-based feature availability
- `GET /api/ollama/status` - Check Ollama service status

### WebSocket
- `ws://localhost:8000/ws/analysis` - Event stream

**Query Parameters:**
- `scenario` - Scenario ID (e.g., "ces2026" - can be any event/timeframe)
- `tier` - Tier (e.g., "standard" or "pro")
- `aidaptiv` - Enable aiDAPTIV+ (true/false)

---

## Incomplete Features & Future Work

### Phase 1: Core Demo (Current State)

**✅ Completed:**
- Real system memory monitoring (psutil)
- Real LLM generation (Ollama)
- WebSocket streaming
- Multi-model support (Llama, Qwen, LLaVA)
- RAG with ChromaDB vector database
- Context management and pruning
- Crash detection based on real swap usage
- KV cache telemetry (with fallback estimates)

**⏳ Partially Complete:**
- **KV Cache Telemetry**: Uses real Ollama logs/API when available, but falls back to formula-based estimates
- **Reddit Integration**: Simple public JSON endpoint implemented, but OAuth API not integrated
- **Document Processing**: Real text files are processed, but business metrics are simulated

### Phase 2: Enhanced Realism

**🚀 High Priority:**

1. **Real Analysis Metrics Extraction**
   - Metrics are currently incremented based on progress percentage
   - Should extract from actual LLM output using JSON mode or structured parsing
   - Enable JSON mode in Ollama requests (`format: "json"`)
   - Parse structured output from LLM
   - Count actual entities, topics, patterns from analysis

2. **VLLM Integration for Exact KV Cache Stats**
   - Currently uses Ollama logs/API (when available) or formula-based estimates
   - VLLM API would provide exact KV cache measurements
   - Fallback chain: VLLM API → Ollama logs → Ollama API → Formula estimate

### Phase 3: Live Data Sources

**🚀 High Priority:**

3. **Live News Fetching**
   - `LiveDataSource.fetch_news()` method exists but returns empty list
   - Implement NewsAPI integration (free tier: 100 requests/day)
   - Implement RSS feed parsing (TechCrunch, Ars Technica, The Verge, Hacker News)
   - Add caching layer (1 hour TTL)
   - Add rate limiting

4. **Reddit OAuth API Integration**
   - Simple public JSON endpoint works ✅
   - OAuth API client exists but not fully integrated
   - Needs proper error handling, rate limiting, caching

5. **Twitter/X API Integration**
   - No Twitter client exists
   - OAuth 2.0 flow needed
   - Rate limits: 1,500 tweets/month (free tier)

6. **RSS Feed Integration (Fallback)**
   - RSS feed parser doesn't exist
   - Should be fallback when APIs fail
   - Parse RSS feeds (TechCrunch, Ars Technica, The Verge, Hacker News)

7. **Live Data Caching & Rate Limiting**
   - No caching layer for API responses
   - No rate limiting implementation
   - Create `cache.py` for response caching (disk-based JSON, TTL-based expiration)
   - Create `rate_limiter.py` for API rate limit tracking

### Phase 4: Hardware Integration

**🚀 High Priority:**

8. **Actual aiDAPTIV+ Hardware Integration**
   - KV cache offload is simulated/conceptual
   - No actual hardware driver integration
   - No real SSD offload happening
   - Integrate aiDAPTIV+ SDK/driver
   - Real-time monitoring of actual unified memory usage
   - Automatic offloading of LLM KV cache to Phison SSD

### Phase 5: Advanced Features

**🟢 Medium Priority:**

9. **Multi-Model Support (External APIs)**
   - Currently only supports Ollama (local models)
   - Add support for OpenAI API (GPT-4)
   - Add support for Anthropic API (Claude)
   - Add support for Google API (Gemini)

10. **Document Content Analysis (Not Just Metadata)**
    - Enhanced document parsing (extract entities, dates, relationships)
    - Structured data extraction from documents
    - Cross-reference analysis between documents
    - Build knowledge graph from document relationships

11. **Session History & Persistence**
    - Session manager exists ✅
    - Sessions are saved to disk ✅
    - **BUT:** No UI to view session history
    - Add session history UI component
    - Display previous runs with metrics
    - Compare runs (with/without aiDAPTIV+)

---

## Troubleshooting

### Model Swap Not Visible
**Symptom:** Phase 2 skipped, no model swap  
**Cause:** Trigger percentage too high  
**Fix:** Adjust `trigger_percent` in `ANALYSIS_PHASES`

### Memory Not Updating
**Symptom:** Telemetry shows 0GB or doesn't change  
**Cause:** Backend not sending events or frontend not processing  
**Fix:** Check WebSocket connection, verify `calculate_memory()` is called

### Slow Model Loading
**Symptom:** qwen2.5:14b takes >30s to load  
**Cause:** System swapping heavily, not enough RAM  
**Fix:** Use smaller model (qwen2.5:7b) or close other apps

### Crash Detection Not Working
**Symptom:** Large tier doesn't crash without aiDAPTIV+  
**Cause:** Swap delta < 2GB threshold  
**Fix:** Adjust threshold in `memory_monitor.py` or use larger model

---

## Project Structure

```
├── backend/              # FastAPI server
│   ├── services/         # Orchestrator, Memory Monitor, Ollama integration
│   └── api/              # WebSocket + REST endpoints
├── src/                  # React frontend
│   ├── components/       # Dashboard, HardwareMonitor
│   └── ScenarioContext.tsx  # State management
├── data/
│   ├── realstatic/         # Real intelligence sources (e.g., ces2026/)
│   │   ├── dossier/        # Competitor profiles
│   │   ├── news/           # Market announcements
│   │   └── social/         # Developer signals
│   ├── dummy/              # Dummy/test data
│   └── generated/          # Generated data
```

---

## License

Proprietary - Phison Electronics Corp.
