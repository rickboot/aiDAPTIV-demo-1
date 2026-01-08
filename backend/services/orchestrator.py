"""
Simulation orchestrator for aiDAPTIV+ demo.
Manages simulation flow, timing, and event generation.
"""

import asyncio
from datetime import datetime
from typing import AsyncGenerator, Literal, Optional
from pathlib import Path
import logging

from models.schemas import (
    ScenarioConfig, ThoughtEvent, ThoughtData, MemoryEvent, DocumentEvent,
    DocumentData, MetricEvent, MetricData, CompleteEvent, CompleteData,
    CrashEvent, CrashData, FindingsData, MemoryStatsData, PerformanceEvent, PerformanceData,
    ImpactSummaryEvent, ImpactSummaryData, StatusEvent
)
from services.memory_monitor import MemoryMonitor
from services.performance_monitor import PerformanceMonitor
from services.ollama_service import OllamaService, ANALYSIS_PHASES
import config

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════
# SCENARIO CONFIGURATIONS
# ═══════════════════════════════════════════════════════════════

SCENARIOS = {
    "pmm_lite": ScenarioConfig(
        scenario="pmm",
        tier="lite",
        duration_seconds=60, # Slower for better observability
        total_documents=18,  # 3 competitors + 10 papers + 5 social
        memory_target_gb=10.0,
        crash_threshold_percent=None  # Won't crash - fits in 16GB
    ),
    "pmm_large": ScenarioConfig(
        scenario="pmm",
        tier="large",
        duration_seconds=120, # 2 minutes for full run
        total_documents=268,  # 12 competitors + 234 papers + 22 social
        memory_target_gb=19.0,
        crash_threshold_percent=76.0  # Crashes at 76% without aiDAPTIV+
    )
}


# ═══════════════════════════════════════════════════════════════
# AI THOUGHT TEMPLATES
# ═══════════════════════════════════════════════════════════════

THOUGHT_PHASES = {
    "loading": {
        "text": "Plan: Load visual corpus containing {visual_count} competitor UI screenshots",
        "status": "PROCESSING",
        "trigger_percent": 5,
        "step_type": "plan"
    },
    "analyzing": {
        "text": "Analyzing Competitor X homepage redesign captured Jan 3, 2026",
        "status": "ANALYZING",
        "trigger_percent": 20,
        "step_type": "thought",
        "related_doc_ids": ["Comp_UI_1", "Comp_UI_2"]
    },
    "cross_ref": {
        "text": "Cross-referencing visual changes with arXiv paper 2401.12847",
        "status": "ACTIVE",
        "trigger_percent": 40,
        "step_type": "action",
        "tools": ["arxiv_search", "rag_pipeline"]
    },
    "pattern": {
        "text": "Observation: Detected {shifts} of {total_competitors} competitors shifting to agentic architecture",
        "status": "ACTIVE",
        "trigger_percent": 60,
        "step_type": "observation"
    },
    "memory_pressure": {
        "text": "⚠️ Memory pressure at 95% - triggering aiDAPTIV+ offload to SSD cache",
        "status": "WARNING",
        "trigger_percent": 85,
        "step_type": "tool_use",
        "tools": ["memory_manager"]
    },
    "complete": {
        "text": "✅ Analysis complete: Competitive positioning gap identified",
        "status": "COMPLETE",
        "step_type": "thought"
    }
}


# ═══════════════════════════════════════════════════════════════
# SIMULATION ORCHESTRATOR
# ═══════════════════════════════════════════════════════════════



