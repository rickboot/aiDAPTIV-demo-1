# aiDAPTIV+ Demo – Marketing Intelligence Platform

## Business Purpose

This repository is a demo and engineering testbed for exploring how aiDAPTIV+ could help AI workloads run on systems with limited memory.

**Current status:** This early version does not include real aiDAPTIV+ support. It creates real memory pressure and runs real local models, but SSD offload is not implemented in this codebase yet.

## Target Audience

- **Primary:** System architects, IT teams, hardware platform teams
- **Secondary:** Product and business teams evaluating local vs. cloud tradeoffs

## Goal

- **Without aiDAPTIV+:** The system can run out of memory and the workload may fail
- **With aiDAPTIV+ (future integration):** The workload should complete by offloading memory pressure to SSD

## What This Demo Does

This demo simulates an ongoing marketing intelligence service that processes market signals over time. As new data is ingested, the vector database grows and the system can retrieve more relevant history.

The system:

- Ingests a large data set – text documents, images, and video transcripts
- Stores data in a Vector DB – ChromaDB for semantic search and RAG retrieval
- Runs a multi-step workflow – uses multiple models (Llama 3.1, LLaVA) for different tasks
- Maintains large context windows – creates memory pressure and exposes failure modes
- Shows real-time telemetry – displays memory usage, KV cache estimates, and system metrics

The demo uses real system telemetry and real LLM generation. This helps show what happens when a workload pushes beyond available memory.

## Behavior Under Memory Pressure

### Without aiDAPTIV+ (OS swap only):

- The OS swaps memory to disk as needed
- Performance can become unstable as swapping increases
- The system may slow down or the workload may fail

### With aiDAPTIV+ (future integration):

- Offload can focus on less-active data (for example older context or embeddings)
- Keep active inference data in RAM as much as possible
- The goal is stable execution and workload completion

**Key point:** aiDAPTIV+ is not expected to make SSD faster. The goal is to make the workload run to completion on limited-memory systems.

## Core Architectural Features

This demo uses four common AI system patterns:

### Agent Workflow

The system runs a multi-step workflow similar to an analyst process:

1. **Load Context** – Review available documents (dossiers, news, strategic context) and summarize key information and data sources
2. **Analyze Documents** – Analyze news articles, technical specifications, and market reports to identify patterns and trends with specific findings
3. **Analyze Video/Images** – Extract insights from video transcripts and images, correlating visual content with document findings
4. **Analyze User Feedback** – Check social media signals (Reddit, Twitter, forums) and validate findings with real user feedback
5. **Generate Summary** – Synthesize findings from all sources and provide actionable recommendations

Each step builds on earlier results. This requires keeping context across steps, which increases memory usage.

### Multi-Model Architecture

The system swaps between models based on the task:

- **Llama 3.1 8B** – text analysis (dossiers, news, social, video transcripts)
- **LLaVA 13B** – image analysis (images, infographics)

Models load/unload on demand, which creates real memory pressure.

### Multi-Modal Processing

The demo processes multiple data types:

- **Text** – dossiers, news, social posts, video transcripts
- **Images** – infographics, screenshots, competitor visuals
- **Structured data** – metadata, metrics, timestamps

Different models handle different input types (vision vs. text).

### RAG (Retrieval-Augmented Generation)

The system uses ChromaDB for semantic search and context expansion:

- **Document storage** – documents are embedded and stored in a vector DB
- **Semantic retrieval** – retrieve relevant documents by meaning, not keywords
- **Context augmentation** – retrieved documents are added to the current step context
- **Memory control** – active context is limited; older content stays in the vector DB

This helps the system work with larger knowledge bases while controlling RAM usage.

## What's Real vs. Simulated

### What is REAL

- **System memory telemetry:** RAM and swap metrics from the OS via psutil
- **LLM generation:** real-time output from local Ollama models
- **Model loading:** model weights load into memory and create real pressure
- **Crash detection:** triggered by real memory exhaustion (swap delta threshold)
- **KV cache telemetry:** read from Ollama logs/API when available (otherwise estimated)
- **Vector DB:** ChromaDB stores and retrieves real embeddings
- **Document content:** documents are real files that are read and processed

### What is SIMULATED / ESTIMATED

- **Business metrics:** counters are progress indicators (not extracted from LLM output)
- **KV cache estimation:** formula-based when Ollama telemetry is unavailable
- **aiDAPTIV+ offload:** conceptual only in this repo (requires hardware + drivers)

**Note:** The demo is designed so the core workload behavior is real (models, memory, DB). Only the aiDAPTIV+ SSD offload is not yet implemented.

## Quick Start

### Prerequisites

- macOS (tested on Apple Silicon)
- 16GB RAM (recommended to see memory pressure)
- Node.js 18+
- Python 3.9+
- Ollama installed

### Installation

```bash
# 1. Start Ollama (in a separate terminal)
ollama serve

# 2. Pull required models
ollama pull llama3.1:8b      # Text analysis
ollama pull llava:13b        # Image analysis

# 3. Install dependencies
npm install
cd backend && pip install -r requirements.txt

# 4. Start services (2 terminals)
# Terminal 1: Backend
cd backend && python3 main.py

# Terminal 2: Frontend
npm run dev
```

