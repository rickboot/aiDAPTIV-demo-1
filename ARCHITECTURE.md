# aiDAPTIV+ Demo - Architecture & How It Works

## Business Purpose

**Primary Goal:** Demonstrate that Phison aiDAPTIV+ SSDs enable AI workloads that exceed available RAM, preventing OOM crashes and eliminating the need for expensive cloud GPU instances.

**Target Audience:**
- IT Directors and System Architects evaluating AI infrastructure
- Hardware buyers comparing local vs. cloud AI deployment costs
- Business stakeholders assessing ROI of AI-capable workstations

**Value Proposition:**
- **Without aiDAPTIV+:** Memory-intensive AI workloads crash (OOM) on standard 16GB systems
- **With aiDAPTIV+:** Seamless memory offload to SSD enables workloads to complete successfully

---

## Overview

This demo simulates a **high-fidelity competitive intelligence analysis** for CES 2026 to showcase aiDAPTIV+'s value in managing memory during AI workloads on memory-constrained systems.

The simulation processes real market intelligence (text documents, images, videos) through a strategic AI agent (@Virtual_PMM) powered by **Semantic Grounding Profiles (SGP)** that analyzes competitor moves, breaking news, and visual materials to construct the "Memory Wall" narrative—validating Phison's market opportunity.

**Key Features:**
- Multi-modal analysis (text, images via LLaVA vision model)
- Real-time LLM streaming with accurate token counting
- Batch-based context management for focused analysis
- SGP-driven strategic reasoning for consistent insights

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
│                   ┌────────▼────────┐                         │
│                   │  Orchestrator   │                         │
│                   └────────┬────────┘                         │
│                            │                                  │
│                   ┌────────▼────────┐                         │
│                   │ OllamaService   │                         │
│                   └────────┬────────┘                         │
└────────────────────────────┼───────────────────────────────────┘
                             │ HTTP API
┌────────────────────────────▼───────────────────────────────────┐
│                      Ollama Server                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│  │ llama3.1:8b  │  │qwen2.5:14b   │  │   llava      │        │
│  │   (5GB)      │  │   (9GB)      │  │   (5GB)      │        │
│  └──────────────┘  └──────────────┘  └──────────────┘        │
│                                                                │
│  Models stored: ~/.ollama/models/blobs/                       │
└────────────────────────────────────────────────────────────────┘
```

---

## Data Flow

### 1. Simulation Start

```
User clicks "Start Analysis"
    ↓
Frontend → POST /api/scenarios/start
    ↓
Backend returns WebSocket URL
    ↓
Frontend connects to ws://localhost:8000/ws/analysis
    ↓
Backend creates Orchestrator instance
    ↓
Orchestrator.run_simulation() starts
```

### 2. Event Streaming

The orchestrator yields different event types over WebSocket:

```python
# Event Types
DocumentEvent    # New document being processed
MemoryEvent      # Real-time memory telemetry (5Hz)
ThoughtEvent     # LLM-generated analysis
PerformanceEvent # Model performance metrics
StatusEvent      # System status (e.g., "Loading Model...")
MetricEvent      # Business metrics updates
CrashEvent       # Crash scenario (if aiDAPTIV+ disabled)
```

### 3. Model Swapping Flow

```
Phase 1 (5%): llama3.1:8b loaded
    ↓
Phase 2 (15%): Trigger model swap
    ↓
    1. StatusEvent("Offloading Model: llama3.1:8b...")
    2. _wait_with_telemetry(2.0s) → MemoryEvents
    3. StatusEvent("Loading Model: qwen2.5:14b...")
    4. Start background_telemetry() task
    5. Call ollama_service.generate_reasoning()
       ↓ (Ollama loads 14B model - takes 5-15s)
       ↓ (background_telemetry sends MemoryEvents every 200ms)
       ↓ (Memory climbs from ~13GB → ~20GB)
    6. First response arrives → stop background_telemetry
    7. Continue streaming thought events
    ↓
Phase 3 (50%): qwen2.5:14b stays loaded
    ↓
