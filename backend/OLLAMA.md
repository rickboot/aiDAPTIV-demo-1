# Ollama Integration Guide

## Overview

The backend now supports **real LLM reasoning** via Ollama integration. This replaces canned responses with authentic AI analysis of the document corpus.

## Quick Start

### 1. Install Ollama

```bash
# macOS
brew install ollama

# Or download from https://ollama.ai
```

### 2. Start Ollama Server

```bash
ollama serve
```

### 3. Pull Model

```bash
# Recommended: balanced performance
ollama pull llama3.1:8b

# Alternatives:
# ollama pull llama3.2:3b  # Lighter, faster
# ollama pull llama3:70b   # Best quality, requires more memory
```

### 4. Enable Ollama in Backend

```bash
cd backend

# Enable Ollama mode
export USE_REAL_OLLAMA=true

# Start backend
python3 main.py
```

## Configuration

### Environment Variables

```bash
# Toggle Ollama (default: false)
export USE_REAL_OLLAMA=true

# Ollama host (default: http://localhost:11434)
export OLLAMA_HOST=http://localhost:11434

# Model to use (default: llama3.1:8b)
export OLLAMA_MODEL=llama3.1:8b
```

### Fallback Behavior

The backend automatically falls back to canned responses if:
- `USE_REAL_OLLAMA=false` (default)
- Ollama is not running
- Model is not pulled
- Document loading fails
- LLM streaming errors occur

## How It Works

### Document Loading

At simulation start, the backend:
1. Loads all `.txt` files from `/documents/pmm/{tier}/`
2. Combines into structured context with section markers
3. Estimates token count (~8000 token limit)

**Lite Tier**: 18 documents (3 competitors + 10 papers + 5 social)  
**Large Tier**: 268 documents (12 competitors + 234 papers + 22 social)

### Agentic Analysis Phases

The LLM performs 5-phase progressive analysis:

**Phase 1 (5%)**: Document Review  
- Summarizes available data sources

**Phase 2 (25%)**: Pattern Detection  
- Analyzes competitor UI changes and architecture shifts

**Phase 3 (50%)**: Technical Cross-Reference  
- Cross-references findings with research papers

**Phase 4 (70%)**: Social Signal Validation  
- Validates with CTO posts and social media

**Phase 5 (90%)**: Synthesis & Recommendations  
- Synthesizes findings and provides strategic recommendations

### Streaming Thoughts

- LLM responses stream in real-time to frontend
- Throttled to 50ms per chunk for readability
- Each phase generates multiple thought events
- Thoughts reference actual competitors/papers from documents

## Comparison: Canned vs. Real LLM

| Feature | Canned (Default) | Real LLM (Ollama) |
|---------|------------------|-------------------|
| Speed | Instant | 2-5 minutes |
| Thoughts | Pre-scripted templates | Authentic AI reasoning |
| References | Generic | Specific competitors/papers |
| Findings | Static | Based on actual analysis |
| Variability | Same every time | Different each run |
| Requirements | None | Ollama + model |

## Testing

### Verify Ollama Connection

```bash
# Check Ollama is running
curl http://localhost:11434/api/tags

# Should return list of models
```

### Test with Backend

```bash
# Enable Ollama and start backend
USE_REAL_OLLAMA=true python3 main.py

# Look for logs:
# INFO - Ollama enabled with model: llama3.1:8b
# INFO - Loaded context: 45231 chars, ~11307 tokens
```

### Run Simulation

1. Start frontend: `npm run dev`
2. Click "START ANALYSIS"
3. Watch backend logs for:
   - `INFO - Generating LLM thought for phase: phase_1_review`
   - Streaming thought chunks
4. Frontend displays real AI reasoning

## Troubleshooting

### "Ollama not running"

```bash
# Start Ollama server
ollama serve
```

### "Model not found"

```bash
# Pull the model
ollama pull llama3.1:8b
```

### "Context too large"

- Backend automatically truncates to 8000 tokens
- Consider using lite tier for testing
- Or use smaller model (llama3.2:3b)

### Slow Performance

- Large tier with 268 documents takes 2-5 minutes
- Use lite tier (18 documents) for faster demos
- Consider using smaller model for speed

## Development Tips

### Quick Toggle

```bash
# Disable Ollama (use canned responses)
unset USE_REAL_OLLAMA
python3 main.py

# Enable Ollama (use real LLM)
USE_REAL_OLLAMA=true python3 main.py
```

### Test Different Models

```bash
# Fast but less accurate
OLLAMA_MODEL=llama3.2:3b USE_REAL_OLLAMA=true python3 main.py

# Best quality (requires significant memory)
OLLAMA_MODEL=llama3:70b USE_REAL_OLLAMA=true python3 main.py
```

### Monitor LLM Output

Backend logs show:
- Phase being processed
- Thought chunks being streamed
- Errors and fallbacks

## Architecture

```
Simulation Start
    ↓
Load Documents (18 or 268 .txt files)
    ↓
Build Context String (~8000 tokens)
    ↓
For each phase (5 total):
    ↓
    Generate LLM Reasoning
    ↓
    Stream Thoughts to Frontend
    ↓
    Throttle for Readability
    ↓
Complete Analysis
```

## Next Steps

- **Phase 3**: Real memory monitoring (track actual LLM memory usage)
- **Phase 4**: Multi-model support (GPT-4, Claude, Gemini)
- **Phase 5**: Document content analysis (not just metadata)
