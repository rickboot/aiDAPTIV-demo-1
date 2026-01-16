# Development Mode - Lightweight Models

For development on resource-constrained systems (like MacBook Air M4 16GB), use **DEV_MODE** to enable lighter models that maintain functionality while reducing memory usage and improving performance.

## Quick Start

Enable dev mode by setting the environment variable:

```bash
export DEV_MODE=true
```

Or when running the backend:

```bash
DEV_MODE=true python3 backend/main.py
```

## Model Comparison

### Production Models (Default)
| Use Case | Model | Size | Memory |
|----------|-------|------|--------|
| Text Analysis | `llama3.1:8b` | 4.9 GB | 5.0 GB |
| Image/Video Analysis | `llava:13b` | 8.0 GB | 8.0 GB |
| Cross-Modal Synthesis | `qwen2.5:14b` | 9.0 GB | 9.0 GB |
| Audio Transcription | Whisper `base` | ~150 MB | ~150 MB |
| **Total (worst case)** | | | **~22 GB** |

### Dev Mode Models (Lighter)
| Use Case | Model | Size | Memory | Savings |
|----------|-------|------|--------|---------|
| Text Analysis | `llama3.2:3b` | 2.0 GB | 2.0 GB | **-3.0 GB** |
| Image/Video Analysis | `llava:latest` | 4.7 GB | 4.7 GB | **-3.3 GB** |
| Cross-Modal Synthesis | `phi3:mini` | 1.7 GB | 1.7 GB | **-7.3 GB** |
| Audio Transcription | Whisper `tiny` | ~75 MB | ~75 MB | **-75 MB** |
| **Total (worst case)** | | | **~8.5 GB** | **-13.5 GB** |

## Memory Impact

On a 16GB MacBook Air M4:
- **Production**: Models can use 22GB+ (with KV cache), causing swap usage and slowdowns
- **Dev Mode**: Models use ~14.5GB, leaving more headroom for system and other apps

## Required Models

Make sure you have the dev models pulled:

```bash
# Download lightweight dev models
ollama pull llama3.2:3b      # Text (2.0 GB - much lighter!)
ollama pull llava:latest     # Vision (4.7 GB)
ollama pull phi3:mini        # Cross-modal (1.7 GB - very light!)
```

These models have been automatically downloaded for you.

## What Changes in Dev Mode?

1. **Text Models**: `llama3.1:8b` → `llama3.2:3b` (2.0 GB instead of 4.9 GB) - **60% reduction!**
2. **Vision Models**: `llava:13b` → `llava:latest` (4.7 GB instead of 8.0 GB)
3. **Cross-Modal**: `qwen2.5:14b` → `phi3:mini` (1.7 GB instead of 9.0 GB) - **81% reduction!**
4. **Whisper**: `base` → `tiny` (75 MB instead of 150 MB)

## Quality Trade-offs

- **Text**: `llama3.2:3b` is faster and lighter, slightly less nuanced than `llama3.1:8b` but excellent for dev iteration
- **Vision**: `llava:latest` is slightly less accurate than `llava:13b` but still very capable
- **Cross-Modal**: `phi3:mini` is much smaller but maintains good reasoning for synthesis tasks - Microsoft's efficient model
- **Whisper**: `tiny` is faster and lighter, accuracy is slightly lower but acceptable for dev

## When to Use Dev Mode

✅ **Use Dev Mode When:**
- Developing on resource-constrained systems (16GB RAM or less)
- Iterating quickly and need faster model loading/swapping
- Testing functionality without needing production-quality outputs
- Running multiple services simultaneously

❌ **Don't Use Dev Mode When:**
- Preparing for demos (use production models)
- Need highest quality analysis outputs
- Have plenty of system resources (32GB+ RAM)
- Running final validation tests

## Switching Back to Production

Simply unset the environment variable:

```bash
unset DEV_MODE
# or
export DEV_MODE=false
```

The system will automatically use production models on next restart.

## Verification

Check which models are being used by looking at the logs:

```
INFO: Using DEV_MODE: lighter models for faster development
INFO: Model Changed: llama3.1:8b -> llava:latest
```

Or check the status events in the UI - they'll show the actual model names being swapped.