### Optional: Live Reddit Feeds

The app can fetch live Reddit posts (no authentication required):

```bash
export DATA_SOURCE_MODE=live
# or
export DATA_SOURCE_MODE=hybrid
```

**What gets fetched:**

- Subreddits: r/LocalLLaMA, r/MachineLearning, r/hardware, r/buildapc, r/artificial
- Filter keywords: AI, memory, GPU, LLM, VRAM, RAM, DRAM, NAND, SSD
- Uses public JSON endpoints

**Optional OAuth setup** (higher rate limits):

1. Create app at https://www.reddit.com/prefs/apps (type: "script")
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
2. Toggle **aiDAPTIV+ ON/OFF** to compare scenarios (conceptual today)
3. Click **START ANALYSIS**
4. Watch the Hardware Monitor for memory and model changes

## Architecture & Tech Stack

### Backend

- **Framework:** FastAPI (Python 3.9+)
- **LLM engine:** Ollama (local inference)
- **Vector DB:** ChromaDB
- **Memory monitoring:** psutil
- **WebSocket:** real-time streaming
- **Data processing:** sentence-transformers (embeddings), Pillow (images)

### Frontend

- React 19 + TypeScript
- Vite
- TailwindCSS + @tailwindcss/typography
- lucide-react
- react-markdown

### AI Models

**Current implementation (standard tier):**
- **Llama 3.1 8B** – Text analysis (dossiers, news, social, video transcripts)
- **LLaVA 13B** – Image analysis (infographics, screenshots)

Models are swapped dynamically during the workflow based on document type (text vs. images).

**Note:** The current `mktg_intelligence_demo` scenario uses the "standard" tier.

### Infrastructure

- WebSocket + REST
- Local filesystem for documents
- ChromaDB for embeddings
- Memory model: RAM → (future SSD offload) → Vector DB

### Key Features

**Two Views in the UI**

**View 1: Analyst UI**
- Live LLM output stream
- Progress counters (placeholders today)
- Document processing grid

**View 2: System UI**
- Real-time RAM and swap
- Model swap visibility
- Crash visualization when memory limits are exceeded

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
│  ┌──────────────┐  ┌──────────────┐                          │
│  │ llama3.1:8b  │  │   llava:13b  │                          │
│  │   (5GB)      │  │   (8GB)      │                          │
│  └──────────────┘  └──────────────┘                          │
└────────────────────────────────────────────────────────────────┘
                             │
┌────────────────────────────▼───────────────────────────────────┐
│                    ChromaDB (Vector DB)                       │
│  Document Embeddings (sentence-transformers)                  │
│  Semantic Search & RAG Retrieval                              │
│  Storage: backend/chroma_db/                                  │
└────────────────────────────────────────────────────────────────┘
```

## Document Loading Order

Documents are loaded in a specific order to ensure proper context:

1. **README** – Strategic context and instructions
2. **Dossiers** – Competitor intelligence profiles (excludes Samsung, Silicon Motion, and Kioxia dossiers)
3. **Live Reddit** – Real-time social signals (if enabled via `DATA_SOURCE_MODE=live`)
4. **News** – Market announcements and articles
5. **Social** – File-based social signals (fallback if live Reddit unavailable)
6. **Images** – Infographics, screenshots, competitor visuals (from all subdirectories)
7. **Video Transcripts** – Keynote and demo transcripts

**Note:** The default `mktg_intelligence_demo` scenario processes **87 documents** (1 README + 2 dossiers + 60 news + 20 social + 3 video transcripts + 3 images).

## Vector Database & RAG Workflow

The demo uses ChromaDB to support RAG.

**Memory tiers:**

1. **Active context (RAM)** – current documents (max 60K tokens)
2. **Recent context (SSD)** – future aiDAPTIV+ offload (not implemented here)
3. **Long-term memory (Vector DB)** – embeddings stored in ChromaDB

**How it works:**

**Document storage:**
- Embedding model: all-MiniLM-L6-v2 (384 dimensions)
- Stored with metadata (category, title, tokens, timestamp)

**RAG retrieval:**
- Before each analysis step, retrieve similar documents by meaning
- Exclude current batch documents
- Limit retrieved content to ~3K tokens (default parameter is 5K, but current usage limits to 3K)

**Context pruning:**
- When active context exceeds 60K tokens:
  - Move oldest documents to Vector DB
  - Active context reduced to ~54K tokens

## Memory Telemetry

### Real-Time Updates (1Hz)

```json
{
    "unified_percent": 66.8,
    "unified_gb": 13.2,
    "unified_total_gb": 16.0,
    "virtual_percent": 60.1,
    "virtual_gb": 2.4,
    "virtual_active": true,
    "context_tokens": 50000,
    "kv_cache_gb": 0.75,
    "model_weights_gb": 5.0,
    "loaded_model": "llama3.1:8b"
}
```

### KV Cache Telemetry

Multi-tier approach:

1. **Parse Ollama logs:** `~/.ollama/logs/server.log`
2. **Use Ollama API:** `/api/ps`
3. **Formula estimate:**
   ```
   (context_tokens / 1000) × 0.015 GB × model_scale_factor
   ```

## Experiment Knobs (Things to Try)

These are simple changes engineers can use to create more or less memory pressure.

### Workload Size

- Add more documents in `data/realstatic/<scenario_slug>/...`
- Use larger documents (longer text, more images, longer transcripts)
- Increase the number of documents retrieved for RAG (Top-K)
- Increase RAG token budget (more retrieved tokens)

### Model Choices

- Use a larger model (for example 14B → 32B or 70B, if available)
- Use a higher precision model (for example FP16 instead of quantized)
- Keep multiple models loaded longer (reduce unloading between steps)
- Increase context length settings (if supported by the model)

### Concurrency

- Run multiple analysis sessions at the same time (multiple browser tabs)
- Add "multiple users" by starting more backend workers (future)
- Run multiple model calls at the same time (future)

### Artificial Memory Limits (Optional)

These options help reproduce "low-memory system" behavior on a high-memory system.

- Restrict process memory (OS-level limits, if supported)
- Reduce GPU memory available to the runtime (runtime/config dependent)
- Run on a smaller system (for example 16GB RAM, small GPU)

### What to Watch in Telemetry

- RAM usage and swap growth during model load and inference
- KV cache growth as context tokens increase
- Model weight size changes during model swaps
- Time-to-first-token changes when the system is under memory pressure

## Crash Detection

```python
baseline_swap_gb = psutil.swap_memory().used / (1024**3)
current_swap_gb = psutil.swap_memory().used / (1024**3)
swap_delta = current_swap_gb - baseline_swap_gb

