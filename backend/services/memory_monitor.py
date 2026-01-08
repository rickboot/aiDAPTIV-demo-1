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
        Calculate memory usage using REAL System Telemetry.
        """
        import psutil
        
        # Get Real System Stats
        vm = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        # Unified Memory (System RAM)
        # Using 'used' gives better correlation to active workload than 'active'
        unified_gb = vm.used / (1024**3)
        unified_total_gb = vm.total / (1024**3)
        unified_percent = vm.percent
        
        # Virtual Memory (Swap -> Narrative: aiDAPTIV+ SSD Offload)
        virtual_gb = swap.used / (1024**3)
        virtual_active = virtual_gb > 0.1  # Consider active if > 100MB swap
        virtual_percent = swap.percent
        
        # Crash Logic:
        # In real scenario, if aidaptiv is disabled (no swap allowed narrative),
        # but we are using swap, we theoretically "crashed".
        # For the demo, we won't force-stop, but we flag it.
        should_crash = False
        if not self.aidaptiv_enabled and virtual_active:
            # Optional: could trigger crash event if desired
            pass
        
        memory_data = MemoryData(
            unified_percent=round(unified_percent, 1),
            unified_gb=round(unified_gb, 2),
            unified_total_gb=round(unified_total_gb, 1),
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
