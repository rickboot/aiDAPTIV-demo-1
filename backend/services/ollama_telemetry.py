"""
Ollama telemetry service - fetches real KV cache and memory stats from Ollama.
"""

import logging
import requests
from typing import Optional, Dict
from pathlib import Path

logger = logging.getLogger(__name__)

try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False


class OllamaTelemetry:
    """Fetch real telemetry from Ollama API and logs."""
    
    def __init__(self, host: str = "http://localhost:11434"):
        self.host = host
        self.log_path = Path.home() / ".ollama" / "logs" / "server.log"
    
    def get_running_processes(self) -> list[Dict]:
        """Get list of running Ollama processes via /api/ps."""
        try:
            response = requests.get(f"{self.host}/api/ps", timeout=2)
            if response.status_code == 200:
                data = response.json()
                return data.get("models", [])
        except Exception as e:
            logger.debug(f"Could not fetch Ollama processes: {e}")
        return []
    
    def get_kv_cache_from_logs(self) -> Optional[Dict]:
        """
        Parse Ollama server logs to extract KV cache information.
        
        Looks for lines like:
        llama_kv_cache_init: kv_size = 8192, ... CUDA0 KV buffer size = 224.00 MiB
        """
        if not self.log_path.exists():
            return None
        
        try:
            # Read last 500 lines of log
            with open(self.log_path, 'r') as f:
                lines = f.readlines()
                # Search backwards for KV cache init
                for line in reversed(lines[-500:]):
                    if "kv_cache_init" in line or "KV buffer size" in line:
                        # Try to extract KV cache size
                        # Format: "CUDA0 KV buffer size = 224.00 MiB"
                        import re
                        kv_match = re.search(r'KV buffer size\s*=\s*([\d.]+)\s*(MiB|GiB)', line)
                        if kv_match:
                            size = float(kv_match.group(1))
                            unit = kv_match.group(2)
                            # Convert to GB
                            if unit == "MiB":
                                size_gb = size / 1024
                            else:
                                size_gb = size
                            
                            # Also try to get context length
                            ctx_match = re.search(r'kv_size\s*=\s*(\d+)', line)
                            context_length = int(ctx_match.group(1)) if ctx_match else None
                            
                            return {
                                "kv_cache_gb": round(size_gb, 2),
                                "context_length": context_length,
                                "source": "ollama_logs"
                            }
        except Exception as e:
            logger.debug(f"Could not parse Ollama logs: {e}")
        
        return None
    
    def estimate_kv_cache_from_context(self, context_tokens: int, model_size_gb: float = 5.0) -> float:
        """
        Estimate KV cache from context tokens (fallback if logs unavailable).
        
        Formula based on typical KV cache growth:
        - ~15MB per 1000 tokens for 8B model
        - Scales with model size
        """
        base_per_1k_tokens = 0.015  # 15MB per 1000 tokens
        scale_factor = model_size_gb / 5.0
        kv_cache_gb = (context_tokens / 1000) * base_per_1k_tokens * scale_factor
        return round(kv_cache_gb, 2)
    
    def get_kv_cache_info(self, context_tokens: int, model_size_gb: float = 5.0) -> Dict:
        """
        Get KV cache information, trying real telemetry first, then estimate.
        
        Returns:
            Dict with kv_cache_gb, source, and context_length if available
        """
        # Try to get from Ollama logs (most accurate)
        log_info = self.get_kv_cache_from_logs()
        if log_info:
            logger.info(f"KV Cache from Ollama logs: {log_info['kv_cache_gb']}GB")
            return log_info
        
        # Try to get from running processes
        processes = self.get_running_processes()
        if processes:
            # Use context_length from process if available
            for proc in processes:
                if proc.get('context_length'):
                    # Estimate based on actual context length
                    estimated = self.estimate_kv_cache_from_context(
                        context_tokens, 
                        model_size_gb
                    )
                    return {
                        "kv_cache_gb": estimated,
                        "context_length": proc.get('context_length'),
                        "source": "ollama_api_estimate"
                    }
        
        # Fallback to estimation
        estimated = self.estimate_kv_cache_from_context(context_tokens, model_size_gb)
        return {
            "kv_cache_gb": estimated,
            "context_length": None,
            "source": "formula_estimate"
        }


def get_ollama_telemetry() -> Optional[OllamaTelemetry]:
    """Get Ollama telemetry service if available."""
    if not OLLAMA_AVAILABLE:
        return None
    try:
        return OllamaTelemetry()
    except Exception as e:
        logger.debug(f"Could not create Ollama telemetry: {e}")
        return None
