"""
Pydantic models for aiDAPTIV+ demo backend.
Defines data schemas for WebSocket messages, simulation config, and API responses.
"""

from pydantic import BaseModel, Field
from typing import Literal, Optional, Dict, Any
from datetime import datetime


# ═══════════════════════════════════════════════════════════════
# SIMULATION CONFIGURATION
# ═══════════════════════════════════════════════════════════════

class ScenarioConfig(BaseModel):
    """Configuration for a simulation scenario."""
    scenario: Literal["pmm", "ces2026"] = "pmm"
    tier: Literal["lite", "large", "standard"] = "lite"
    duration_seconds: int
    total_documents: int
    memory_target_gb: float
    crash_threshold_percent: Optional[float] = None  # Only for large tier without aiDAPTIV+
    
    class Config:
        json_schema_extra = {
            "example": {
                "scenario": "pmm",
                "tier": "large",
                "duration_seconds": 30,
                "total_documents": 268,
                "memory_target_gb": 19.0,
                "crash_threshold_percent": 76.0
            }
        }


class SimulationRequest(BaseModel):
    """Request to start a simulation."""
    scenario: Literal["pmm"] = "pmm"
    tier: Literal["lite", "large"] = "lite"
    aidaptiv_enabled: bool = False


# ═══════════════════════════════════════════════════════════════
# WEBSOCKET EVENT MESSAGES
# ═══════════════════════════════════════════════════════════════

class ThoughtData(BaseModel):
    """AI reasoning thought data."""
    text: str
    status: Literal["PROCESSING", "ACTIVE", "ANALYZING", "COMPLETE", "WARNING"]
    timestamp: str
    step_type: Optional[Literal["plan", "action", "observation", "thought", "tool_use"]] = "thought"
    tools: Optional[list[str]] = None
    parent_id: Optional[str] = None
    related_doc_ids: Optional[list[str]] = None
    author: Optional[str] = None
    source: Optional[str] = None  # Document being analyzed (e.g., "intel_panther_lake.png")


class ThoughtEvent(BaseModel):
    """AI thought event message."""
    type: Literal["thought"] = "thought"
    data: ThoughtData


class MemoryData(BaseModel):
    """Memory usage statistics."""
    unified_percent: float = Field(..., ge=0, le=100)
    unified_gb: float = Field(..., ge=0)
    unified_total_gb: float = 16.0
    virtual_percent: float = Field(default=0.0, ge=0, le=100)
    virtual_gb: float = Field(default=0.0, ge=0)
    virtual_active: bool = False
    
    # Context and KV cache tracking
    context_tokens: int = Field(default=0, ge=0)
    kv_cache_gb: float = Field(default=0.0, ge=0)
    model_weights_gb: float = Field(default=0.0, ge=0)
    loaded_model: str = Field(default="llama3.1:8b", description="Currently loaded model name")


class MemoryEvent(BaseModel):
    """Memory update event message."""
    type: Literal["memory"] = "memory"
    data: MemoryData


class DocumentData(BaseModel):
    """Document processing data."""
    name: str
    index: int = Field(..., ge=0)
    total: int = Field(..., gt=0)
    category: Literal["competitor", "paper", "social", "dossier", "news", "documentation", "video", "image"]
    size_kb: float = Field(default=50.0, ge=0)


class DocumentEvent(BaseModel):
    """Document processing event message."""
    type: Literal["document"] = "document"
    data: DocumentData


class MetricData(BaseModel):
    """Metric update data."""
    name: Literal["key_topics", "patterns_detected", "insights_generated", "critical_flags"]
    value: int = Field(..., ge=0)


class MetricEvent(BaseModel):
    """Metric update event message."""
    type: Literal["metric"] = "metric"
    data: MetricData


class PerformanceData(BaseModel):
    """Performance metrics data."""
    ttft_ms: int = Field(..., ge=0, description="Time to first token in milliseconds")
    tokens_per_second: float = Field(..., ge=0, description="Token generation speed")
    latency_ms: int = Field(..., ge=0, description="Average token latency in milliseconds")
    status: Literal["optimal", "degraded", "critical"]
    degradation_percent: int = Field(default=0, ge=0, le=100)