Phase 4 (70%): Swap back to llama3.1:8b
    ↓ (Memory drops from ~20GB → ~13GB)
```

---

## Key Components

### Backend

#### **Orchestrator** (`backend/services/orchestrator.py`)
- Main simulation engine
- Manages event streaming
- Coordinates model swapping
- Implements background telemetry during model loads

**Key Methods:**
- `run_simulation()` - Main event loop
- `_generate_llm_thought()` - Handles LLM generation and model swapping
- `_wait_with_telemetry()` - Yields memory events during pauses
- `background_telemetry()` - Polls memory during model loading

#### **MemoryMonitor** (`backend/services/memory_monitor.py`)
- Uses `psutil` to get real system memory
- Tracks baseline swap usage
- Detects crash conditions (swap delta > 2GB)

**Key Method:**
- `calculate_memory()` - Returns current RAM/swap usage

#### **OllamaService** (`backend/services/ollama_service.py`)
- Interfaces with Ollama API
- Manages document context building
- Streams LLM responses with accurate token counting
- Handles vision models (LLaVA) for image analysis

**Key Methods:**
- `generate_step()` - Streams LLM analysis for a specific document batch
  - Accumulates all chunks to build complete response
  - Tracks Time To First Token (TTFT) on first chunk
  - Extracts real token counts from Ollama's final chunk
  - Yields single result with accurate performance metrics
- `build_context()` - Builds context from document list

#### **WebSocket Handler** (`backend/api/websocket.py`)
- Manages WebSocket connections
- Streams events from orchestrator to frontend
- Handles connection lifecycle

### Frontend

#### **ScenarioContext** (`src/ScenarioContext.tsx`)
- Global state management
- WebSocket connection handling
- Event processing and state updates
- Fetches baseline memory on mount

**Key State:**
- `systemState` - Memory usage, model name, total RAM
- `feed` - Activity feed items
- `metrics` - Business metrics

#### **HardwareMonitor** (`src/components/HardwareMonitor.tsx`)
- Real-time memory visualization
- Shows RAM and swap usage
- Displays model swapping status
- Updates at 5Hz during simulation

#### **Dashboard** (`src/components/Dashboard.tsx`)
- Main UI container
- Activity feed
- Metrics cards
- Scenario selection

---

## Analysis Flow

The demo processes documents in **category-based batches** with SGP-driven analysis:

### Document Processing Order
1. **Images** (multi-modal demo priority)
   - Model: `llava:13b` (vision model)
   - Agent: @Visual_Intel
   - Analysis: Competitive positioning from infographics

2. **Dossiers** (strategic context)
   - Model: `llama3.1:8b`
   - Agent: @Virtual_PMM
   - Analysis: Competitor weaknesses and attack vectors

3. **News** (market validation)
   - Model: `llama3.1:8b`
   - Agent: @Virtual_PMM
   - Analysis: Validation signals for memory bottleneck thesis

4. **Social** (developer pain points)
   - Model: `llama3.1:8b`
   - Agent: @Virtual_PMM
   - Analysis: Voice of customer, OOM complaints

### Context Management
- **Batch-based context**: LLM analyzes only current batch documents (not all accumulated)
- **Prevents context pollution**: Each document gets focused analysis
- **Example**: When analyzing Intel image, context contains only Intel image (not README + dossiers)

### Semantic Grounding Profiles (SGP)

Every document analysis is grounded by the SGP (`backend/sgp_config/virtual_pmm.json`), which provides:

- **Product Identity**: aiDAPTIV+ positioning and value proposition
- **Problem Context**: Memory constraints in AI workloads
- **Solution Approach**: KV-cache offloading to SSD
- **Competitive Landscape**: Samsung, Kioxia threat levels
- **Analytical Frameworks**: How to analyze data (e.g., "follow the money", "second-order effects")
- **Evidence Tiers**: How to weight sources (Tier 1: specs, Tier 2: analyst reports, Tier 3: social signals)
- **Guardrails**: Forbidden claims (never claim performance without data)

**SGP is applied to EVERY data source analysis**, ensuring consistent, grounded reasoning across all categories.

---

## Memory Telemetry

### Real-Time Updates (5Hz)

```python
# Every 200ms during simulation
memory_data, should_crash = memory_monitor.calculate_memory()

