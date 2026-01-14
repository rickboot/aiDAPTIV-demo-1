"""
Memory monitoring service for aiDAPTIV+ demo.
Uses real system telemetry via psutil.
Attempts to get real KV cache stats from Ollama when available.
"""

import logging
import psutil
from models.schemas import MemoryData, ScenarioConfig
from services.ollama_telemetry import get_ollama_telemetry

logger = logging.getLogger(__name__)


class MemoryMonitor:
    """
    Monitors real system memory usage for the aiDAPTIV+ demo.
    
    Uses psutil to track actual RAM and swap usage.
    """
    
    def __init__(self, config: ScenarioConfig, aidaptiv_enabled: bool):
        """
        Initialize memory monitor.
        
        Args:
            config: Scenario configuration
            aidaptiv_enabled: Whether aiDAPTIV+ is enabled
        """
        self.config = config
        self.aidaptiv_enabled = aidaptiv_enabled
        
        # Capture baseline swap usage at start
        swap = psutil.swap_memory()
        self.baseline_swap_gb = swap.used / (1024**3)
        
        # Context and model tracking
        self.context_tokens = 0
        self.current_model_name = "llama3.1:8b"
        self.current_model_size_gb = 5.0  # Default: llama3.1:8b
        
        # Ollama telemetry (for real KV cache stats)
        self.ollama_telemetry = get_ollama_telemetry()
        
    def set_context_size(self, tokens: int):
        """Update current context size in tokens."""
        self.context_tokens = tokens
    
    def set_model_size(self, model_name: str):
        """Update current model size based on model name."""
        self.current_model_name = model_name
        model_sizes = {
            "llama3.1:8b": 5.0,
            "qwen2.5:14b": 9.0,
            "qwen2.5:32b": 19.0,
            "llava:13b": 8.0,
            "llava:34b": 20.0,
            "llava": 4.7
        }
        self.current_model_size_gb = model_sizes.get(model_name, 5.0)
    
    def _estimate_kv_cache_size(self) -> float:
        """
        Get KV cache size - tries real Ollama telemetry first, then estimates.
        
        Returns:
            KV cache size in GB
        """
        if self.context_tokens == 0:
            return 0.0
        
        # Try to get real KV cache from Ollama (logs or API)
        if self.ollama_telemetry:
            try:
                kv_info = self.ollama_telemetry.get_kv_cache_info(
                    self.context_tokens,
                    self.current_model_size_gb
                )
                kv_cache_gb = kv_info.get("kv_cache_gb", 0.0)
                source = kv_info.get("source", "unknown")
                
                # Log if we got real telemetry
                if source == "ollama_logs":
                    logger.debug(f"KV Cache from Ollama logs: {kv_cache_gb}GB")
                elif source == "ollama_api_estimate":
                    logger.debug(f"KV Cache estimated from Ollama API: {kv_cache_gb}GB")
                
                return kv_cache_gb
            except Exception as e:
                logger.debug(f"Could not get Ollama KV cache telemetry: {e}")
        
        # Fallback to formula-based estimate
        base_per_1k_tokens = 0.015  # 15MB per 1000 tokens for 8B model
        scale_factor = self.current_model_size_gb / 5.0  # Scale with model size
        kv_cache_gb = (self.context_tokens / 1000) * base_per_1k_tokens * scale_factor
        return round(kv_cache_gb, 2)
        
    def calculate_memory(self) -> tuple[MemoryData, bool]:
        """
        Calculate memory usage using real system telemetry.
        
        Returns:
            Tuple of (MemoryData, should_crash)
        """
        # Get Real System Stats
        vm = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        # Unified Memory (System RAM)
        unified_gb = vm.used / (1024**3)
        unified_total_gb = vm.total / (1024**3)
        unified_percent = vm.percent
        
        # Virtual Memory (Swap -> aiDAPTIV+ SSD Offload narrative)
        virtual_gb = swap.used / (1024**3)
        virtual_active = virtual_gb > 0.1  # Active if > 100MB swap
        virtual_percent = swap.percent
        
        # Crash Logic: Only crash if swap INCREASES significantly from baseline
        # This prevents false positives from existing system swap usage
        swap_delta = virtual_gb - self.baseline_swap_gb
        should_crash = False
        if not self.aidaptiv_enabled and swap_delta > 2.0:
            # Swap increased by >2GB during simulation - would crash
            should_crash = True
        
        # Calculate KV cache size
        kv_cache_gb = self._estimate_kv_cache_size()
        
        memory_data = MemoryData(
            unified_percent=round(unified_percent, 1),
            unified_gb=round(unified_gb, 2),
            unified_total_gb=round(unified_total_gb, 1),
            virtual_percent=round(virtual_percent, 1),
            virtual_gb=round(virtual_gb, 2),
            virtual_active=virtual_active,
            context_tokens=self.context_tokens,
            kv_cache_gb=kv_cache_gb,
            model_weights_gb=self.current_model_size_gb,
            loaded_model=self.current_model_name
        )
        
        return memory_data, should_crash


