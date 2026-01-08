"""
Memory monitoring service for aiDAPTIV+ demo.
Uses real system telemetry via psutil.
"""

import psutil
from models.schemas import MemoryData, ScenarioConfig


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
        
        # Crash Logic: If aiDAPTIV+ disabled and system is swapping heavily
        should_crash = False
        if not self.aidaptiv_enabled and virtual_active and virtual_gb > 1.0:
            # System is using >1GB swap without aiDAPTIV+ - would crash
            should_crash = True
        
        memory_data = MemoryData(
            unified_percent=round(unified_percent, 1),
            unified_gb=round(unified_gb, 2),
            unified_total_gb=round(unified_total_gb, 1),
            virtual_percent=round(virtual_percent, 1),
            virtual_gb=round(virtual_gb, 2),
            virtual_active=virtual_active
        )
        
        return memory_data, should_crash

