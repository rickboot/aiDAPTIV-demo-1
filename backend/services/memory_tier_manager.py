"""
Memory Tier Manager - Dynamic Feature Gating Based on Available Memory
"""
import psutil
import logging
from typing import Dict, List
import config as app_config

logger = logging.getLogger(__name__)

class MemoryTierManager:
    """Manages feature availability based on system memory and aiDAPTIV+ status"""
    
    # Memory thresholds (in GB)
    TIER_THRESHOLDS = {
        "text_only": 8,
        "standard": 16,
        "pro": 32
    }
    
    # Model configurations per tier
    # Dev mode uses lighter models for faster iteration on resource-constrained systems
    TIER_MODELS_PROD = {
        "text_only": {
            "text_analysis": "llama3.1:8b"
        },
        "standard": {
            "text_analysis": "llama3.1:8b",
            "image_analysis": "llava:13b"
        },
        "pro": {
            "text_analysis": "llama3.1:8b",  # Using 8b for demo speed
            "image_analysis": "llava:13b",  # Changed from 34b to prevent memory thrashing on 16GB systems
            "video_analysis": "llava:13b",  # Changed from 34b to prevent memory thrashing on 16GB systems
            "cross_modal": "qwen2.5:14b",
            "image_generation": "stable-diffusion-xl"
        }
    }
    
    # Lighter models for development (faster, less memory, still functional)
    TIER_MODELS_DEV = {
        "text_only": {
            "text_analysis": "llama3.2:3b"  # 2.0 GB instead of 4.9 GB - much lighter!
        },
        "standard": {
            "text_analysis": "llama3.2:3b",  # 2.0 GB instead of 4.9 GB
            "image_analysis": "llava:latest"  # 4.7 GB instead of 8.0 GB
        },
        "pro": {
            "text_analysis": "llama3.2:3b",  # 2.0 GB instead of 4.9 GB
            "image_analysis": "llava:latest",  # 4.7 GB instead of 8.0 GB
            "video_analysis": "llava:latest",  # 4.7 GB instead of 8.0 GB
            "cross_modal": "phi3:mini",  # 1.7 GB instead of 9.0 GB - much lighter!
            "image_generation": "stable-diffusion-xl"
        }
    }
    
    @property
    def TIER_MODELS(self):
        """Return appropriate model config based on DEV_MODE setting."""
        if app_config.DEV_MODE:
            logger.info("Using DEV_MODE: lighter models for faster development")
            return self.TIER_MODELS_DEV
        else:
            return self.TIER_MODELS_PROD
    
    # Feature definitions (metadata for display, min_tier is now redundant but kept for structure)
    FEATURES = {
        "text_analysis": {
            "name": "Text Analysis",
            "description": "Analyze press releases, news, social posts",
            "min_tier": "text_only" # This will be overridden by the 'features' list in self.tiers
        },
        "image_analysis": {
            "name": "Image Analysis",
            "description": "OCR, logo detection, infographic analysis",
            "min_tier": "standard"
        },
        "video_analysis": {
            "name": "Video Analysis",
            "description": "Keynote extraction, demo walkthroughs",
            "min_tier": "pro"
        },
        "infographic_generation": {
            "name": "Infographic Generation",
            "description": "AI-generated executive summaries",
            "min_tier": "pro"
        },
        "parallel_agents": {
            "name": "Parallel Multi-Agent",
            "description": "5 agents running simultaneously",
            "min_tier": "pro"
        }
    }
    
    def __init__(self):
        logger.info("Initialized MemoryTierManager")
    
    def get_available_memory_gb(self) -> float:
        """Get currently available system memory in GB"""
        mem = psutil.virtual_memory()
        return mem.available / (1024 ** 3)
    
    def get_total_memory_gb(self) -> float:
        """Get total system memory in GB"""
        mem = psutil.virtual_memory()
        return mem.total / (1024 ** 3)
    
    def detect_tier(self, aidaptiv_enabled: bool = False) -> str:
        """
        Detect appropriate tier based on available memory and aiDAPTIV+ status
        
        Args:
            aidaptiv_enabled: Whether aiDAPTIV+ is enabled
            
        Returns:
            Tier name: "text_only", "standard", or "pro"
        """
        available_gb = self.get_available_memory_gb()
        total_gb = self.get_total_memory_gb()
        
        logger.info(f"Memory detection: {available_gb:.1f}GB available / {total_gb:.1f}GB total, aiDAPTIV+: {aidaptiv_enabled}")
        
        # If aiDAPTIV+ is enabled, unlock Pro tier regardless of RAM
        if aidaptiv_enabled:
            logger.info("aiDAPTIV+ enabled - unlocking Pro tier")
            return "pro"
        
        # Otherwise, tier based on available memory
        if available_gb < self.TIER_THRESHOLDS["standard"]:
            logger.info("Low memory - Text-only tier")
            return "text_only"
        elif available_gb < self.TIER_THRESHOLDS["pro"]:
            logger.info("Moderate memory - Standard tier")
            return "standard"
        else:
            logger.info("High memory - Pro tier")
            return "pro"
    
    def get_enabled_features(self, tier: str) -> List[str]:
        """
        Get list of enabled features for a given tier
        
        Args:
            tier: Tier name
            
        Returns:
            List of enabled feature keys
        """
        tier_levels = {"text_only": 1, "standard": 2, "pro": 3}
        current_level = tier_levels.get(tier, 1)
        
        enabled = []
        for feature_key, feature_info in self.FEATURES.items():
            min_level = tier_levels.get(feature_info["min_tier"], 1)
            if current_level >= min_level:
                enabled.append(feature_key)
        
        logger.info(f"Tier '{tier}' enables features: {enabled}")
        return enabled
    
    def get_disabled_features(self, tier: str) -> List[str]:
        """Get list of disabled features for a given tier"""
        enabled = set(self.get_enabled_features(tier))
        all_features = set(self.FEATURES.keys())
        return list(all_features - enabled)
    
    def get_models_for_tier(self, tier: str) -> Dict[str, str]:
        """
        Get optimal model configurations for a tier
        
        Args:
            tier: Tier name
            
        Returns:
            Dict mapping capability to model name
        """
        # Access property to get correct model config (dev or prod)
        models = self.TIER_MODELS
        return models.get(tier, {})
    
    def get_tier_info(self, tier: str) -> Dict:
        """
        Get comprehensive information about a tier
        
        Args:
            tier: Tier name
            
        Returns:
            Dict with tier details
        """
        return {
            "tier": tier,
            "enabled_features": self.get_enabled_features(tier),
            "disabled_features": self.get_disabled_features(tier),
            "models": self.get_models_for_tier(tier),
            "memory_threshold_gb": self.TIER_THRESHOLDS.get(tier, 0),
            "available_memory_gb": self.get_available_memory_gb(),
            "total_memory_gb": self.get_total_memory_gb()
        }
    
    def can_enable_feature(self, feature_key: str, tier: str) -> bool:
        """Check if a feature is available in the current tier"""
        return feature_key in self.get_enabled_features(tier)
    
    def get_upgrade_message(self, tier: str) -> str:
        """Get user-facing message about upgrading tier"""
        if tier == "pro":
            return "All features unlocked!"
        elif tier == "standard":
            return "Enable aiDAPTIV+ to unlock video analysis and infographic generation."
        else:  # text_only
            return "Enable aiDAPTIV+ to unlock image analysis, video analysis, and infographic generation."