class SimulationOrchestrator:
    """
    Orchestrates the simulation flow, generating events and managing timing.
    """
    
    def __init__(self, scenario: str, tier: str, aidaptiv_enabled: bool):
        """
        Initialize simulation orchestrator.
        
        Args:
            scenario: Scenario ID (e.g., "pmm")
            tier: Tier level ("lite" or "large")
            aidaptiv_enabled: Whether aiDAPTIV+ is enabled
        """
        config_key = f"{scenario}_{tier}"
        self.config = SCENARIOS[config_key]
        self.scenario = scenario
        self.tier = tier
        self.aidaptiv_enabled = aidaptiv_enabled
        self.memory_monitor = MemoryMonitor(self.config, aidaptiv_enabled)
        
        # Metrics tracking
        self.metrics = {
            "competitors_tracked": 3 if tier == "lite" else 12,
            "visual_updates": 24 if tier == "lite" else 847,
            "papers_analyzed": 10 if tier == "lite" else 234,
            "signals_detected": 1 if tier == "lite" else 3
        }
        
        # Thought phase tracking
        self.thoughts_sent = set()
        
        # Ollama integration
        self.use_ollama = config.USE_REAL_OLLAMA
        self.ollama_service = None
        self.ollama_context = None
        
        # Performance monitoring
        self.performance_monitor = PerformanceMonitor()
        
        # Track active model to visualize swapping
        self.current_model = "llama3.1:8b"
        self.current_progress = 0.0
        
        if self.use_ollama:
            self.ollama_service = OllamaService(config.OLLAMA_HOST, config.OLLAMA_MODEL)
            available, error_msg = self.ollama_service.check_availability()
            if not available:
                logger.warning(f"Ollama not available: {error_msg}")
                logger.warning("Falling back to canned responses")
                self.use_ollama = False
            else:
                logger.info(f"Ollama enabled with model: {config.OLLAMA_MODEL}")
                # Load documents
                try:
                    documents = self.ollama_service.load_documents(scenario, tier)
                    self.ollama_context = self.ollama_service.build_context(documents)
                    logger.info(f"Loaded context: {len(self.ollama_context)} chars, ~{self.ollama_service.count_tokens(self.ollama_context)} tokens")
                except Exception as e:
                    logger.warning("Falling back to canned responses")
                    self.use_ollama = False
        
    async def _wait_with_telemetry(self, duration: float) -> AsyncGenerator[dict, None]:
        """
        Wait for a duration while yielding memory telemetry events.
        Updates at approx 5Hz (every 0.2s).
        """
        steps = int(duration / 0.2)
        if steps < 1:
            await asyncio.sleep(duration)
            return

        chunk = duration / steps
        for _ in range(steps):
            await asyncio.sleep(chunk)
            memory_data, _ = self.memory_monitor.calculate_memory(self.current_progress)
            yield MemoryEvent(data=memory_data).model_dump()
        
    async def run_simulation(self) -> AsyncGenerator[dict, None]:
        """
        Run the simulation and yield events.
        
        Yields:
            Event dictionaries (thought, memory, document, metric, complete, crash)
        """
        try:
            # Send status: Loading documents
            yield {
                "type": "status",
                "message": f"Loading {self.tier} tier documents..."
            }
            await asyncio.sleep(0.1)  # Allow event to be sent
            
            # Send status: Preparing LLM
            if self.use_ollama:
                yield {
                    "type": "status",
                    "message": "Preparing AI model for analysis..."
                }
                await asyncio.sleep(0.1)
            
            # Send status: Starting analysis
            yield {
                "type": "status",
                "message": "Starting document processing..."
            }
            await asyncio.sleep(0.1)
        except Exception as e:
            logger.error(f"Error during simulation initialization: {e}")
            # Optionally yield a crash event or error status here
            return # Stop simulation if initialization fails

        total_docs = self.config.total_documents
        duration = self.config.duration_seconds
        interval = duration / total_docs  # Time per document
        
        # Get document list
        documents = self._get_document_list()
        
        for doc_index in range(total_docs):
            # Calculate current progress
            progress_percent = ((doc_index + 1) / total_docs) * 100
            self.current_progress = progress_percent
            
            # 1. SEND DOCUMENT EVENT
            doc_event = self._create_document_event(documents[doc_index], doc_index, total_docs)
            yield doc_event.model_dump()
            
            # 2. SEND MEMORY EVENT
            memory_data, should_crash = self.memory_monitor.calculate_memory(progress_percent)
            memory_event = MemoryEvent(data=memory_data)
            yield memory_event.model_dump()
            
            # 3. SEND PERFORMANCE EVENT (only if not using Ollama)
            # When using Ollama, performance metrics come from live LLM measurements during thought generation
            if not self.use_ollama:
                performance_metrics = self.performance_monitor.calculate_performance(
                    memory_data.unified_percent,
                    self.aidaptiv_enabled
                )
                performance_event = PerformanceEvent(data=PerformanceData(**performance_metrics))
                yield performance_event.model_dump()
            
            # 4. CHECK FOR CRASH
            if should_crash and not self.aidaptiv_enabled:
                crash_event = self._create_crash_event(
                    memory_data, 
                    progress_percent, 
                    "Out of unified memory - aiDAPTIV+ required for this workload"
                )
                yield crash_event.model_dump()
                return  # Stop simulation
            
            
            # 5. SEND THOUGHT EVENTS (LLM-based or canned)
            async for thought_event in self._generate_llm_thought(progress_percent):
                yield thought_event.model_dump()
            
            # 6. SEND METRIC UPDATES (periodically)
            if doc_index % max(1, total_docs // 10) == 0:  # Update every ~10%
                metric_events = self._create_metric_updates(progress_percent)
                for metric_event in metric_events:
                    yield metric_event.model_dump()
            
            # 6. WAIT FOR NEXT TICK
            async for event in self._wait_with_telemetry(interval):
                yield event

        
        # SIMULATION COMPLETE
        complete_event = self._create_complete_event(memory_data)
        yield complete_event.model_dump()
        
        # SEND IMPACT SUMMARY
        impact_summary = self._create_impact_summary(total_docs, memory_data, duration)
        yield impact_summary.model_dump()
    
    def _get_document_list(self) -> list[dict]:
        """Get list of documents for this scenario."""
        tier = self.config.tier
        docs = []
        
        if tier == "lite":
            # 3 competitors + 10 papers + 5 social
            for i in range(3):
                docs.append({"name": f"competitor_{chr(97+i)}.txt", "category": "competitor"})
            for i in range(10):
                docs.append({"name": f"arxiv_{i+1:03d}.txt", "category": "paper"})
            for i in range(5):
                docs.append({"name": f"social_signal_{i+1}.txt", "category": "social"})
        else:  # large
            # 12 competitors + 234 papers + 22 social
            for i in range(12):
                docs.append({"name": f"competitor_{chr(97+i)}.txt", "category": "competitor"})
            for i in range(234):
                docs.append({"name": f"arxiv_{i+1:03d}.txt", "category": "paper"})
            for i in range(22):
                docs.append({"name": f"social_signal_{i+1}.txt", "category": "social"})
        
        return docs
    
    def _create_document_event(self, doc: dict, index: int, total: int) -> DocumentEvent:
        """Create a document processing event."""
        return DocumentEvent(
            data=DocumentData(
                name=doc["name"],
                index=index,
                total=total,
                category=doc["category"],
                size_kb=doc.get("size_kb", 50.0)  # Default to 50KB if not provided
            )
        )
    
    def _check_and_create_thought(self, progress_percent: float) -> Optional[ThoughtEvent]:
        """Check if a thought should be sent at this progress point."""
        for phase_name, phase_data in THOUGHT_PHASES.items():
            trigger = phase_data["trigger_percent"]
            
            # Send thought if we've crossed the trigger and haven't sent it yet
            if progress_percent >= trigger and phase_name not in self.thoughts_sent:
                self.thoughts_sent.add(phase_name)
                
                # Skip memory_pressure thought if aiDAPTIV+ is disabled
                if phase_name == "memory_pressure" and not self.aidaptiv_enabled:
                    continue
                
                # Format text with dynamic values
                text = phase_data["text"].format(
                    visual_count=847 if self.config.tier == "large" else 151,
                    shifts=3 if self.config.tier == "large" else 2,
                    total_competitors=12 if self.config.tier == "large" else 3
                )
                
                return ThoughtEvent(
                    data=ThoughtData(
                        text=text,
                        status=phase_data["status"],
                        timestamp=datetime.utcnow().isoformat() + "Z",
                        step_type=phase_data.get("step_type", "thought"),
                        tools=phase_data.get("tools"),
                        related_doc_ids=phase_data.get("related_doc_ids")
                    )
                )
        
        return None
    
    async def _generate_llm_thought(self, progress_percent: float) -> AsyncGenerator[ThoughtEvent, None]:
        """
        Generate LLM-based thought for current progress using Ollama.
        Falls back to canned response if Ollama unavailable.
        
        Args:
            progress_percent: Current simulation progress
        
        Yields:
            ThoughtEvent objects with LLM-generated reasoning
        """
        # Find which phase we're in
        current_phase = None
        for phase_key, phase_data in ANALYSIS_PHASES.items():
            trigger = phase_data["trigger_percent"]
            if progress_percent >= trigger and phase_key not in self.thoughts_sent:
                current_phase = phase_key
                self.thoughts_sent.add(phase_key)
                break
        
        if not current_phase:
            return  # No phase to process
        
        # Use Ollama if available
        if self.use_ollama and self.ollama_service and self.ollama_context:
            try:
                # Check for model swap
                target_model = ANALYSIS_PHASES[current_phase].get("model", "llama3.1:8b")
                if target_model != self.current_model:
                     yield StatusEvent(message=f"Offloading Model: {self.current_model}...")
                     async for e in self._wait_with_telemetry(1.0): yield e # Visual pause with telemetry
                     yield StatusEvent(message=f"Loading Model: {target_model}...")
                     async for e in self._wait_with_telemetry(1.0): yield e # Visual pause with telemetry
                     self.current_model = target_model

                logger.info(f"Generating LLM thought for phase: {current_phase}")
                async for thought_text, performance_metrics in self.ollama_service.generate_reasoning(
                    self.ollama_context, 
                    current_phase
                ):
                    # Yield thought event
                    yield ThoughtEvent(
                        data=ThoughtData(
                            text=thought_text,
                            status="ANALYZING",
                            timestamp=datetime.utcnow().isoformat() + "Z",
                            step_type=ANALYSIS_PHASES[current_phase].get("step_type", "thought"),
                            tools=ANALYSIS_PHASES[current_phase].get("tools"),
                            related_doc_ids=ANALYSIS_PHASES[current_phase].get("related_doc_ids"),
                            author=ANALYSIS_PHASES[current_phase].get("author")
                        )
                    )
                    
                    # Yield live performance metrics from Ollama
                    yield PerformanceEvent(data=PerformanceData(**performance_metrics))
                    
                    # Throttle streaming for readability
                    await asyncio.sleep(config.THOUGHT_STREAM_DELAY)
            
            except Exception as e:
                logger.error(f"Error generating LLM thought: {e}")
                # Fall back to canned response
                canned_thought = self._check_and_create_thought(progress_percent)
                if canned_thought:
                    yield canned_thought
        else:
            # Use canned response
            canned_thought = self._check_and_create_thought(progress_percent)
            if canned_thought:
                yield canned_thought
    
    def _create_metric_updates(self, progress_percent: float) -> list[MetricEvent]:
        """Create metric update events based on progress."""
        events = []
        tier = self.config.tier
        
        # Calculate incremental values
        if tier == "lite":
            visual_target = 151
            papers_target = 12
            signals_target = 2
        else:
            visual_target = 974
            papers_target = 252
            signals_target = 5
        
        # Increment metrics proportionally
        visual_current = int(24 + (visual_target - 24) * (progress_percent / 100))
        papers_current = int(self.metrics["papers_analyzed"] + (papers_target - self.metrics["papers_analyzed"]) * (progress_percent / 100))
        
        # Signals jump at 80%
        signals_current = signals_target if progress_percent >= 80 else self.metrics["signals_detected"]
        
        # Update and create events
        if visual_current != self.metrics["visual_updates"]:
            self.metrics["visual_updates"] = visual_current
            events.append(MetricEvent(data=MetricData(name="visual_updates", value=visual_current)))
        
        if papers_current != self.metrics["papers_analyzed"]:
            self.metrics["papers_analyzed"] = papers_current
            events.append(MetricEvent(data=MetricData(name="papers_analyzed", value=papers_current)))
        
        if signals_current != self.metrics["signals_detected"]:
            self.metrics["signals_detected"] = signals_current
            events.append(MetricEvent(data=MetricData(name="signals_detected", value=signals_current)))
        
        return events
    
    def _create_crash_event(self, memory_data, progress, reason: str) -> CrashEvent:
        """Create a crash event."""
        # Calculate processed documents based on progress
        total_docs = 268 if self.config.tier == "large" else 18
        processed_docs = int(total_docs * (progress / 100))
        
        return CrashEvent(
            data=CrashData(
                reason=reason,
                memory_snapshot=memory_data,
                processed_documents=processed_docs,
                total_documents=total_docs,
                required_vram_gb=48.0 # Hardcoded estimate for large tier
            )
        )
    
    
    def _create_complete_event(self, memory_data) -> CompleteEvent:
        """Create analysis complete event."""
        tier = self.config.tier
        
        findings = FindingsData(
            shifts_detected=3 if tier == "large" else 2,
            evidence="5 UI patterns, 8 papers, 23 social signals" if tier == "large" else "3 UI patterns, 2 papers, 5 signals",
            recommendation="Expedited roadmap review required" if tier == "large" else "Monitor competitive landscape"
        )
        
        memory_stats = MemoryStatsData(
            unified_gb=memory_data.unified_gb,
            virtual_gb=memory_data.virtual_gb,
            total_gb=memory_data.unified_gb + memory_data.virtual_gb
        )
        
        return CompleteEvent(
            data=CompleteData(
                success=True,
                scenario=self.config.scenario,
                tier=self.config.tier,
                findings=findings,
                memory_stats=memory_stats
            )
        )
    
    def _create_impact_summary(self, total_docs: int, memory_data, duration_seconds: float) -> ImpactSummaryEvent:
        """Create impact summary event with analysis metrics."""
        # Calculate context size (rough estimate based on documents)
        avg_doc_size_mb = 0.05  # 50KB average
        context_size_gb = (total_docs * avg_doc_size_mb) / 1024
        
        # Calculate memory saved (offloaded to SSD)
        memory_saved_gb = memory_data.virtual_gb if memory_data.virtual_active else 0.0
        
        # Estimate costs
        estimated_cost_local = 0.0
        
        # Cloud GPU estimate
        if self.config.tier == "lite":
            estimated_cost_cloud = 0.10
            time_without_aidaptiv = duration_seconds / 60
        else:
            estimated_cost_cloud = 45.0
            time_without_aidaptiv = 15.0
        
        time_minutes = duration_seconds / 60
        
        return ImpactSummaryEvent(
            data=ImpactSummaryData(
                documents_processed=total_docs,
                total_documents=total_docs,
                context_size_gb=round(context_size_gb, 2),
                memory_saved_gb=round(memory_saved_gb, 2),
                estimated_cost_local=estimated_cost_local,
                estimated_cost_cloud=estimated_cost_cloud,
                estimated_monthly_cost=50.0 if self.config.tier == "lite" else 3200.0,
                time_minutes=round(time_minutes, 1),
                time_without_aidaptiv=time_without_aidaptiv
            )
        )
