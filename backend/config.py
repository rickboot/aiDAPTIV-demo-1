"""
Configuration settings for aiDAPTIV+ demo backend.
"""

import os
from typing import Literal

# ═══════════════════════════════════════════════════════════════
# OLLAMA CONFIGURATION
# ═══════════════════════════════════════════════════════════════

# Toggle between real Ollama LLM and canned responses
# Default: true (use real Ollama)
# Set USE_REAL_OLLAMA=false to use canned responses
USE_REAL_OLLAMA = os.getenv("USE_REAL_OLLAMA", "true").lower() == "true"

# Ollama connection settings
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1:8b")

# Alternative models (for different memory constraints)
# - llama3.2:3b (lighter, faster, less accurate)
# - llama3.1:8b (balanced, recommended)
# - llama3:70b (best quality, requires significant memory)

# ═══════════════════════════════════════════════════════════════
# SIMULATION SETTINGS
# ═══════════════════════════════════════════════════════════════

# Streaming throttle (seconds between thought chunks)
THOUGHT_STREAM_DELAY = 0.05  # 50ms for readable streaming

# Maximum context size (tokens)
MAX_CONTEXT_TOKENS = 8000  # Leave room for response

# ═══════════════════════════════════════════════════════════════
# LOGGING
# ═══════════════════════════════════════════════════════════════

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
