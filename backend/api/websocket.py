"""
WebSocket endpoint for real-time simulation streaming.
"""

import json
import logging
import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from services.orchestrator import SimulationOrchestrator
from services.memory_monitor import MemoryMonitor
from models.schemas import MemoryEvent, ScenarioConfig

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
    
    monitor_task = None
    
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
        
        # 3. START CONTINUOUS BACKGROUND MEMORY MONITOR
        stop_monitor = asyncio.Event()
        
        async def continuous_memory_monitor():
            """Continuously broadcast memory telemetry at 5Hz."""
            memory_monitor = orchestrator.memory_monitor
            while not stop_monitor.is_set():
                try:
                    memory_data, _ = memory_monitor.calculate_memory()
                    event = MemoryEvent(data=memory_data).model_dump()
                    await websocket.send_json(event)
                    await asyncio.sleep(0.2)  # 5Hz
                except Exception as e:
                    logger.error(f"Memory monitor error: {e}")
                    break
        
        monitor_task = asyncio.create_task(continuous_memory_monitor())
        logger.info("Started continuous memory monitor (5Hz)")
        
        # 4. STREAM SIMULATION EVENTS
        async for event in orchestrator.run_simulation():
            # Skip memory events from simulation (monitor handles them)
            if event.get('type') == 'memory':
                continue
                
            await websocket.send_json(event)
            
            # Log important events
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
    finally:
        # Stop background monitor
        if monitor_task:
            stop_monitor.set()
            try:
                await asyncio.wait_for(monitor_task, timeout=1.0)
            except asyncio.TimeoutError:
                monitor_task.cancel()
            logger.info("Stopped continuous memory monitor")
