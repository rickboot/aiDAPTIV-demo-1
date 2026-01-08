"""
Memory monitoring service for aiDAPTIV+ demo.
Calculates simulated memory usage based on simulation progress.
"""

from models.schemas import MemoryData, ScenarioConfig


class MemoryMonitor:
    """
    Simulates memory usage for the aiDAPTIV+ demo.
    
    Models unified memory (16GB MacBook Air M4) and virtual memory
    (aiDAPTIV+ SSD offload) based on simulation progress.
    """
    
    UNIFIED_TOTAL_GB = 16.0
    CRITICAL_THRESHOLD = 0.95  # 95% triggers aiDAPTIV+ or crash
    
    def __init__(self, config: ScenarioConfig, aidaptiv_enabled: bool):
        """
        Initialize memory monitor.
        
        Args:
            config: Scenario configuration with memory target
            aidaptiv_enabled: Whether aiDAPTIV+ is enabled
        """
        self.config = config
        self.aidaptiv_enabled = aidaptiv_enabled
        self.memory_target_gb = config.memory_target_gb
        
    def calculate_memory(self, progress_percent: float) -> tuple[MemoryData, bool]:
        """
        Calculate memory usage at a given progress point.
        
        Args:
            progress_percent: Simulation progress (0-100)
            
        Returns:
            Tuple of (MemoryData, should_crash)
        """
        # Calculate raw memory need based on progress
        raw_memory_gb = (progress_percent / 100.0) * self.memory_target_gb
        
        # Determine unified and virtual memory split
        if raw_memory_gb <= self.UNIFIED_TOTAL_GB:
            # Fits entirely in unified memory
            unified_gb = raw_memory_gb
            virtual_gb = 0.0
            virtual_active = False
            should_crash = False
            
        elif raw_memory_gb > self.UNIFIED_TOTAL_GB:
            # Exceeds unified memory capacity
            unified_gb = self.UNIFIED_TOTAL_GB
            overflow = raw_memory_gb - self.UNIFIED_TOTAL_GB
            
            if self.aidaptiv_enabled:
                # aiDAPTIV+ handles overflow with virtual memory
                virtual_gb = overflow
                virtual_active = True
                should_crash = False
            else:
                # No aiDAPTIV+: crash when hitting limit
                virtual_gb = 0.0
                virtual_active = False
                should_crash = True
        else:
            unified_gb = raw_memory_gb
            virtual_gb = 0.0
            virtual_active = False
            should_crash = False
        
        # Calculate percentages
        unified_percent = min((unified_gb / self.UNIFIED_TOTAL_GB) * 100, 100.0)
        virtual_percent = (virtual_gb / self.UNIFIED_TOTAL_GB) * 100 if virtual_active else 0.0
        
        memory_data = MemoryData(
            unified_percent=round(unified_percent, 1),
            unified_gb=round(unified_gb, 2),
            unified_total_gb=self.UNIFIED_TOTAL_GB,
            virtual_percent=round(virtual_percent, 1),
            virtual_gb=round(virtual_gb, 2),
            virtual_active=virtual_active
        )
        
        return memory_data, should_crash
    
    def get_crash_point_percent(self) -> float:
        """
        Calculate the progress percentage where crash occurs (if aiDAPTIV+ disabled).
        
        Returns:
            Progress percentage where unified memory is exhausted
        """
        if self.memory_target_gb <= self.UNIFIED_TOTAL_GB:
            return 100.0  # Won't crash - fits in unified memory
        
        # Calculate when unified memory hits 100%
        crash_percent = (self.UNIFIED_TOTAL_GB / self.memory_target_gb) * 100
        return round(crash_percent, 1)