if not aidaptiv_enabled and swap_delta > 2.0:
    should_crash = True
```

**Why delta-based:**

- The OS may already be using swap before the demo starts
- Delta isolates swap caused by this workload

## API Endpoints

### REST

- `GET /api/health`
- `GET /api/system/info`
- `GET /api/memory/current`
- `GET /api/scenarios`
- `POST /api/scenarios/start`
- `GET /api/capabilities`
- `GET /api/ollama/status`

### WebSocket

- `ws://localhost:8000/ws/analysis`

**Query parameters:**
- `scenario` – scenario ID (any scenario slug)
- `tier` – standard
- `aidaptiv` – true or false

## Incomplete Features & Future Work

### Phase 1: Core Demo (Current State)

**Completed:**
- Real memory monitoring (psutil)
- Real local LLM generation (Ollama)
- WebSocket streaming
- Multi-model support
- RAG with ChromaDB
- Context pruning
- Crash detection (swap delta)
- KV cache telemetry with fallback estimate

**Partially complete:**
- KV cache telemetry depends on Ollama support; fallback is estimate
- Reddit integration works without OAuth; OAuth path is incomplete
- Business metrics are placeholders

### Phase 2: More Real Metrics

**High priority:**

1. **Extract real analysis metrics from LLM output**
   - Use structured output (JSON)
   - Parse topics, entities, patterns from model output instead of progress counters

2. **Exact KV cache stats**
   - vLLM could provide direct KV cache measurement
   - Possible fallback chain: vLLM → Ollama logs → Ollama API → estimate

### Phase 3: Live Data Sources

**High priority:**

3. Live news fetching (LiveDataSource.fetch_news() currently empty)
4. Reddit OAuth integration (optional, higher rate limits)
5. Twitter/X integration (requires OAuth flow)
6. RSS feed parsing as fallback
7. Caching and rate limiting modules

### Phase 4: Hardware Integration

**High priority:**

8. **Real aiDAPTIV+ hardware integration**
   - This repo currently does not offload anything to SSD using aiDAPTIV+
   - Future work: integrate SDK/driver and measure actual offload behavior

### Phase 5: Advanced Features

**Medium priority:**

9. External model providers (OpenAI, Anthropic, Google)
10. Deeper document parsing (entities, dates, relationships)
11. Session history UI (data exists, UI does not)

## Troubleshooting

### Model swap not visible

**Cause:** trigger percentage too high  
**Fix:** adjust `trigger_percent` in `ANALYSIS_PHASES`

### Memory not updating

**Cause:** backend not sending or frontend not processing events  
**Fix:** check WebSocket and verify `calculate_memory()` runs

### Slow model loading

**Cause:** system swapping heavily  
**Fix:** use smaller model or close other apps

### Crash detection not working

**Cause:** swap delta does not exceed threshold  
**Fix:** adjust threshold in `memory_monitor.py` or increase workload size

## Project Structure

```
├── backend/
│   ├── services/
│   └── api/
├── src/
│   ├── components/
│   └── ScenarioContext.tsx
├── data/
│   ├── realstatic/
│   ├── dummy/
│   └── generated/
```

## License

Proprietary – Phison Electronics Corp.
