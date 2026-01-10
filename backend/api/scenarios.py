"""
REST API endpoints for scenario management.
"""

import psutil
import platform
from fastapi import APIRouter, UploadFile, File
from models.schemas import (
    HealthResponse, SystemInfo, ScenarioListResponse, ScenarioListItem,
    StartSimulationResponse, SimulationRequest
)
from services.memory_tier_manager import MemoryTierManager
from services.image_gen_service import ImageGenService

router = APIRouter(prefix="/api")

# Initialize services
memory_tier_manager = MemoryTierManager()
image_gen_service = ImageGenService()


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
            name="CES 2026 Intelligence Platform",
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


@router.post("/analyze/image")
async def analyze_image(
    file: UploadFile = File(...),
    prompt: str = "Analyze this image and describe what you see"
):
    """
    Analyze an uploaded image using LLaVA.
    
    Args:
        file: Uploaded image file
        prompt: Analysis prompt
        
    Returns:
        Analysis results
    """
    # Save uploaded file temporarily
    import tempfile
    from pathlib import Path
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name
    
    # Analyze image
    result = await vision_service_13b.analyze_image(tmp_path, prompt)
    
    # Clean up temp file
    Path(tmp_path).unlink()
    
    return result


@router.post("/analyze/video")
async def analyze_video(
    file: UploadFile = File(...),
    prompt: str = "Analyze this video and summarize the key points",
    max_frames: int = 10
):
    """
    Analyze an uploaded video using LLaVA.
    
    Args:
        file: Uploaded video file
        prompt: Analysis prompt
        max_frames: Maximum number of frames to analyze
        
    Returns:
        Video analysis results
    """
    # Save uploaded file temporarily
    import tempfile
    from pathlib import Path
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name
    
    # Analyze video
    result = await vision_service_34b.analyze_video(tmp_path, prompt, max_frames)
    
    # Clean up temp file
    Path(tmp_path).unlink()
    
    return result


@router.post("/generate/infographic")
async def generate_infographic(findings: dict):
    """
    Generate an executive summary infographic from analysis findings.
    
    Args:
        findings: Dict containing analysis results
        
    Returns:
        Path to generated infographic
    """
    image_path = await image_gen_service.generate_infographic(findings)
    return {"image_url": image_path, "status": "generated"}


@router.post("/generate/timeline")
async def generate_timeline(historical_data: list):
    """
    Generate a trend timeline visualization.
    
    Args:
        historical_data: List of historical events/data points
        
    Returns:
        Path to generated timeline
    """
    image_path = await image_gen_service.generate_timeline(historical_data)
    return {"image_url": image_path, "status": "generated"}
