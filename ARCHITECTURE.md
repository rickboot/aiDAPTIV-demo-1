# aiDAPTIV+ Demo - Architecture & How It Works

## Overview

This demo simulates a **multi-agent competitive intelligence analysis** to showcase aiDAPTIV+'s value in managing memory during model swapping on memory-constrained systems.

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         Frontend (React)                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ WarRoomDisplay│  │HardwareMonitor│  │ ImpactMetrics│      │
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
- Manages document context
- Streams LLM responses
- Defines analysis phases

**Key Method:**
- `generate_reasoning()` - Async generator that streams LLM responses

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
- `impactSummary` - Final results

#### **HardwareMonitor** (`src/components/HardwareMonitor.tsx`)
- Real-time memory visualization
- Shows RAM and swap usage
- Displays model swapping status
- Updates at 5Hz during simulation

#### **WarRoomDisplay** (`src/components/WarRoomDisplay.tsx`)
- Main UI container
- Activity feed
- Metrics cards
- Scenario selection

---

## Analysis Phases

The demo simulates a **5-phase multi-agent analysis**:

| Phase | Trigger | Agent | Model | Task |
|-------|---------|-------|-------|------|
| 1. Document Review | 5% | @Orchestrator | llama3.1:8b | Survey data sources |
| 2. Pattern Detection | 15% | @AI_Analyst | qwen2.5:14b | Find UI patterns |
| 3. Technical Cross-Ref | 50% | @Tech_Specialist | qwen2.5:14b | Match with research |
| 4. Social Validation | 70% | @Market_Researcher | llama3.1:8b | Check social signals |
| 5. Synthesis | 90% | @Lead_Strategist | llama3.1:8b | Executive summary |

**Model Swaps:**
- Phase 1→2: 8b → 14b (memory +5-7GB)
- Phase 3→4: 14b → 8b (memory -5-7GB)

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
    "pmm_lite": ScenarioConfig(
        scenario="pmm",
        tier="lite",
        duration_seconds=60,        # 1 minute demo
        total_documents=18,         # Fewer documents
        memory_target_gb=10.0,      # Fits in RAM
        crash_threshold_percent=None  # No crash
    ),
    "pmm_large": ScenarioConfig(
        scenario="pmm",
        tier="large",
        duration_seconds=120,       # 2 minute demo
        total_documents=268,        # Full dataset
        memory_target_gb=19.0,      # Exceeds 16GB RAM
        crash_threshold_percent=76.0  # Crashes at 76%
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
| Lite scenario | 60s | 18 documents |
| Large scenario | 120s | 268 documents |

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
