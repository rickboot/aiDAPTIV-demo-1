# aiDaptiv+ Demo Backend

FastAPI backend for the aiDaptiv+ competitive intelligence demo. Provides WebSocket-based real-time simulation streaming with memory management and crash detection.

## Features

- **WebSocket Streaming**: Real-time event streaming for simulation progress
- **Memory Simulation**: Models unified memory (16GB) and virtual memory (aiDaptiv+ SSD offload)
- **Two Tiers**: Lite (15s, 18 docs) and Large (30s, 268 docs)
- **Crash Detection**: Simulates OOM crash at 76% for large tier without aiDaptiv+
- **Document Corpus**: 286 realistic competitive intelligence documents

## Installation

### Prerequisites

- Python 3.8+
- pip

### Setup

```bash
# Navigate to backend directory
cd backend

# Install dependencies
pip install -r requirements.txt

# Generate document corpus (if not already done)
python3 generate_documents.py
```

## Running the Backend

### Development Mode (with auto-reload)

```bash
# From backend directory
python3 main.py

# Or using uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

The backend will start on `http://localhost:8000`

## API Documentation

### REST Endpoints

#### Health Check
```
GET /api/health
Response: {"status": "ok"}
```

#### System Information
```
GET /api/system/info
Response: {
  "memory_gb": 16.0,
  "model": "MacBook Air M4",
  "platform": "darwin"
}
```

#### List Scenarios
```
GET /api/scenarios
Response: {
  "scenarios": [
    {
      "id": "pmm",
      "name": "PMM Competitive Intelligence",
      "tiers": ["lite", "large"]
    }
  ]
}
```

#### Start Simulation
```
POST /api/scenarios/start
Body: {
  "scenario": "pmm",
  "tier": "lite" | "large",
  "aidaptiv_enabled": true | false
}
Response: {
  "ws_url": "ws://localhost:8000/ws/analysis",
  "scenario": "pmm",
  "tier": "lite",
  "aidaptiv_enabled": false
}
```

### WebSocket Endpoint

#### Analysis Stream
```
WS /ws/analysis

Client sends:
{
  "scenario": "pmm",
  "tier": "lite" | "large",
  "aidaptiv_enabled": true | false
}

Server streams events:
- thought: AI reasoning updates
- memory: Memory usage statistics
- document: Document processing progress
- metric: Metric updates (visual_updates, papers_analyzed, etc.)
- complete: Simulation success
- crash: Simulation failure (OOM)
```

## WebSocket Message Format

### Thought Event
```json
{
  "type": "thought",
  "data": {
    "text": "Analyzing Competitor X homepage redesign...",
    "status": "PROCESSING" | "ACTIVE" | "ANALYZING" | "COMPLETE" | "WARNING",
    "timestamp": "2026-01-07T10:23:45Z"
  }
}
```

### Memory Event
```json
{
  "type": "memory",
  "data": {
    "unified_percent": 67.5,
    "unified_gb": 10.8,
    "unified_total_gb": 16.0,
    "virtual_percent": 0.0,
    "virtual_gb": 0.0,
    "virtual_active": false
  }
}
```

### Document Event
```json
{
  "type": "document",
  "data": {
    "name": "competitor_a.txt",
    "index": 12,
    "total": 268,
    "category": "competitor" | "paper" | "social"
  }
}
```

### Metric Event
```json
{
  "type": "metric",
  "data": {
    "name": "visual_updates" | "papers_analyzed" | "signals_detected" | "competitors_tracked",
    "value": 152
  }
}
```

### Complete Event
```json
{
  "type": "complete",
  "data": {
    "success": true,
    "scenario": "pmm",
    "tier": "large",
    "findings": {
      "shifts_detected": 3,
      "evidence": "5 UI patterns, 8 papers, 23 social signals",
      "recommendation": "Expedited roadmap review required"
    },
    "memory_stats": {
      "unified_gb": 15.2,
      "virtual_gb": 4.2,
      "total_gb": 19.4
    }
  }
}
```

### Crash Event
```json
{
  "type": "crash",
  "data": {
    "progress_percent": 76.0,
    "docs_loaded": 203,
    "docs_total": 268,
    "memory_used_gb": 15.2,
    "memory_limit_gb": 16.0,
    "reason": "Out of unified memory - aiDaptiv+ required for this workload"
  }
}
```

## Simulation Tiers

### Lite Tier
- **Duration**: 15 seconds
- **Documents**: 18 (3 competitors + 10 papers + 5 social)
- **Memory Target**: 10GB
- **Outcome**: Always succeeds (fits in 16GB unified memory)

### Large Tier
- **Duration**: 30 seconds
- **Documents**: 268 (12 competitors + 234 papers + 22 social)
- **Memory Target**: 19GB
- **Without aiDaptiv+**: Crashes at 76% progress (203/268 docs)
- **With aiDaptiv+**: Succeeds with 4.2GB virtual memory offload

## Architecture

```
backend/
├── main.py                 # FastAPI app entry point
├── api/
│   ├── websocket.py       # WebSocket endpoint
│   └── scenarios.py       # REST endpoints
├── services/
│   ├── simulation.py      # Orchestration engine
│   └── memory_monitor.py  # Memory calculations
├── models/
│   └── schemas.py         # Pydantic models
└── generate_documents.py  # Document corpus generator
```

## Development Notes

- All AI responses are canned/simulated (Phase 1)
- Memory monitoring is calculated, not real system monitoring
- Target platform: macOS (MacBook Air M4, 16GB unified memory)
- CORS enabled for `localhost:5173` (Vite dev server)
- Logging configured at INFO level

## Interactive API Docs

FastAPI provides automatic interactive documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Troubleshooting

### Port Already in Use
```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9
```

### CORS Issues
Ensure frontend is running on `localhost:5173`. If using a different port, update CORS origins in `main.py`.

### WebSocket Connection Failed
- Check backend is running: `curl http://localhost:8000/api/health`
- Verify WebSocket URL: `ws://localhost:8000/ws/analysis`
- Check browser console for connection errors

## Future Enhancements (Phase 2)

- Real LLM integration (Ollama)
- Actual system memory monitoring
- Document content analysis
- Multi-scenario support
- User authentication
- Persistent simulation history
