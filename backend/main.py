"""
FastAPI application entry point for aiDAPTIV+ demo backend.
"""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import websocket, scenarios

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="aiDAPTIV+ Demo Backend",
    description="Backend API for aiDAPTIV+ competitive intelligence demo",
    version="1.0.0"
)

# Configure CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite dev server
        "http://localhost:3000",  # Alternative port
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(scenarios.router)
app.include_router(websocket.router)

@app.on_event("startup")
async def startup_event():
    """Log startup message."""
    import config
    
    logger.info("=" * 60)
    logger.info("aiDAPTIV+ Demo Backend Started")
    logger.info("=" * 60)
    logger.info("REST API: http://localhost:8000/api")
    logger.info("WebSocket: ws://localhost:8000/ws/analysis")
    logger.info("Docs: http://localhost:8000/docs")
    logger.info("=" * 60)
    logger.info(f"Ollama Integration: {'ENABLED' if config.USE_REAL_OLLAMA else 'DISABLED (using canned responses)'}")
    if config.USE_REAL_OLLAMA:
        logger.info(f"Ollama Host: {config.OLLAMA_HOST}")
        logger.info(f"Ollama Model: {config.OLLAMA_MODEL}")
    logger.info("=" * 60)


@app.on_event("shutdown")
async def shutdown_event():
    """Log shutdown message."""
    logger.info("aiDAPTIV+ Demo Backend Shutting Down")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
