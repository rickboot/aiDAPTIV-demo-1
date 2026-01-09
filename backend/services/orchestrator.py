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
from services.ollama_service import OllamaService, ANALYSIS_PHASES, ANALYSIS_PHASES_CES
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
    ),
    "ces2026_standard": ScenarioConfig(
        scenario="ces2026",
        tier="standard",
        duration_seconds=10,  # Fast for dev (set to 120 for demo)
        total_documents=21,   # 5 dossier + 10 news + 2 social + 3 video + 1 README
        memory_target_gb=14.0,  # Higher target due to video transcripts + dossiers
        crash_threshold_percent=None  # Won't crash - focused intelligence scenario
    )
}


# ═══════════════════════════════════════════════════════════════
# AI THOUGHT TEMPLATES
# ═══════════════════════════════════════════════════════════════

THOUGHT_PHASES_PMM = {
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

THOUGHT_PHASES_CES = {
    "loading": {
        "text": "Plan: Monitor CES 2026 keynote streams and competitive announcements",
        "status": "PROCESSING",
        "trigger_percent": 5,
        "step_type": "plan"
    },
    "analyzing": {
        "text": "Analyzing Samsung booth demo video - checking for PM9E1 references",
        "status": "ANALYZING",
        "trigger_percent": 20,
        "step_type": "thought",
        "related_doc_ids": ["samsung_booth_demo.txt", "pm9e1_specs.txt"]
    },
    "cross_ref": {
        "text": "Cross-referencing NVIDIA keynote transcript with phison_profile.txt",
        "status": "ACTIVE",
        "trigger_percent": 40,
        "step_type": "action",
        "tools": ["video_analysis", "rag_pipeline"]
    },
    "pattern": {
        "text": "Observation: Detected consistent 'AI on Device' messaging from Intel, AMD, and NVIDIA",
        "status": "ACTIVE",
        "trigger_percent": 60,
        "step_type": "observation"
    },
    "memory_pressure": {
        "text": "⚠️ Video transcript context size > 24GB - triggering aiDAPTIV+ offload",
        "status": "WARNING",
        "trigger_percent": 85,
        "step_type": "tool_use",
        "tools": ["memory_manager"]
    },
    "complete": {
        "text": "✅ Analysis complete: Samsung PM9E1 threat vector confirmed",
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
        # Metrics tracking
        self.metrics = {
            "key_topics": 0,
            "patterns_detected": 0,
            "insights_generated": 0,
            "critical_flags": 0
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
                    context_tokens = self.ollama_service.count_tokens(self.ollama_context)
                    logger.info(f"Loaded context: {len(self.ollama_context)} chars, ~{context_tokens} tokens")
                    
                    # Update memory monitor with context size
                    self.memory_monitor.set_context_size(context_tokens)
                    self.memory_monitor.set_model_size(self.current_model)
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
            memory_data, _ = self.memory_monitor.calculate_memory()
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
        
        # Send initialization event with all documents
        yield {
            "type": "init",
            "data": {
                "documents": documents,
                "total": total_docs
            }
        }
        
        for doc_index in range(total_docs):
            # Calculate current progress
            progress_percent = ((doc_index + 1) / total_docs) * 100
            self.current_progress = progress_percent
            
            # 1. SEND DOCUMENT EVENT
            doc_event = self._create_document_event(documents[doc_index], doc_index, total_docs)
            yield doc_event.model_dump()
            
            # 2. SEND MEMORY EVENT
            memory_data, should_crash = self.memory_monitor.calculate_memory()
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
                yield thought_event
                
                # Simulate context growth: each thought adds ~500-1000 tokens
                if thought_event.get('type') == 'thought':
                    thought_text = thought_event.get('data', {}).get('text', '')
                    # Rough estimate: 4 chars per token
                    tokens_added = len(thought_text) // 4
                    current_tokens = self.memory_monitor.context_tokens
                    self.memory_monitor.set_context_size(current_tokens + tokens_added)
            
            # Simulate context growth: each document adds to cumulative context
            # In real agentic systems, documents stay in context for future agents
            # Increase to 200 tokens per doc for dramatic growth (lite: 4.5K→8K, large: 8K→60K)
            doc_tokens = 200  # Aggressive growth to show KV cache pressure
            current_tokens = self.memory_monitor.context_tokens
            self.memory_monitor.set_context_size(current_tokens + doc_tokens)
            
            # 6. SEND METRIC UPDATES (periodically)
            if doc_index % max(1, total_docs // 10) == 0:  # Update every ~10%
                metric_events = self._create_metric_updates(progress_percent)
                for metric_event in metric_events:
                    yield metric_event.model_dump()
            
            # 7. WAIT FOR NEXT TICK
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
        scenario = self.config.scenario
        tier = self.config.tier
        docs = []
        
        if scenario == "ces2026":
            # Read actual files from documents/ces2026/
            ces_dir = Path("documents/ces2026")
            
            # 1. README (Core Instructions) - Load FIRST
            readme = ces_dir / "README.md"
            if readme.exists():
                size_kb = readme.stat().st_size / 1024
                docs.append({"name": readme.name, "category": "documentation", "size_kb": round(size_kb, 1)})
            
            # 2. Dossier files (Strategic Context) - Load SECOND
            for file in sorted((ces_dir / "dossier").glob("*.txt")):
                size_kb = file.stat().st_size / 1024
                docs.append({"name": file.name, "category": "dossier", "size_kb": round(size_kb, 1)})
            
            # 3. News files
            for file in sorted((ces_dir / "news").glob("*.txt")):
                size_kb = file.stat().st_size / 1024
                docs.append({"name": file.name, "category": "news", "size_kb": round(size_kb, 1)})
            
            # 4. Social files
            for file in sorted((ces_dir / "social").glob("*.txt")):
                size_kb = file.stat().st_size / 1024
                docs.append({"name": file.name, "category": "social", "size_kb": round(size_kb, 1)})
            
            # 5. Video transcripts
            video_dir = ces_dir / "video"
            if video_dir.exists():
                for file in sorted(video_dir.glob("*.txt")):
                    size_kb = file.stat().st_size / 1024
                    docs.append({"name": file.name, "category": "video", "size_kb": round(size_kb, 1)})
                
        elif tier == "lite":
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
    
    async def _check_and_create_thought(self, progress_percent: float) -> Optional[ThoughtEvent]:
        """Check if a thought should be sent at this progress point."""
        # Select phases based on scenario
        phases = THOUGHT_PHASES_CES if self.config.scenario == "ces2026" else THOUGHT_PHASES_PMM
        
        for phase_name, phase_data in phases.items():
            trigger = phase_data["trigger_percent"]
            
            # Send thought if we've crossed the trigger and haven't sent it yet
            if progress_percent >= trigger and phase_name not in self.thoughts_sent:
                self.thoughts_sent.add(phase_name)
                
                # Skip memory_pressure thought if aiDAPTIV+ is disabled
                if phase_name == "memory_pressure" and not self.aidaptiv_enabled:
                    continue
                
                # Format text with dynamic values (safe get for optional params)
                text = phase_data["text"]
                if self.config.scenario == "pmm":
                    text = text.format(
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
        # Select phases based on scenario
        phases = ANALYSIS_PHASES_CES if self.config.scenario == "ces2026" else ANALYSIS_PHASES
        
        # Find which phase we're in
        current_phase = None
        for phase_key, phase_data in phases.items():
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
                val_phase = phases[current_phase] # Use the selected phases dict
                target_model = val_phase.get("model", "llama3.1:8b")
                if target_model != self.current_model:
                     yield StatusEvent(message=f"Offloading Model: {self.current_model}...").model_dump()
                     await asyncio.sleep(2.0)  # Pause for offload
                     
                     yield StatusEvent(message=f"Loading Model: {target_model}...").model_dump()
                     # WebSocket's continuous monitor will show memory changes during load
                     
                     self.current_model = target_model
                     # Update memory monitor with new model size
                     self.memory_monitor.set_model_size(target_model)

                logger.info(f"Generating LLM thought for phase: {current_phase}")
                async for thought_text, performance_metrics in self.ollama_service.generate_reasoning(
                    self.ollama_context, 
                    current_phase,
                    scenario=self.config.scenario # Pass scenario to service
                ):
                    # Yield thought event
                    yield ThoughtEvent(
                        data=ThoughtData(
                            text=thought_text,
                            status="ANALYZING",
                            timestamp=datetime.utcnow().isoformat() + "Z",
                            step_type=val_phase.get("step_type", "thought"),
                            tools=val_phase.get("tools"),
                            related_doc_ids=val_phase.get("related_doc_ids"),
                            author=val_phase.get("author")
                        )
                    ).model_dump()
                    
                    # Yield live performance metrics from Ollama
                    yield PerformanceEvent(data=PerformanceData(**performance_metrics)).model_dump()
                    
                    # Throttle streaming for readability
                    await asyncio.sleep(config.THOUGHT_STREAM_DELAY)
            
            except Exception as e:
                logger.error(f"Error generating LLM thought: {e}")
                # Fall back to canned response
                canned_thought = self._check_and_create_thought(progress_percent)
                if canned_thought:
                    yield canned_thought.model_dump()
        else:
            # Use canned response
            canned_thought = self._check_and_create_thought(progress_percent)
            if canned_thought:
                yield canned_thought.model_dump()
    
    def _create_metric_updates(self, progress_percent: float) -> list[MetricEvent]:
        """Create metric update events based on progress."""
        events = []
        tier = self.config.tier
        
        # Calculate incremental values
        if tier == "lite":
            topics_target = 150
            patterns_target = 45
            insights_target = 12
            flags_target = 3
        else:
            topics_target = 2500
            patterns_target = 800
            insights_target = 300
            flags_target = 25
        
        # Increment metrics proportionally
        topics_current = int(topics_target * (progress_percent / 100))
        patterns_current = int(patterns_target * (progress_percent / 100))
        insights_current = int(insights_target * (progress_percent / 100))
        
        # Flags jump at 80%
        flags_current = flags_target if progress_percent >= 80 else int(flags_target * 0.2)
        
        # Update and create events
        if topics_current != self.metrics.get("key_topics", 0):
            self.metrics["key_topics"] = topics_current
            events.append(MetricEvent(data=MetricData(name="key_topics", value=topics_current)))

        if patterns_current != self.metrics.get("patterns_detected", 0):
            self.metrics["patterns_detected"] = patterns_current
            events.append(MetricEvent(data=MetricData(name="patterns_detected", value=patterns_current)))
        
        if insights_current != self.metrics.get("insights_generated", 0):
            self.metrics["insights_generated"] = insights_current
            events.append(MetricEvent(data=MetricData(name="insights_generated", value=insights_current)))
        
        if flags_current != self.metrics.get("critical_flags", 0):
            self.metrics["critical_flags"] = flags_current
            events.append(MetricEvent(data=MetricData(name="critical_flags", value=flags_current)))
        
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
