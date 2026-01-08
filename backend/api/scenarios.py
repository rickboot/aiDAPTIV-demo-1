"""
REST API endpoints for scenario management.
"""

from fastapi import APIRouter
from models.schemas import (
    HealthResponse, SystemInfo, ScenarioListResponse, ScenarioListItem,
    StartSimulationResponse, SimulationRequest
)

router = APIRouter(prefix="/api")


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(status="ok")


@router.get("/system/info", response_model=SystemInfo)
async def system_info():
    """Get system information."""
    return SystemInfo(
        memory_gb=16.0,
        model="MacBook Air M4",
        platform="darwin"
    )


@router.get("/scenarios", response_model=ScenarioListResponse)
async def list_scenarios():
    """List available scenarios."""
    scenarios = [
        ScenarioListItem(
            id="pmm",
            name="PMM Competitive Intelligence",
            tiers=["lite", "large"]
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
