# Model Concurrency Analysis

Understanding which models can be loaded simultaneously and their memory impact.

## Model Loading Architecture

### Ollama Models (LLM Inference)
**Ollama loads ONE model at a time by default.**

When you request a different model:
1. Ollama unloads the previous model from VRAM/RAM
2. Loads the new model
3. The swap happens during the "Swapping Model" status event

**Exception:** Ollama supports `keep_alive` parameter to keep models in memory, but our code doesn't use this - we swap models sequentially.

### Whisper (Audio Transcription)
**Whisper is a separate Python library** (not Ollama), so it:
- Can be loaded while an Ollama model is also in memory
- Stays loaded once initialized (lazy loading on first video)
- Uses Python/PyTorch memory space (separate from Ollama)

## Concurrent Model Scenarios

### Scenario 1: Normal Text/Image Processing
**Concurrent Models: 1**
- **Ollama Model**: One at a time (e.g., `llama3.2:3b` OR `llava:latest`)
- **Whisper**: Not loaded (no video processing)
- **Total Memory**: ~2.0 GB (dev) or ~5.0 GB (prod) for text, ~4.7 GB (dev) or ~8.0 GB (prod) for vision

### Scenario 2: Video Processing (During Processing)
**Concurrent Models: 2**
- **Ollama Model**: One loaded (e.g., `llama3.2:3b` for transcript analysis)
- **Whisper**: Loaded in Python memory (~75 MB for tiny, ~150 MB for base)
- **Total Memory**: Model size + Whisper size
  - Dev: ~2.0 GB + 0.075 GB = **~2.1 GB**
  - Prod: ~5.0 GB + 0.15 GB = **~5.2 GB**

### Scenario 3: Video Processing (Frame Analysis)
**Concurrent Models: 2**
- **Ollama Model**: `llava:latest` (4.7 GB dev) or `llava:13b` (8.0 GB prod)
- **Whisper**: Still in memory from previous step (~75-150 MB)
- **Total Memory**: 
  - Dev: ~4.7 GB + 0.075 GB = **~4.8 GB**
  - Prod: ~8.0 GB + 0.15 GB = **~8.2 GB**

### Scenario 4: Model Swap Transition
**Concurrent Models: Potentially 2 (briefly)**
- During model swap, Ollama may briefly have both models in memory
- This is transient (seconds) during the swap
- Not a sustained concurrent state

## Maximum Concurrent Memory Usage

### Production Mode
**Worst Case:**
- `llava:13b` (8.0 GB) + Whisper base (0.15 GB) + KV cache (~1-2 GB) = **~10-11 GB**
- Plus system overhead, context tokens, etc.

### Dev Mode  
**Worst Case:**
- `llava:latest` (4.7 GB) + Whisper tiny (0.075 GB) + KV cache (~0.5-1 GB) = **~5.5-6 GB**
- Much more manageable on 16GB systems!

## Model Swap Behavior

Models are swapped **sequentially**, not concurrently:

1. **Text document** → `llama3.2:3b` (dev) or `llama3.1:8b` (prod)
2. **Image document** → Swap to `llava:latest` (dev) or `llava:13b` (prod)
3. **Back to text** → Swap back to text model
4. **Video processing** → Whisper loads (stays), then text model for transcript, then vision model for frames

**Swap overhead:** ~1.5 seconds per swap (configurable delay)

## Memory Optimization

The system is designed to:
- ✅ Load only one Ollama model at a time
- ✅ Keep Whisper loaded once initialized (small footprint)
- ✅ Clear KV cache between major phases
- ✅ Swap models efficiently

**This means:**
- You don't need to sum all model sizes
- Peak memory = largest single model + Whisper + KV cache + context
- Dev mode: ~6 GB peak
- Prod mode: ~11 GB peak

## Recommendations for 16GB MacBook Air M4

**Use DEV_MODE** to keep peak concurrent memory under 6 GB:
- Leaves ~10 GB for system, browser, IDE, etc.
- Prevents swap usage
- Smooth development experience