class PerformanceEvent(BaseModel):
    """Performance update event message."""
    type: Literal["performance"] = "performance"
    data: PerformanceData


class StatusEvent(BaseModel):
    """Status update event message."""
    type: Literal["status"] = "status"
    message: str = Field(..., description="Current activity status message")


class DocumentStatusEvent(BaseModel):
    """Explicit document status update."""
    type: Literal["document_status"] = "document_status"
    data: dict = Field(..., description="{index, status}")


class ImpactSummaryData(BaseModel):
    """Analysis impact summary data."""
    documents_processed: int = Field(..., ge=0, description="Number of documents successfully processed")
    total_documents: int = Field(..., ge=0, description="Total documents in analysis")
    context_size_gb: float = Field(..., ge=0, description="Total context size in GB")
    memory_saved_gb: float = Field(default=0, ge=0, description="Memory offloaded to SSD in GB")
    estimated_cost_local: float = Field(default=0, ge=0, description="Cost to run locally")
    estimated_cost_cloud: float = Field(..., ge=0, description="Cost to run on cloud GPU")
    time_minutes: float = Field(..., ge=0, description="Actual analysis time in minutes")
    time_without_aidaptiv: float = Field(..., ge=0, description="Estimated time without aiDAPTIV+")


class ImpactSummaryEvent(BaseModel):
    """Impact summary event message."""
    type: Literal["impact_summary"] = "impact_summary"
    data: ImpactSummaryData


class FindingsData(BaseModel):
    """Analysis findings."""
    shifts_detected: int
    evidence: str
    recommendation: str


class MemoryStatsData(BaseModel):
    """Final memory statistics."""
    unified_gb: float
    virtual_gb: float
    total_gb: float


class CompleteData(BaseModel):
    """Simulation completion data."""
    success: bool = True
    scenario: str
    tier: str
    findings: FindingsData
    memory_stats: MemoryStatsData


class CompleteEvent(BaseModel):
    """Simulation complete event message."""
    type: Literal["complete"] = "complete"
    data: CompleteData


class CrashData(BaseModel):
    """Crash event data."""
    reason: str
    memory_snapshot: MemoryData
    processed_documents: int = Field(default=0, description="Number of documents processed before crash")
    total_documents: int = Field(default=0, description="Total documents in scenario")
    required_vram_gb: float = Field(default=0.0, description="Estimated VRAM needed")


class CrashEvent(BaseModel):
    """Simulation crash event message."""
    type: Literal["crash"] = "crash"
    data: CrashData


class RAGStorageData(BaseModel):
    """RAG document storage event data."""
    document_name: str
    document_category: str
    tokens: int
    total_documents_in_db: int
    timestamp: str


class RAGStorageEvent(BaseModel):
    """RAG document storage event message."""
    type: Literal["rag_storage"] = "rag_storage"
    data: RAGStorageData


class RAGRetrievalData(BaseModel):
    """RAG retrieval event data."""
    query_preview: str  # First 100 chars of query
    query_length: int
    candidates_found: int
    documents_retrieved: int
    tokens_retrieved: int
    tokens_limit: int
    excluded_count: int
    retrieved_document_names: list[str]
    timestamp: str


class RAGRetrievalEvent(BaseModel):
    """RAG retrieval event message."""
    type: Literal["rag_retrieval"] = "rag_retrieval"
    data: RAGRetrievalData


# ═══════════════════════════════════════════════════════════════
# API RESPONSE MODELS
# ═══════════════════════════════════════════════════════════════

class HealthResponse(BaseModel):
    """Health check response."""
    status: Literal["ok"] = "ok"


class SystemInfo(BaseModel):
    """System information response."""
    memory_gb: float = 16.0
    model: str = "MacBook Air M4"
    platform: str = "darwin"


class ScenarioListItem(BaseModel):
    """Scenario list item."""
    id: str
    name: str
    tiers: list[str]


class ScenarioListResponse(BaseModel):
    """List of available scenarios."""
    scenarios: list[ScenarioListItem]


class StartSimulationResponse(BaseModel):
    """Response when starting a simulation."""
    ws_url: str
    scenario: str
    tier: str
    aidaptiv_enabled: bool
