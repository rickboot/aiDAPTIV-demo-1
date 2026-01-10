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
from services.image_gen_service import ImageGenService
from services.memory_tier_manager import MemoryTierManager
from sgp_config.sgp_loader import SGPLoader
import config as app_config
import os

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
        
        # Base directory for documents
        self.doc_dir = Path(__file__).parent.parent.parent / "documents" / scenario
        
        # Metrics tracking
        self.metrics = {
            "key_topics": 0,
            "patterns_detected": 0,
            "insights_generated": 0,
            "critical_flags": 0
        }
        
        # Token tracking for TCO/billing (separate from memory usage)
        self.cumulative_input_tokens = 0
        self.cumulative_output_tokens = 0
        
        # Thought phase tracking
        self.thoughts_sent = set()
        
        # Multi-modal services
        self.memory_tier_manager = MemoryTierManager()
        self.current_tier = self.memory_tier_manager.detect_tier(aidaptiv_enabled)
        self.image_gen_service = None
        if self.current_tier == "pro":
            self.image_gen_service = ImageGenService()
        
        logger.info(f"Initialized with tier: {self.current_tier}, aiDAPTIV+: {aidaptiv_enabled}")
        
        # Load Semantic Grounding Profile
        sgp_path = Path(__file__).parent.parent / "sgp_config" / "sgp_aidaptiv_competitive_intel.json"
        self.sgp_loader = None
        if sgp_path.exists():
            try:
                self.sgp_loader = SGPLoader(str(sgp_path))
                logger.info(f"Loaded SGP: {self.sgp_loader.sgp.get('profile_name', 'Unknown')}")
            except Exception as e:
                logger.warning(f"Failed to load SGP: {e}")
        else:
            logger.warning(f"SGP file not found: {sgp_path}")
        
        # Ollama integration
        self.use_ollama = app_config.USE_REAL_OLLAMA
        self.ollama_service = None
        self.ollama_context = None
        
        # Performance monitoring
        self.performance_monitor = PerformanceMonitor()
        
        # Track active model to visualize swapping
        self.current_model = "llama3.1:8b"
        self.current_progress = 0.0
        
        if self.use_ollama:
            self.ollama_service = OllamaService(app_config.OLLAMA_HOST, app_config.OLLAMA_MODEL)
            available, error_msg = self.ollama_service.check_availability()
            if not available:
                error_message = f"Ollama is required but not available: {error_msg}"
                logger.error(error_message)
                logger.error("Start Ollama with: ollama serve")
                logger.error("Then ensure models are available: ollama pull llama3.1:8b && ollama pull llava:13b")
                raise RuntimeError(error_message)
            else:
                logger.info(f"Ollama enabled with model: {app_config.OLLAMA_MODEL}")
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
                    logger.error(f"Failed to load documents: {e}")
                    raise RuntimeError(f"Failed to initialize Ollama service: {e}")
        
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
        
        # Track processed documents for dynamic context
        self.processed_documents = []
        docs_in_current_batch = 0
        
        for doc_index in range(total_docs):
            current_doc = documents[doc_index]
            self.processed_documents.append(current_doc) # Add to timeline
            
            prev_doc = documents[doc_index - 1] if doc_index > 0 else None
            
            # Emit category transition status messages
            if prev_doc is None:
                # First document
                if current_doc['category'] == 'image':
                    yield {"type": "status", "message": "Loading image data for visual analysis..."}
                elif current_doc['category'] == 'dossier':
                    yield {"type": "status", "message": "Loading Strategic Dossiers..."}
                elif current_doc['category'] == 'news':
                    yield {"type": "status", "message": "Ingesting CES News Feed..."}
            elif prev_doc and current_doc['category'] != prev_doc['category']:
                if current_doc['category'] == 'image':
                    yield {"type": "status", "message": "Loading image data for visual analysis..."}
                elif current_doc['category'] == 'dossier':
                    yield {"type": "status", "message": "Loading Strategic Dossiers..."}
                elif current_doc['category'] == 'news':
                    yield {"type": "status", "message": "Ingesting CES News Feed..."}
                elif current_doc['category'] == 'social':
                    yield {"type": "status", "message": "Monitoring Social Channels..."}
                elif current_doc['category'] == 'video':
                    yield {"type": "status", "message": "Processing Video Transcripts..."}
            
            # Calculate current progress
            progress_percent = ((doc_index + 1) / total_docs) * 100
            self.current_progress = progress_percent
            
            # 1. SEND DOCUMENT EVENT
            doc_event = self._create_document_event(current_doc, doc_index, total_docs)
            yield doc_event.model_dump()
            
            # Context growth is now tracked from real LLM responses only (no simulation)
            # doc_tokens = 200
            # self.memory_monitor.set_context_size(self.memory_monitor.context_tokens + doc_tokens)
            
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
            
            
            # 5. CHECK FOR AGENT TRIGGER (Event-Driven)
            # Trigger when we finish a category (batch processing) OR every 4 documents
            next_doc = documents[doc_index + 1] if doc_index + 1 < total_docs else None
            docs_in_current_batch += 1
            
            is_batch_complete = False
            
            if next_doc is None: # Last doc
                is_batch_complete = True
            elif current_doc['category'] != next_doc['category']:
                is_batch_complete = True
            elif current_doc['category'] == 'image':  # Process images individually for llava
                is_batch_complete = True
            elif current_doc['category'] == 'video':  # Process video individually for vision
                is_batch_complete = True
            elif docs_in_current_batch >= 4: # Granular processing to prevent signal loss
                is_batch_complete = True
            
            if is_batch_complete:
                logger.info(f"Triggering Agent Cycle. Documents in batch: {docs_in_current_batch}, Category: {current_doc['category']}")
                docs_in_current_batch = 0
                
                # Yield status update
                yield StatusEvent(message=f"Analyzing {current_doc['category']} data...").model_dump()
                
                # Run the Agent Cycle for this category
                async for agent_event in self._run_agent_cycle(current_doc['category'], current_doc):
                    yield agent_event

            
            # 6. SEND METRIC UPDATES (periodically)
            if doc_index % max(1, total_docs // 10) == 0:  # Update every ~10%
                metric_events = self._create_metric_updates(progress_percent)
                for metric_event in metric_events:
                    yield metric_event.model_dump()
            
            # 7. WAIT FOR NEXT TICK (only if not about to run agent cycle)
            if not is_batch_complete:
                async for event in self._wait_with_telemetry(interval):
                    yield event

        
        # SIMULATION COMPLETE
        yield StatusEvent(message="Analysis Finalized").model_dump()
    
    # ... (helper methods) ...

    async def _get_model_for_category(self, category: str, doc: dict = None) -> str:
        """
        Get the appropriate model for a category based on current tier.
        Refinement: Treat text-based video transcripts as text analysis.
        """
        tier_models = self.memory_tier_manager.get_models_for_tier(self.current_tier)
        
        if category == 'image':
            # Pro: llava:34b, Standard: llava:13b
            return tier_models.get('image_analysis', 'llava:13b')
        elif category == 'video':
            # If it's a transcript (.txt), use text model. If it's a real video/frames, use vision.
            if doc and doc.get('name', '').lower().endswith('.txt'):
                return tier_models.get('text_analysis', 'llama3.1:8b')
            # Fallback to vision model for video category if not clearly a transcript
            return tier_models.get('video_analysis', tier_models.get('image_analysis', 'llava:13b'))
        else:
            # Default text model for everything else
            return tier_models.get('text_analysis', 'llama3.1:8b')

    async def _run_agent_cycle(self, category: str, current_doc: dict = None) -> AsyncGenerator[dict, None]:
        """
        Execute a multi-step Agent Reasoning Cycle based on the completed category.
        This simulates a real agent deciding what to do with new data.
        
        Args:
            category: Category of documents being processed
            current_doc: The current document being processed (for images, to get the path)
        """
        if not self.use_ollama or not self.ollama_service:
            return

        # Define the Agent's Workflow based on what just arrived
        steps = []
        
        # SGP is the authoritative source for agent grounding
        
        if not self.sgp_loader:
            logger.error("SGP not loaded - agent cannot operate without semantic grounding")
            raise RuntimeError("Semantic Grounding Profile is required but not loaded")
        
        virtual_pmm_identity = self.sgp_loader.build_system_prompt(focus="competitive_intel")

        default_model = await self._get_model_for_category(category, current_doc)

        if category == 'dossier':
            steps = [
                {
                    "type": "thought",
                    "prompt": "TASK: Analyze these competitor dossiers.\nQUESTION: What specific technical weaknesses do Samsung/Kioxia have that leave the door open for aiDAPTIV+?\nOUTPUT: The 'Attack Vector' we can use against them.",
                    "system": virtual_pmm_identity,
                    "author": "@Virtual_PMM"
                }
            ]
        elif category == 'news':
            steps = [
                {
                    "type": "thought",
                    "prompt": "TASK: Scan the current news batch for 'Validation Signals'.\nQUESTION: Connect NVIDIA's recent hardware moves with Intel's client constraints. Specifically, how does this validate the need for KV-cache offloading?\nOUTPUT: Strategic synthesis of the market wedge.",
                    "system": virtual_pmm_identity,
                    "author": "@Virtual_PMM"
                }
            ]
        elif category == 'video' or (category == 'documentation' and 'transcript' in current_doc.get('name', '').lower()):
            steps = [
                {
                    "type": "observation",
                    "prompt": "TASK: Extract 'Ground Truth' from these transcripts.\nQUESTION: Are they admitting to heat/power/memory limits? Find the apologies or excuses.\nOUTPUT: Verbatim quotes supporting the memory bottleneck thesis.",
                    "system": virtual_pmm_identity,
                    "author": "@Media_Analyst"
                }
            ]
        elif category == 'image':
            steps = [
                {
                    "type": "observation",
                    "prompt": "TASK: Analyze these visual materials (infographics, screenshots, booth photos).\nQUESTION: What are competitors claiming? What specs are they highlighting? What are they hiding?\nOUTPUT: Visual evidence of competitive positioning and technical claims.",
                    "system": virtual_pmm_identity,
                    "author": "@Visual_Intel",
                    "model": default_model # Use the vision model
                }
            ]
        elif category == 'social':
            steps = [
                {
                    "type": "observation",
                    "prompt": "TASK: Listen to the developer complaints.\nQUESTION: Are they crying about 'OOM' (Out of Memory)? Are they unable to run Llama-3-70B?\nOUTPUT: The 'Voice of the Customer' pain points that justify our existence.",
                    "system": virtual_pmm_identity,
                    "author": "@Virtual_PMM"
                }
            ]
        else:
            # Skip analysis for unknown categories or README
            return

        # Execute the steps
        dynamic_context = self.ollama_service.build_context(self.processed_documents)
        
        for step in steps:
            try:
                # Emit status update for model loading (if using a different model)
                step_model = step.get('model', default_model)
                if step_model != self.current_model:
                    yield StatusEvent(message=f"Swapping Model: {self.current_model} ➔ {step_model}...").model_dump()
                    
                    # Update model state
                    self.current_model = step_model
                    self.memory_monitor.set_model_size(step_model)
                    
                    # Force a memory update to show model weights in UI
                    memory_data, _ = self.memory_monitor.calculate_memory()
                    yield MemoryEvent(data=memory_data).model_dump()
                    
                    await asyncio.sleep(1.5)  # Pause to show loading status
                
                logger.info(f"Running Agent Step: {step['type']} with model {step_model}")
                
                # Collect image paths for llava (if processing images)
                image_paths = []
                if category == 'image' and current_doc and 'path' in current_doc:
                    image_paths.append(current_doc['path'])
                
                async for thought_text, metrics in self.ollama_service.generate_step(
                    context=dynamic_context,
                    system_prompt=step['system'],
                    user_prompt=step['prompt'],
                    model=step_model,
                    image_paths=image_paths if image_paths else None
                ):
                     # Log the content for monitoring
                     logger.info(f"AGENT THOUGHT ({step['type']}): {thought_text[:100]}...")
                     
                     # Track cumulative tokens for TCO/billing (separate from memory usage)
                     if 'input_tokens' in metrics:
                         self.cumulative_input_tokens += metrics['input_tokens']
                     if 'output_tokens' in metrics:
                         self.cumulative_output_tokens += metrics['output_tokens']
                     logger.info(f"Cumulative tokens for billing: {self.cumulative_input_tokens} input + {self.cumulative_output_tokens} output")
                     
                     yield ThoughtEvent(
                        data=ThoughtData(
                            text=thought_text,
                            status="COMPLETE",
                            timestamp=datetime.utcnow().isoformat() + "Z",
                            step_type=step['type'],
                            author=step['author']
                        )
                    ).model_dump()
                     
                     yield PerformanceEvent(data=PerformanceData(**metrics)).model_dump()
                
                # Short pause between steps
                await asyncio.sleep(0.5)

            except Exception as e:
                logger.error(f"Agent step failed: {e}")
                yield ThoughtEvent(
                    data=ThoughtData(
                        text=f"[Analysis Error: {str(e)}]",
                        status="ERROR",
                        timestamp=datetime.utcnow().isoformat() + "Z",
                        step_type=step['type'],
                        author=step['author']
                    )
                ).model_dump()
    
    
    def _get_document_list(self) -> list[dict]:
        """Get list of documents for this scenario."""
        scenario = self.config.scenario
        tier = self.config.tier
        docs = []
        
        if scenario == "ces2026":
            # Read actual files from documents/ces2026/
            # Path: backend/services/orchestrator.py -> backend/ -> project_root/ -> documents/
            ces_dir = Path(__file__).parent.parent.parent / "documents" / "ces2026"
            
            # 1. README (Core Instructions) - Load FIRST
            readme = ces_dir / "README.md"
            if readme.exists():
                content = readme.read_text(encoding='utf-8')
                size_kb = readme.stat().st_size / 1024
                docs.append({"name": readme.name, "category": "documentation", "size_kb": round(size_kb, 1), "content": content})
            
            # 2. Dossier files (Strategic Context) - Load SECOND
            for file in sorted((ces_dir / "dossier").glob("*.txt")):
                content = file.read_text(encoding='utf-8')
                size_kb = file.stat().st_size / 1024
                docs.append({"name": file.name, "category": "dossier", "size_kb": round(size_kb, 1), "content": content})
            
            # 3. News files
            for file in sorted((ces_dir / "news").glob("*.txt")):
                content = file.read_text(encoding='utf-8')
                size_kb = file.stat().st_size / 1024
                docs.append({"name": file.name, "category": "news", "size_kb": round(size_kb, 1), "content": content})
            
            # 4. Social files
            for file in sorted((ces_dir / "social").glob("*.txt")):
                content = file.read_text(encoding='utf-8')
                size_kb = file.stat().st_size / 1024
                docs.append({"name": file.name, "category": "social", "size_kb": round(size_kb, 1), "content": content})
            
            # 5. Image files (if tier supports it)
            if self.current_tier in ["standard", "pro"]:
                images_dir = ces_dir / "images"
                if images_dir.exists():
                    for subdir in ["infographics", "competitor_screenshots", "social_media"]:
                        subdir_path = images_dir / subdir
                        if subdir_path.exists():
                            for file in sorted(subdir_path.glob("*.png")):
                                size_kb = file.stat().st_size / 1024
                                docs.append({
                                    "name": file.name,
                                    "category": "image",
                                    "size_kb": round(size_kb, 1),
                                    "path": str(file),
                                    "content": f"[Image: {file.name}]"
                                })
            
            # 6. Video transcripts (categorized as documentation since they're text files)
            video_dir = ces_dir / "video"
            if video_dir.exists():
                for file in sorted(video_dir.glob("*.txt")):
                    content = file.read_text(encoding='utf-8')
                    size_kb = file.stat().st_size / 1024
                    docs.append({"name": file.name, "category": "video", "size_kb": round(size_kb, 1), "content": content})
        
        # Sort documents by priority for demo:
        # 1. Images (multi-modal demo - FIRST for dev speed)
        # 2. Dossier (core context)
        # 3. Videos (multi-modal demo)
        # 4. Everything else
        def get_priority(doc):
            if doc['category'] == 'image':
                return 0
            elif doc['category'] == 'dossier':
                return 1
            elif doc['category'] == 'video':
                return 2
            else:
                return 3
        
        docs.sort(key=get_priority)
        
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
        if self.use_ollama and self.ollama_service:
            try:
                # Build context DYNAMICALLY from processed documents only
                # This ensures the LLM can only "see" what has actually arrived in the simulation
                dynamic_context = self.ollama_service.build_context(self.processed_documents)
                
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
                     
                     # Force immediate update
                     memory_data, _ = self.memory_monitor.calculate_memory()
                     yield MemoryEvent(data=memory_data).model_dump()

                logger.info(f"Generating LLM thought for phase: {current_phase} with dynamic context")
                async for thought_text, performance_metrics in self.ollama_service.generate_reasoning(
                    dynamic_context, 
                    current_phase,
                    scenario=self.config.scenario # Pass scenario to service
                ):
                    # Track cumulative tokens for TCO/billing (separate from memory usage)
                    if 'input_tokens' in performance_metrics:
                        self.cumulative_input_tokens += performance_metrics['input_tokens']
                    if 'output_tokens' in performance_metrics:
                        self.cumulative_output_tokens += performance_metrics['output_tokens']
                    logger.info(f"Cumulative tokens for billing: {self.cumulative_input_tokens} input + {self.cumulative_output_tokens} output")
                    
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
                    await asyncio.sleep(app_config.THOUGHT_STREAM_DELAY)
            
            except Exception as e:
                logger.error(f"Error generating LLM thought: {e}")
                # Fall back to canned response
                canned_thought = await self._check_and_create_thought(progress_percent)
                if canned_thought:
                    yield canned_thought.model_dump()
        else:
            # Use canned response
            canned_thought = await self._check_and_create_thought(progress_percent)
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
    
