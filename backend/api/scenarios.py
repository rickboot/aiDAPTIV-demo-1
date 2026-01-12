"""
REST API endpoints for scenario management.
"""

import psutil
import platform
from fastapi import APIRouter
from models.schemas import (
    HealthResponse, SystemInfo, ScenarioListResponse, ScenarioListItem,
    StartSimulationResponse, SimulationRequest
)
from services.memory_tier_manager import MemoryTierManager
from services.ollama_service import OllamaService
import config as app_config

router = APIRouter(prefix="/api")

# Initialize services
memory_tier_manager = MemoryTierManager()

# Initialize Ollama service only if enabled
def get_ollama_service():
    """Get Ollama service instance, creating if needed."""
    if not app_config.USE_REAL_OLLAMA:
        return None
    try:
        return OllamaService(app_config.OLLAMA_HOST, app_config.OLLAMA_MODEL)
    except Exception:
        return None


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(status="ok")


@router.get("/system/info", response_model=SystemInfo)
async def system_info():
    """Get dynamic system information."""
    # Get total memory in GB
    vm = psutil.virtual_memory()
    total_gb = vm.total / (1024**3)
    
    # Get Processor Info
    proc_info = platform.machine()
    system_name = platform.system()
    
    model_name = "Workstation"
    if system_name == "Darwin":
        model_name = f"Apple Silicon ({proc_info})"
    elif system_name == "Windows":
        model_name = f"Windows PC ({proc_info})"
        
    return SystemInfo(
        memory_gb=round(total_gb, 1),
        model=model_name,
        platform=system_name.lower()
    )


@router.get("/memory/current")
async def current_memory():
    """Get current memory usage for baseline telemetry."""
    vm = psutil.virtual_memory()
    swap = psutil.swap_memory()
    
    return {
        "unified_percent": round(vm.percent, 1),
        "unified_gb": round(vm.used / (1024**3), 2),
        "unified_total_gb": round(vm.total / (1024**3), 1),
        "virtual_percent": round(swap.percent, 1),
        "virtual_gb": round(swap.used / (1024**3), 2),
        "virtual_active": swap.used > 100 * 1024 * 1024  # >100MB
    }


@router.get("/scenarios", response_model=ScenarioListResponse)
async def list_scenarios():
    """List available scenarios."""
    scenarios = [
        ScenarioListItem(
            id="ces2026",
            name="Marketing Intelligence",
            tiers=["standard"]
        )
    ]
    return ScenarioListResponse(scenarios=scenarios)


@router.post("/scenarios/start", response_model=StartSimulationResponse)
async def start_simulation(request: SimulationRequest):
    """
    Start a simulation (returns WebSocket URL).
    
    Note: This endpoint just returns the WebSocket URL.
    The actual simulation starts when the client connects to the WebSocket.
    """
    return StartSimulationResponse(
        ws_url="ws://localhost:8000/ws/analysis",
        scenario=request.scenario,
        tier=request.tier,
        aidaptiv_enabled=request.aidaptiv_enabled
    )


@router.get("/capabilities")
async def get_capabilities(aidaptiv_enabled: bool = False):
    """
    Get available features based on system memory and aiDAPTIV+ status.
    
    Args:
        aidaptiv_enabled: Whether aiDAPTIV+ is enabled
        
    Returns:
        Dict with tier info and available features
    """
    tier = memory_tier_manager.detect_tier(aidaptiv_enabled)
    tier_info = memory_tier_manager.get_tier_info(tier)
    tier_info["upgrade_message"] = memory_tier_manager.get_upgrade_message(tier)
    return tier_info


@router.get("/ollama/status")
async def ollama_status():
    """
    Check Ollama service status.
    
    Returns:
        Dict with Ollama availability and status
    """
    if not app_config.USE_REAL_OLLAMA:
        return {
            "available": True,
            "enabled": False,
            "message": "Ollama disabled (using canned responses)",
            "model": None
        }
    
    ollama_service = get_ollama_service()
    if not ollama_service:
        return {
            "available": False,
            "enabled": True,
            "message": "Ollama service not initialized",
            "model": app_config.OLLAMA_MODEL
        }
    
    available, error_msg = ollama_service.check_availability()
    
    return {
        "available": available,
        "enabled": True,
        "message": error_msg if not available else "Ollama is running",
        "model": app_config.OLLAMA_MODEL,
        "host": app_config.OLLAMA_HOST
    }


