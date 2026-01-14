"""
Configuration settings for aiDAPTIV+ demo backend.
"""

import os
from typing import Literal
from pathlib import Path

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
THOUGHT_STREAM_DELAY = 0.0  # No delay for dev (set to 0.05 for demo readability)

# Maximum context size (tokens)
MAX_CONTEXT_TOKENS = 8000  # Leave room for response

# ═══════════════════════════════════════════════════════════════
# DATA SOURCE CONFIGURATION
# ═══════════════════════════════════════════════════════════════

# Data source mode: "generated" (deterministic, for dev) | "live" (real-time APIs) | "hybrid" (live with fallback)
DATA_SOURCE_MODE = os.getenv("DATA_SOURCE_MODE", "generated").lower()

# Generated data settings
GENERATED_NEWS_COUNT = int(os.getenv("GENERATED_NEWS_COUNT", "50"))  # Number of news articles to generate
GENERATED_SOCIAL_COUNT = int(os.getenv("GENERATED_SOCIAL_COUNT", "20"))  # Number of social signals to generate

# ═══════════════════════════════════════════════════════════════
# LIVE DATA SOURCE CONFIGURATION
# ═══════════════════════════════════════════════════════════════

# NewsAPI (https://newsapi.org/)
NEWS_API_KEY = os.getenv("NEWS_API_KEY", "")
NEWS_API_ENABLED = bool(NEWS_API_KEY)

# Twitter/X API v2 (https://developer.twitter.com/)
TWITTER_BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN", "")
TWITTER_API_ENABLED = bool(TWITTER_BEARER_TOKEN)

# Reddit API (https://www.reddit.com/dev/api/)
REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID", "")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET", "")
REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT", "aiDAPTIV-Demo/1.0")
REDDIT_API_ENABLED = bool(REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET)

# RSS Feeds (no auth needed)
RSS_FEEDS_ENABLED = os.getenv("RSS_FEEDS_ENABLED", "true").lower() == "true"
RSS_FEED_URLS = [
    "https://techcrunch.com/feed/",
    "https://feeds.arstechnica.com/arstechnica/index",
    "https://www.theverge.com/rss/index.xml",
    "https://hnrss.org/frontpage",  # Hacker News RSS
]

# Caching
LIVE_DATA_CACHE_TTL = int(os.getenv("LIVE_DATA_CACHE_TTL", "3600"))  # 1 hour default
LIVE_DATA_CACHE_DIR = Path(__file__).parent.parent / "data" / "cache"

# Rate limiting
LIVE_DATA_RATE_LIMIT_ENABLED = os.getenv("LIVE_DATA_RATE_LIMIT_ENABLED", "true").lower() == "true"

# ═══════════════════════════════════════════════════════════════
# LOGGING
# ═══════════════════════════════════════════════════════════════

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
