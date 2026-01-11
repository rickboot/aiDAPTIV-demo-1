import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class SessionManager:
    """
    Manages persistent session storage using JSON files.
    Stores:
    - Active simulation state
    - User preferences
    - Cumulative metrics (billing/TCO)
    """
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.sessions_dir = self.data_dir / "sessions"
        self.metrics_file = self.data_dir / "metrics.json"
        self.prefs_file = self.data_dir / "preferences.json"
        
        # Ensure directories exist
        self.sessions_dir.mkdir(parents=True, exist_ok=True)
        
    def save_session(self, session_id: str, data: Dict[str, Any]):
        """Save a simulation session state."""
        try:
            file_path = self.sessions_dir / f"{session_id}.json"
            data["last_updated"] = datetime.utcnow().isoformat()
            
            with open(file_path, "w") as f:
                json.dump(data, f, indent=2, default=str)
                
            logger.info(f"Saved session {session_id}")
        except Exception as e:
            logger.error(f"Failed to save session {session_id}: {e}")
            
    def load_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Load a simulation session state."""
        try:
            file_path = self.sessions_dir / f"{session_id}.json"
            if not file_path.exists():
                return None
                
            with open(file_path, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load session {session_id}: {e}")
            return None
            
    def save_metrics(self, cumulative_input: int, cumulative_output: int):
        """Save cumulative billing metrics."""
        try:
            metrics = {
                "cumulative_input_tokens": cumulative_input,
                "cumulative_output_tokens": cumulative_output,
                "last_updated": datetime.utcnow().isoformat()
            }
            
            with open(self.metrics_file, "w") as f:
                json.dump(metrics, f, indent=2)
                
        except Exception as e:
            logger.error(f"Failed to save metrics: {e}")
            
    def load_metrics(self) -> Dict[str, int]:
        """Load cumulative billing metrics."""
        try:
            if not self.metrics_file.exists():
                return {"cumulative_input_tokens": 0, "cumulative_output_tokens": 0}
                
            with open(self.metrics_file, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load metrics: {e}")
            return {"cumulative_input_tokens": 0, "cumulative_output_tokens": 0}