# Returns:
{
    "unified_percent": 66.8,      # RAM usage %
    "unified_gb": 13.2,            # RAM usage GB
    "unified_total_gb": 16.0,      # Total RAM
    "virtual_percent": 60.1,       # Swap usage %
    "virtual_gb": 2.4,             # Swap usage GB
    "virtual_active": true         # Swap > 100MB
}
```

### Background Telemetry During Model Load

When a model swap occurs:

```python
# Start background task
async def background_telemetry():
    while not stop_event.is_set():
        memory_data = calculate_memory()
        queue.put(memory_data)
        await asyncio.sleep(0.2)  # 5Hz

# Ollama loads model (blocks for 5-15s)
async for response in ollama.generate():
    # Drain telemetry queue
    while not queue.empty():
        yield queue.get()  # Send buffered memory updates
    
    # Stop telemetry after first response
    stop_event.set()
```

This ensures **continuous memory updates** even while Ollama is loading the model.

---

## Crash Detection

### Logic

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

### Why Delta-Based?

- User's Mac may already have 2-3GB swap in use
- Absolute threshold would false-trigger
- Delta shows swap **caused by the simulation**

---

## Configuration

### Scenarios (`backend/services/orchestrator.py`)

```python
SCENARIOS = {
    "ces2026": ScenarioConfig(
        scenario="ces2026",
        tier="standard",
        duration_seconds=180,       # 3 minute demo
        total_documents=21,         # CES intelligence feed
        memory_target_gb=24.0,      # Exceeds 16GB RAM for impact
        crash_threshold_percent=85.0
    )
}
```

### Models

- **llama3.1:8b** - Fast, general purpose (5GB)
- **qwen2.5:14b** - Larger, better quality (9GB)
- **llava** - Vision model (5GB) - not currently used

---

## API Endpoints

### REST

- `GET /api/health` - Health check
- `GET /api/system/info` - Get system memory/CPU info
- `GET /api/memory/current` - Get current memory usage (baseline)
- `GET /api/scenarios` - List available scenarios
- `POST /api/scenarios/start` - Start simulation (returns WebSocket URL)

### WebSocket

- `ws://localhost:8000/ws/analysis` - Event stream

**Query Parameters:**
- `scenario` - Scenario ID (e.g., "pmm")
- `tier` - Tier (e.g., "lite" or "large")
- `aidaptiv` - Enable aiDAPTIV+ (true/false)

---

## Development

### Running Locally

```bash
# Terminal 1: Ollama
ollama serve

# Terminal 2: Backend
cd backend
python3 main.py

# Terminal 3: Frontend
npm run dev
```

### Key Files

**Backend:**
- `backend/services/orchestrator.py` - Main simulation engine
- `backend/services/memory_monitor.py` - Memory telemetry
- `backend/services/ollama_service.py` - LLM integration
- `backend/api/websocket.py` - WebSocket handler
- `backend/models/schemas.py` - Pydantic models

**Frontend:**
- `src/ScenarioContext.tsx` - State management
- `src/components/HardwareMonitor.tsx` - Memory visualization
- `src/components/WarRoomDisplay.tsx` - Main UI
- `src/components/ImpactMetrics.tsx` - Results dashboard

---

## Performance Characteristics

### Memory Usage

| State | RAM Usage | Notes |
|-------|-----------|-------|
| Idle | ~13GB | System baseline |
| llama3.1:8b loaded | ~13-14GB | Small increase |
| qwen2.5:14b loaded | ~18-20GB | Significant increase |
| Model swap | Spike/drop | Visible in telemetry |

### Timing

| Operation | Duration | Notes |
|-----------|----------|-------|
| llama3.1:8b load | 1-2s | Fast |
| qwen2.5:14b load | 5-15s | Slower, visible in demo |
| Model swap | 7-17s | Offload + load |
| CES 2026 | 180s | 21 high-fidelity documents |

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
