# aiDAPTIV+ Demo - CES 2026 Intelligence Platform

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

Simulates a **high-fidelity competitive intelligence analysis** for CES 2026, processing real market signals through a strategic AI agent (@Virtual_PMM) that:

1. Analyzes competitor dossiers (Samsung, Kioxia)
2. Synthesizes breaking news (NVIDIA Rubin, Intel Panther Lake)
3. Cross-references social developer signals
4. Constructs the "Memory Wall" narrative validating Phison's market opportunity

The demo uses **real system telemetry** and **real LLM generation** to show measurable memory offload to SSD.

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
# 1. Install Ollama models
ollama pull llama3.1:8b

# 2. Install dependencies
npm install
cd backend && pip install -r requirements.txt

# 3. Start services (3 terminals)
# Terminal 1: Ollama
ollama serve

# Terminal 2: Backend
cd backend && python3 main.py

# Terminal 3: Frontend
npm run dev
```

### Running the Demo

1. Open http://localhost:5173
2. Toggle **aiDAPTIV+ ON/OFF** to compare scenarios
3. Click **START ANALYSIS**
4. Watch the Hardware Monitor sidebar to see memory offload in action

---

## Key Features

### "The Two Worlds" UI Design

**Userland (Business Analyst View)**
- Live AI reasoning chain showing strategic synthesis
- Business metrics (Key Topics, Patterns, Insights, Critical Flags)
- Document processing grid

**Customer Land (IT Buyer View)**
- Real-time memory telemetry (RAM, Swap, SSD offload)
- Model swapping visualization
- Crash scenario when aiDAPTIV+ is disabled

### Technical Highlights

- **Real Memory Monitoring:** Uses `psutil` for actual system metrics
- **Real LLM Generation:** Ollama generates strategic insights in real-time
- **Dynamic Context Injection:** Agent loads Phison strategy from disk at runtime
- **Granular Analysis:** Processes signals every 4 documents to prevent "signal loss"

---

## Documentation

- **[ARCHITECTURE.md](./ARCHITECTURE.md)** - Technical deep-dive: system design, data flow, components
- **[DEMO_ARCHITECTURE.md](./DEMO_ARCHITECTURE.md)** - Design philosophy: "The Two Worlds" concept
- **[artifacts/architecture_update_virtual_pmm.md](./artifacts/)** - AI persona design: Hybrid Context Architecture

---

## Project Structure

```
├── backend/              # FastAPI server
│   ├── services/         # Orchestrator, Memory Monitor, Ollama integration
│   └── api/              # WebSocket + REST endpoints
├── src/                  # React frontend
│   ├── components/       # WarRoomDisplay, HardwareMonitor
│   └── ScenarioContext.tsx  # State management
├── documents/ces2026/    # High-fidelity intelligence sources
│   ├── dossier/          # Competitor profiles
│   ├── news/             # Market announcements
│   └── social/           # Developer signals
```

---

## License

Proprietary - Phison Electronics Corp.
