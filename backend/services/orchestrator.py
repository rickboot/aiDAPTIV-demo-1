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
    DocumentData, DocumentStatusEvent, MetricEvent, MetricData, CompleteEvent, CompleteData,
    CrashEvent, CrashData, FindingsData, MemoryStatsData, PerformanceEvent, PerformanceData,
    ImpactSummaryEvent, ImpactSummaryData, StatusEvent,
    RAGStorageEvent, RAGStorageData, RAGRetrievalEvent, RAGRetrievalData
)
from services.memory_monitor import MemoryMonitor
from services.performance_monitor import PerformanceMonitor
from services.ollama_service import OllamaService, ANALYSIS_PHASES, ANALYSIS_PHASES_CES
from services.memory_tier_manager import MemoryTierManager
from services.context_manager import ContextManager
from services.session_manager import SessionManager
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
        total_documents=87,   # 2 dossier + 60 news + 20 social + 3 video + 3 images + 1 README (all local inputs included)
        memory_target_gb=14.0,  # Higher target due to video transcripts + dossiers
        crash_threshold_percent=None  # Won't crash - focused intelligence scenario
    )
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
        self.doc_dir = Path(__file__).parent.parent.parent / "data" / "realstatic" / scenario
        
        # Metrics tracking
        self.metrics = {
            "key_topics": 0,
            "patterns_detected": 0,
            "insights_generated": 0,
            "critical_flags": 0
        }
        
        # Track unique items to avoid double counting
        self.unique_topics = set()
        self.unique_patterns = set()
        self.unique_insights = set()
        self.unique_flags = set()
        
        # Token tracking for TCO/billing (separate from memory usage)
        self.cumulative_input_tokens = 0
        self.cumulative_output_tokens = 0
        
        # Thought phase tracking
        self.thoughts_sent = set()
        
        # Multi-modal services
        self.memory_tier_manager = MemoryTierManager()
        self.current_tier = self.memory_tier_manager.detect_tier(aidaptiv_enabled)
            
        # Persistent state
        self.context_manager = ContextManager()
        self.session_manager = SessionManager()
        
        # Load accumulated metrics
        saved_metrics = self.session_manager.load_metrics()
        # Initialize if not present in saved metrics, otherwise use saved values or start at 0
        self.cumulative_input_tokens = saved_metrics.get("cumulative_input_tokens", 0)
        self.cumulative_output_tokens = saved_metrics.get("cumulative_output_tokens", 0)
        
        # Load persistent active context
        context_state_path = self.session_manager.data_dir / "context_state.json"
        self.context_manager.load_state(context_state_path)
        
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
                logger.error("Then ensure models are available: ollama pull llama3.1:8b && ollama pull llava:13b && ollama pull qwen2.5:14b")
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

        # Clear Ollama KV cache and context before starting analysis
        # Do this BEFORE sending init event so cache is cleared before memory events start flowing
        if self.use_ollama and self.ollama_service:
            try:
                logger.info("Clearing Ollama KV cache and context before analysis...")
                cleared = self.ollama_service.clear_model_cache()
                if cleared:
                    logger.info("Ollama cache cleared successfully - waiting for model to unload...")
                    # Give Ollama a moment to unload the model and clear cache
                    await asyncio.sleep(0.5)
                else:
                    logger.warning("Ollama cache clear returned False")
            except Exception as e:
                logger.warning(f"Failed to clear Ollama cache (non-fatal): {e}")
        
        # Reset memory monitor's context tracking to ensure clean state
        # This clears any context_tokens that were set during document loading
        if hasattr(self, 'memory_monitor'):
            self.memory_monitor.set_context_size(0)
            logger.info("Reset memory monitor context size to 0 (cleared stale values from document loading)")
        
        # Reset context_manager's token count to ensure clean state
        # This clears any tokens that were loaded from previous session state
        if hasattr(self, 'context_manager'):
            self.context_manager.total_tokens = 0
            self.context_manager.active_documents = []
            logger.info("Reset context_manager to clean state (cleared tokens from previous session)")
        
        # Get document list first to get actual count
        documents = self._get_document_list()
        actual_total_docs = len(documents)
        
        # Use actual count if different from config (config is approximate)
        total_docs = actual_total_docs if actual_total_docs > 0 else self.config.total_documents
        duration = self.config.duration_seconds
        interval = duration / total_docs  # Time per document
        
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
                elif current_doc['category'] == 'documentation' and 'transcript' in current_doc.get('name', '').lower():
                    yield {"type": "status", "message": "Processing Video Transcripts..."}
            
            # Calculate current progress
            progress_percent = ((doc_index + 1) / total_docs) * 100
            self.current_progress = progress_percent
            
            # 1. SEND DOCUMENT EVENT (Start Processing)
            # This puts the document in "Processing" (Blue) state in UI
            doc_event = self._create_document_event(current_doc, doc_index, total_docs)
            yield doc_event.model_dump()
            
            # Send explicit status update
            yield DocumentStatusEvent(data={"index": doc_index, "status": "processing"}).model_dump()
            
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
            elif current_doc['category'] == 'documentation' and 'transcript' in current_doc.get('name', '').lower():  # Process video transcripts individually
                is_batch_complete = True
            elif docs_in_current_batch >= 4: # Granular processing to prevent signal loss
                is_batch_complete = True
            
            if is_batch_complete:
                batch_size = docs_in_current_batch # Store for later loop
                logger.info(f"Triggering Agent Cycle. Documents in batch: {batch_size}, Category: {current_doc['category']}")
                docs_in_current_batch = 0
                
                # Yield status update
                yield StatusEvent(message=f"Analyzing {current_doc['category']} data...").model_dump()
                
                # Run the Agent Cycle for this category
                # Pass batch info so agent can mark documents green at the right time
                async for agent_event in self._run_agent_cycle(
                    current_doc['category'], 
                    current_doc,
                    batch_size=batch_size,
                    doc_index=doc_index
                ):
                    yield agent_event

            
            # 6. METRICS are yielded directly from the agent cycle based on LLM output tags
            
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
        # Video transcripts are now categorized as 'documentation', handled above
        # Real video files would use vision model, but we only have text transcripts
        else:
            # Default text model for everything else
            return tier_models.get('text_analysis', 'llama3.1:8b')

    async def _run_agent_cycle(self, category: str, current_doc: dict = None, batch_size: int = 1, doc_index: int = 0) -> AsyncGenerator[dict, None]:
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
        
        # Add metric instruction to the system prompt
        metric_instruction = (
            "\n\nIMPORTANT: Embed findings naturally in your analysis using these tags WITHIN sentences:\n"
            "As you analyze, you MUST strictly tag key findings using this format:\n"
            "- [TOPIC: <Entity Name>] for companies, products, or technologies mentioned.\n"
            "- [PATTERN: <Short Description>] for recurring trends or design shifts.\n"
            "- [INSIGHT: <Short Description>] for actionable conclusions or value judgments.\n"
            "- [FLAG: <Urgent Issue>] for critical risks, bottlenecks, or warnings.\n"
            "Example output: 'I noticed [TOPIC: Samsung] is releasing a new controller. This indicates a [PATTERN: monolithic design] shift. [INSIGHT: Vertical integration is key].'"
        )
        
        virtual_pmm_identity = self.sgp_loader.build_system_prompt(focus="competitive_intel") + metric_instruction

        default_model = await self._get_model_for_category(category, current_doc)

        if category == 'dossier':
            steps = [
                {
                    "type": "thought",
                    "prompt": f"""DATA SOURCE: {current_doc.get('name', 'Unknown')}

TASK: Analyze these competitor dossiers and identify specific technical weaknesses and attack vectors.

NOTE: Kioxia is a NAND supplier and strategic partner (not a competitor). Focus analysis on actual competitors only.

OUTPUT FORMAT (you MUST fill in all sections with specific details):

## Analysis of Competitor Dossiers

[Brief 1-2 sentence summary of the overall competitive landscape]

## Competitor Weaknesses:

- [Specific technical weakness #1 with details from dossier]
- [Specific technical weakness #2 with details from dossier]

## Attack Vector:

[2-3 sentence explanation of how aiDAPTIV+ can exploit these weaknesses]

By:
- [Specific action/strategy #1]
- [Specific action/strategy #2]

[1-2 sentences explaining how this creates competitive advantage]

## Recommendations:

- [Specific recommendation #1]
- [Specific recommendation #2]
- [Specific recommendation #3]

CRITICAL: You MUST provide specific details, technical facts, and concrete examples from the dossier content. Do NOT leave bullet points empty. Every bullet must contain substantive analysis.""",
                    "system": virtual_pmm_identity,
                    "author": "@Virtual_PMM"
                }
            ]
        elif category == 'news':
            steps = [
                {
                    "type": "thought",
                    "prompt": f"DATA SOURCE: {current_doc.get('name', 'Unknown')}\n\nTASK: Analyze this news article and organize insights by topic.\n\nOUTPUT FORMAT:\n## Topic: [Primary Topic]\n**Source:** [Company/Organization from article]\n**Key Points:**\n- [Specific insight with numbers/quotes]\n- [Another insight]\n\n## Topic: [Secondary Topic]\n**Source:** [Company/Organization]\n**Key Points:**\n- [Specific insight]\n\nQUESTION: What does this mean for aiDAPTIV+? Does it validate our thesis? Create opportunity? Reveal threats?\nOUTPUT: Strategic analysis organized by topic with specific examples, numbers, and quotes. Always call out the source company/organization.",
                    "system": virtual_pmm_identity,
                    "author": "@Virtual_PMM"
                }
            ]
        elif category == 'documentation' and 'transcript' in current_doc.get('name', '').lower():
            steps = [
                {
                    "type": "observation",
                    "prompt": f"DATA SOURCE: {current_doc.get('name', 'Unknown')}\n\nTASK: Identify 'Market Wedges' for aiDAPTIV+ in this transcript.\n\n1. **Memory Wall:** Where do they admit that HBM/VRAM is expensive, scarce, or power-hungry?\n2. **Edge Gap:** Find evidence that local hardware (even RTX 5090) cannot run frontier models (70B+) without help.\n3. **Actionable Intel:** Extract specific VRAM numbers or model sizes that prove the need for SSD offloading.\n\nOUTPUT: Strategic validation signals for the PMM team.",
                    "system": virtual_pmm_identity,
                    "author": "@Virtual_PMM"
                }
            ]
        elif category == 'image':
            steps = [
                {
                    "type": "observation",
                    "prompt": f"DATA SOURCE: {current_doc.get('name', 'Unknown')}\n\nExtract key intel in 3-4 bullet points:\n• Memory specs (DRAM/HBM amounts, bandwidth)\n• What fails on these specs? (e.g., Llama-3-70B needs 40GB)\n• Opportunity for aiDAPTIV+\n\nBe ultra-concise. Numbers only. No fluff.",
                    "system": virtual_pmm_identity,
                    "author": "@Visual_Intel",
                    "model": default_model # Use the vision model
                }
            ]
        elif category == 'social':
            # Extract Reddit metadata for context
            doc_metadata = current_doc.get('metadata', {})
            subreddit = doc_metadata.get('subreddit', 'unknown')
            author = doc_metadata.get('author', 'unknown')
            upvotes = doc_metadata.get('upvotes', 0)
            comments = doc_metadata.get('comments', 0)
            
            steps = [
                {
                    "type": "observation",
                    "prompt": f"""DATA SOURCE: {current_doc.get('name', 'Unknown')}
SUBREDDIT: r/{subreddit}
USER: u/{author}
ENGAGEMENT: {upvotes} upvotes, {comments} comments

TASK: Analyze this Reddit post. Extract 2-3 key topics. For each topic, provide:
1. Topic name
2. Subreddit (r/{subreddit})
3. User (u/{author})
4. 2-3 specific bullet points

CRITICAL: You MUST use double newlines between sections. Each topic must be separated by TWO blank lines.

OUTPUT FORMAT (copy this exact structure):

## Topic: [Topic Name]

**Subreddit:** r/{subreddit}

**User:** u/{author}

**Key Points:**

- [First specific insight]
- [Second specific insight]
- [Third insight if relevant]


## Topic: [Next Topic Name]

**Subreddit:** r/{subreddit}

**User:** u/{author}

**Key Points:**

- [First insight]
- [Second insight]


Focus on: Memory/VRAM constraints, AI/LLM challenges, hardware limitations, developer frustrations, solutions discussed.

IMPORTANT: Use double newlines (blank line) between each section. Do NOT write everything in one paragraph.""",
                    "system": virtual_pmm_identity,
                    "author": "@Virtual_PMM"
                }
            ]
        else:
            # Skip analysis for unknown categories or README
            return

        # Execute the steps
        
        # Add current doc to persistent context manager
        # Estimate tokens: ~1 token per 4 chars, or use rough size estimate 
        doc_text = current_doc.get('content', '') or current_doc.get('text', '')
        est_tokens = len(doc_text) // 4 if doc_text else int(current_doc.get('size_kb', 0) * 200)
        
        add_result = self.context_manager.add_document(current_doc, est_tokens)
        
        # Update memory monitor with actual context size from context manager
        # This ensures KV cache estimate reflects the actual growing context
        context_stats = self.context_manager.get_context_stats()
        actual_context_tokens = context_stats.get('active_tokens', 0)
        self.memory_monitor.set_context_size(actual_context_tokens)
        
        # Emit RAG storage event if document was stored
        if add_result.get("rag_storage"):
            rag_storage = add_result["rag_storage"]
            yield RAGStorageEvent(
                data=RAGStorageData(
                    document_name=rag_storage["document_name"],
                    document_category=rag_storage["document_category"],
                    tokens=rag_storage["tokens"],
                    total_documents_in_db=rag_storage["total_documents_in_db"],
                    timestamp=datetime.utcnow().isoformat()
                )
            ).model_dump()
        
        # Save context state to disk
        context_state_path = self.session_manager.data_dir / "context_state.json"
        self.context_manager.save_state(context_state_path)
        
        # Build context from CURRENT BATCH ONLY (not all accumulated documents)
        # This ensures LLM analyzes the specific document(s) being processed
        # For images: only the current image
        # For text batches: only the documents in this batch
        batch_documents = []
        for i in range(batch_size):
            batch_doc_index = doc_index - (batch_size - 1) + i
            if 0 <= batch_doc_index < len(self.processed_documents):
                batch_documents.append(self.processed_documents[batch_doc_index])
        
        # RAG: Retrieve relevant context from Vector DB to augment current batch
        rag_documents = []
        if batch_documents and self.context_manager.chroma_client:
            # Build query from current document(s) - use first doc's content as query
            # Extract key terms/topics for better semantic search
            query_text = ""
            batch_content_hashes = set()
            batch_ids = set()  # Track document IDs to exclude from retrieval
            
            for doc in batch_documents:
                doc_content = doc.get('content', '') or doc.get('text', '')
                if doc_content:
                    # Use first 500 chars as query (or full content if shorter)
                    if not query_text:
                        query_text = doc_content[:500] if len(doc_content) > 500 else doc_content
                    # Track content hashes to avoid duplicates
                    batch_content_hashes.add(hash(doc_content[:100]))  # Use first 100 chars as hash
                    # Track document name/ID to exclude from retrieval
                    doc_name = doc.get('name', '')
                    if doc_name:
                        batch_ids.add(doc_name.lower())
            
            if query_text:
                logger.info(f"RAG: Starting retrieval for document batch (query length: {len(query_text)} chars, excluding {len(batch_ids)} current docs)")
                try:
                    # Retrieve relevant documents from Vector DB
                    # Exclude current batch documents by title to avoid retrieving what we're already processing
                    retrieval_result = self.context_manager.retrieve_context(
                        query_text, 
                        max_tokens=3000,
                        exclude_titles=batch_ids
                    )
                    
                    # Handle new return format: (documents, retrieval_info) or just documents
                    if isinstance(retrieval_result, tuple):
                        retrieved, retrieval_info = retrieval_result
                    else:
                        retrieved = retrieval_result
                        retrieval_info = None
                    
                    if retrieved:
                        logger.info(f"RAG: Retrieved {len(retrieved)} documents from Vector DB, filtering duplicates...")
                        # Convert retrieved docs to same format as batch_documents
                        # Filter out documents that are already in the current batch
                        for ret_doc in retrieved:
                            ret_content = ret_doc.get('content', '')
                            if ret_content:
                                # Check if this document is already in the batch
                                ret_hash = hash(ret_content[:100])
                                if ret_hash not in batch_content_hashes:
                                    rag_documents.append({
                                        'name': ret_doc.get('metadata', {}).get('title', 'Retrieved Document'),
                                        'category': ret_doc.get('metadata', {}).get('source', 'archive'),
                                        'content': ret_content,
                                        'size_kb': len(ret_content) / 1024
                                    })
                                    batch_content_hashes.add(ret_hash)  # Track to avoid duplicates in RAG results
                        logger.info(f"RAG: Added {len(rag_documents)} unique documents from Vector DB")
                        
                        # Emit RAG retrieval event
                        if retrieval_info:
                            yield RAGRetrievalEvent(
                                data=RAGRetrievalData(
                                    query_preview=retrieval_info["query_preview"],
                                    query_length=retrieval_info["query_length"],
                                    candidates_found=retrieval_info["candidates_found"],
                                    documents_retrieved=retrieval_info["documents_retrieved"],
                                    tokens_retrieved=retrieval_info["tokens_retrieved"],
                                    tokens_limit=retrieval_info["tokens_limit"],
                                    excluded_count=retrieval_info["excluded_count"],
                                    retrieved_document_names=retrieval_info["retrieved_document_names"],
                                    timestamp=datetime.utcnow().isoformat()
                                )
                            ).model_dump()
                    else:
                        logger.info(f"RAG: No documents retrieved from Vector DB (may be empty or no matches)")
                except Exception as e:
                    logger.warning(f"RAG retrieval failed: {e}, continuing without RAG")
        
        # Combine batch documents with RAG-retrieved documents
        all_documents = batch_documents + rag_documents
        dynamic_context = self.ollama_service.build_context(all_documents)
        
        if rag_documents:
            logger.info(f"Built context from {len(batch_documents)} batch + {len(rag_documents)} RAG documents")
        else:
            logger.info(f"Built context from {len(batch_documents)} batch documents (no RAG)")
        
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
                
                # Append metric reminder to the user prompt to ensure compliance
                step_prompt = step['prompt'] + "\n\nIMPORTANT: Embed tags naturally within your analysis: [TOPIC: name], [PATTERN: description], [INSIGHT: conclusion], [FLAG: issue]. Write clear, analytical prose that demonstrates deep understanding of the context."
                
                async for thought_text, metrics in self.ollama_service.generate_step(
                    context=dynamic_context,
                    system_prompt=step['system'],
                    user_prompt=step_prompt,
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
                     
                     # Save updated metrics to disk
                     self.session_manager.save_metrics(self.cumulative_input_tokens, self.cumulative_output_tokens)
                     
                     logger.info(f"Cumulative tokens for billing: {self.cumulative_input_tokens} input + {self.cumulative_output_tokens} output")
                     
                     yield ThoughtEvent(
                        data=ThoughtData(
                            text=thought_text,
                            status="COMPLETE",
                            timestamp=datetime.utcnow().isoformat() + "Z",
                            step_type=step['type'],
                            author=step['author'],
                            source=current_doc.get('name', 'Unknown')  # Show which document is being analyzed
                        )
                    ).model_dump()
                     
                     yield PerformanceEvent(data=PerformanceData(**metrics)).model_dump()
                     
                     # Extract and yield real metrics from thought text
                     # Primary Method: Regex
                     metric_events = self._extract_metrics(thought_text)
                     
                     # Fallback Method: Two-Pass LLM Extraction (if regex failed)
                     # Essential for Vision Models which ignore formatting instructions
                     if not metric_events and (step.get('model', '').startswith('llava') or "observation" in step['type']):
                         logger.info("Regex found no metrics. Triggering Two-Pass Extraction with Llama 3...")
                         metric_events = await self._analyze_text_for_metrics(thought_text)
                     
                     for me in metric_events:
                         yield me.model_dump()
                     
                     # Mark documents as analyzed AFTER yielding thought
                     # This ensures UI shows green AFTER reasoning appears
                     logger.info(f"🟢 Marking batch as analyzed: batch_size={batch_size}, doc_index={doc_index}")
                     for i in range(batch_size):
                         completed_index = doc_index - (batch_size - 1) + i
                         if completed_index >= 0 and completed_index <= doc_index:
                             logger.info(f"🟢 Sending vram status for doc {completed_index}")
                             yield DocumentStatusEvent(data={"index": completed_index, "status": "vram"}).model_dump()
                
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
    
    
    def _extract_metrics(self, text: str) -> list[MetricEvent]:
        """Extract metrics from tagged LLM output using regex."""
        import re
        events = []
        
        # Regex patterns for tags (Case Insensitive)
        flags = re.IGNORECASE
        patterns = {
            "key_topics": re.compile(r"\[TOPIC:\s*([^\]]+)\]", flags),
            "patterns_detected": re.compile(r"\[PATTERN:\s*([^\]]+)\]", flags),
            "insights_generated": re.compile(r"\[INSIGHT:\s*([^\]]+)\]", flags),
            "critical_flags": re.compile(r"\[FLAG:\s*([^\]]+)\]", flags)
        }
        
        found_any = False
        for metric_name, pattern in patterns.items():
            matches = pattern.findall(text)
            if matches:
                 logger.info(f"FOUND METRICS ({metric_name}): {matches}")
                 found_any = True
            
            for match in matches:
                value = match.strip()
                
                # Determine the correct unique set based on metric_name
                usage_set = None
                if metric_name == "key_topics":
                    usage_set = self.unique_topics
                elif metric_name == "patterns_detected":
                    usage_set = self.unique_patterns
                elif metric_name == "insights_generated":
                    usage_set = self.unique_insights
                elif metric_name == "critical_flags":
                    usage_set = self.unique_flags
                
                if usage_set is not None:
                    if value not in usage_set:
                        usage_set.add(value)
                        self.metrics[metric_name] += 1
                        events.append(MetricEvent(data=MetricData(name=metric_name, value=self.metrics[metric_name])))
        
        if not found_any:
            # Debug log to see why we missed it
            logger.debug(f"NO METRICS FOUND IN: {text[:50]}...")
            
        return events
    
    def _get_document_list(self) -> list[dict]:
        """Get list of documents for this scenario."""
        scenario = self.config.scenario
        tier = self.config.tier
        docs = []
        
        if scenario == "ces2026":
            ces_dir = Path(__file__).parent.parent.parent / "data" / "realstatic" / "ces2026"
            
            # 1. README (Core Instructions) - Load FIRST
            readme = ces_dir / "README.md"
            if readme.exists():
                content = readme.read_text(encoding='utf-8')
                size_kb = readme.stat().st_size / 1024
                docs.append({"name": readme.name, "category": "documentation", "size_kb": round(size_kb, 1), "content": content})
            
            # 2. Dossier files (Strategic Context) - Load SECOND (core context before live data)
            dossier_dir = ces_dir / "dossier"
            if dossier_dir.exists():
                # Exclude Samsung/Silicon Motion (SSD controllers, not direct competitors) and Kioxia (NAND supplier/partner, not competitor)
                excluded_dossiers = [
                    "samsung_competitive_dossier.txt",  # SSD controller, not direct competitor
                    "silicon_motion_competitive_dossier.txt",  # SSD controller, not direct competitor
                    "kioxia_partnership_dossier.txt"  # NAND supplier/partner, not competitor (competes with Micron/Samsung in NAND, not with Phison)
                ]
                for file in sorted(dossier_dir.glob("*.txt")):
                    if file.name in excluded_dossiers:
                        logger.info(f"Skipping dossier (not competitor): {file.name}")
                        continue
                    content = file.read_text(encoding='utf-8')
                    size_kb = file.stat().st_size / 1024
                    docs.append({"name": file.name, "category": "dossier", "size_kb": round(size_kb, 1), "content": content})
            
            # 3. LIVE REDDIT DATA - Load THIRD (after core context so analysis has strategic framework)
            if app_config.DATA_SOURCE_MODE in ["live", "hybrid"]:
                # Fetch live Reddit social signals AFTER core docs for better context
                try:
                    from services.data_source import get_data_source
                    live_source = get_data_source("live")
                    live_social = live_source.fetch_social(count=20)
                    if live_social:
                        logger.info(f"✅ Loaded {len(live_social)} live Reddit posts (after core context)")
                        docs.extend(live_social)
                except Exception as e:
                    logger.warning(f"Failed to fetch live Reddit signals: {e}")
                    if app_config.DATA_SOURCE_MODE == "hybrid":
                        logger.info("Falling back to file-based social signals")
            
            # 4. News files - Load from disk (pre-generated offline)
            news_dir = ces_dir / "news"
            if news_dir.exists():
                for file in sorted(news_dir.glob("*.txt")):
                    content = file.read_text(encoding='utf-8')
                    size_kb = file.stat().st_size / 1024
                    docs.append({"name": file.name, "category": "news", "size_kb": round(size_kb, 1), "content": content})
            
            # 5. Social files - Load from disk (only if not in live mode)
            social_dir = ces_dir / "social"
            if social_dir.exists():
                # In live mode, skip files (already have live Reddit). In hybrid/generated, include them.
                if app_config.DATA_SOURCE_MODE != "live":
                    for file in sorted(social_dir.glob("*.txt")):
                        content = file.read_text(encoding='utf-8')
                        size_kb = file.stat().st_size / 1024
                        docs.append({"name": file.name, "category": "social", "size_kb": round(size_kb, 1), "content": content})
            
            # 6. Image files - Load ALL images from all subdirectories
            images_dir = ces_dir / "images"
            if images_dir.exists():
                # Load from all subdirectories
                for subdir in ["infographics", "competitor_screenshots", "social_media"]:
                    subdir_path = images_dir / subdir
                    if subdir_path.exists():
                        # Support multiple image formats
                        for ext in ["*.png", "*.jpg", "*.jpeg", "*.PNG", "*.JPG", "*.JPEG"]:
                            for file in sorted(subdir_path.glob(ext)):
                                size_kb = file.stat().st_size / 1024
                                docs.append({
                                    "name": file.name,
                                    "category": "image",
                                    "size_kb": round(size_kb, 1),
                                    "path": str(file),
                                    "content": f"[Image: {file.name}]"
                                })
                # Also check root images directory for any loose images
                for ext in ["*.png", "*.jpg", "*.jpeg", "*.PNG", "*.JPG", "*.JPEG"]:
                    for file in sorted(images_dir.glob(ext)):
                        size_kb = file.stat().st_size / 1024
                        docs.append({
                            "name": file.name,
                            "category": "image",
                            "size_kb": round(size_kb, 1),
                            "path": str(file),
                            "content": f"[Image: {file.name}]"
                        })
            
            # 7. Video transcripts (categorized as documentation since they're text file transcripts)
            video_dir = ces_dir / "video"
            if video_dir.exists():
                for file in sorted(video_dir.glob("*.txt")):
                    content = file.read_text(encoding='utf-8')
                    size_kb = file.stat().st_size / 1024
                    docs.append({"name": file.name, "category": "documentation", "size_kb": round(size_kb, 1), "content": content})
        
        # Sort documents by priority for demo:
        # 1. README (core instructions)
        # 2. Dossier (core context/strategic framework)
        # 3. Live Reddit posts (after core context for better analysis)
        # 4. NVIDIA CES 2026 keynote transcript (user priority)
        # 5. Images (multi-modal demo)
        # 6. Video transcripts (documentation category)
        # 7. Everything else
        def get_priority(doc):
            # README gets highest priority
            if doc.get('category') == 'documentation':
                return 0
            # Dossier gets second priority (core context)
            elif doc.get('category') == 'dossier':
                return 1
            # Live Reddit posts get third priority (after core context)
            elif doc.get('source') == 'reddit':
                return 2
            # NVIDIA transcript gets fourth priority
            elif doc.get('name') == 'nvidia_CES_2026_keynote_transcript.txt':
                return 3
            elif doc['category'] == 'image':
                return 4
            elif doc['category'] == 'documentation' and 'transcript' in doc.get('name', '').lower():
                return 5
            else:
                return 6
        
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
    
    async def _analyze_text_for_metrics(self, text: str) -> list[MetricEvent]:
        """
        Two-Pass Extraction: Ask a small LLM to extract metrics from the analysis text.
        Robust fallback for vision models.
        """
        if not self.use_ollama or not self.ollama_service:
            return []
            
        extraction_prompt = (
            f"Analyze the following observation and extract key entities and insights.\n"
            f"TEXT: \"{text}\"\n\n"
            f"INSTRUCTIONS:\n"
            f"Output ONLY tags in this format:\n"
            f"- [TOPIC: <Entity Name>]\n"
            f"- [PATTERN: <Trend>]\n"
            f"- [INSIGHT: <Conclusion>]\n"
            f"- [FLAG: <Warning>]\n"
            f"If nothing relevant is found, output: [INSIGHT: Routine analysis]"
        )
        
        # Use fast model for extraction
        try:
            # We use a non-streaming call here (simulated by iterating the generator)
            response_text = ""
            async for chunk, _ in self.ollama_service.generate_step(
                context="",
                system_prompt="You are a data extraction engine. Output strictly formatted tags.",
                user_prompt=extraction_prompt,
                model="llama3.1:8b" # Always use the text model for extraction
            ):
                response_text += chunk
            
            logger.info(f"Two-Pass Extraction Result: {response_text}")
            return self._extract_metrics(response_text)
            
        except Exception as e:
            logger.error(f"Two-Pass Extraction failed: {e}")
            return []
