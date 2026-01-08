"""
Performance monitoring for LLM analysis.
Simulates performance metrics (TTFT, tokens/sec, latency) based on memory pressure.
"""

from typing import Dict
import logging

logger = logging.getLogger(__name__)


class PerformanceMonitor:
    """Monitor and simulate LLM performance metrics."""
    
    def __init__(self):
        # Baseline performance (optimal conditions)
        self.baseline_ttft_ms = 200  # Time to first token
        self.baseline_tokens_per_sec = 45.0  # Token generation speed
        self.baseline_latency_ms = 22  # Average token latency
    
    def calculate_performance(
        self, 
        memory_percent: float, 
        aidaptiv_enabled: bool
    ) -> Dict:
        """
        Calculate performance metrics based on memory pressure.
        
        Args:
            memory_percent: Current memory usage percentage (0-100)
            aidaptiv_enabled: Whether aiDAPTIV+ is active
        
        Returns:
            Dict with performance metrics and status
        """
        # Determine degradation factor based on memory pressure
        if aidaptiv_enabled:
            # With aiDAPTIV+: Minimal degradation even at high memory
            # Memory offloads to SSD, keeping GPU/unified memory free
            if memory_percent < 70:
                degradation = 0.0  # Optimal
            else:
                # Slight degradation from SSD latency
                degradation = min(0.15, (memory_percent - 70) / 200)
        else:
            # Without aiDAPTIV+: Significant degradation as memory fills
            if memory_percent < 70:
                degradation = 0.0  # Optimal
            elif memory_percent < 85:
                # Moderate degradation (thrashing starts)
                degradation = (memory_percent - 70) / 50  # 0 to 0.3
            else:
                # Severe degradation (heavy thrashing)
                degradation = 0.3 + ((memory_percent - 85) / 15) * 0.6  # 0.3 to 0.9
        
        # Apply degradation to metrics
        ttft_ms = int(self.baseline_ttft_ms * (1 + degradation * 5))  # 200ms → 1200ms
        tokens_per_sec = self.baseline_tokens_per_sec * (1 - degradation * 0.67)  # 45 → 15
        latency_ms = int(self.baseline_latency_ms * (1 + degradation * 3))  # 22ms → 88ms
        
        # Determine status
        if ttft_ms < 500 and tokens_per_sec > 35:
            status = "optimal"
        elif ttft_ms < 1000 and tokens_per_sec > 20:
            status = "degraded"
        else:
            status = "critical"
        
        return {
            "ttft_ms": ttft_ms,
            "tokens_per_second": round(tokens_per_sec, 1),
            "latency_ms": latency_ms,
            "status": status,
            "degradation_percent": int(degradation * 100)
        }
