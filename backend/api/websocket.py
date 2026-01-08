"""
WebSocket endpoint for real-time simulation streaming.
"""

import json
import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from services.orchestrator import SimulationOrchestrator

logger = logging.getLogger(__name__)

router = APIRouter()


@router.websocket("/ws/analysis")
async def websocket_analysis(websocket: WebSocket):
    """
    WebSocket endpoint for streaming simulation events.
    
    Client sends: {"scenario": "pmm", "tier": "lite"|"large", "aidaptiv_enabled": true|false}
    Server streams: Event messages (thought, memory, document, metric, complete, crash)
    """
    await websocket.accept()
    logger.info("WebSocket connection established")
    
    try:
        # 1. RECEIVE START PARAMETERS
        data = await websocket.receive_text()
        params = json.loads(data)
        
        scenario = params.get("scenario", "pmm")
        tier = params.get("tier", "lite")
        aidaptiv_enabled = params.get("aidaptiv_enabled", False)
        
        logger.info(f"Starting simulation: scenario={scenario}, tier={tier}, aidaptiv={aidaptiv_enabled}")
        
        # 2. CREATE ORCHESTRATOR
        orchestrator = SimulationOrchestrator(
            scenario=scenario,
            tier=tier,
            aidaptiv_enabled=aidaptiv_enabled
        )
        
        # 3. STREAM EVENTS
        async for event in orchestrator.run_simulation():
            await websocket.send_json(event)
            # Log all events for debugging
            event_type = event.get('type', 'unknown')
            if event_type == 'document':
                logger.info(f"Sent document: {event['data']['name']} ({event['data']['index']+1}/{event['data']['total']})")
            elif event_type in ['complete', 'crash']:
                logger.info(f"Sent event: {event_type}")
        
        logger.info("Simulation completed successfully")
        
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected by client")
    except Exception as e:
        logger.error(f"WebSocket error: {e}", exc_info=True)
        try:
            await websocket.close(code=1011, reason=str(e))
        except:
            pass
