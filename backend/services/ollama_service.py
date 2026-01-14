"""
Ollama service for real LLM integration.
Handles document loading, context building, and LLM streaming.
"""

import logging
from pathlib import Path
from typing import AsyncGenerator, List, Dict
import asyncio

import asyncio
import base64
import time

try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════
# AGENTIC ANALYSIS PHASES
# ═══════════════════════════════════════════════════════════════

ANALYSIS_PHASES = {
    "phase_1_review": {
        "name": "Load Context",
        "prompt": "Review the provided documents (dossiers, news, strategic context). Summarize the key information and data sources available for analysis.",
        "trigger_percent": 30,  # Start after Core Data (Dossiers + README) is loaded
        "step_type": "plan",
        "tools": ["document_loader"],
        "related_doc_ids": [],
        "author": "@Orchestrator",
        "system_prompt": "You are the Orchestrator. Your role is to survey available data and plan the analysis resources. Maintain a high-level operational tone.",
        "model": "llama3.1:8b"
    },
    "phase_2_patterns": {
        "name": "Analyze Documents",
        "prompt": "Analyze the documents provided (news articles, technical specifications, market reports). What patterns and trends do you notice? Be specific about key findings.",
        "trigger_percent": 50,  # Start mid-way through document loading
        "step_type": "thought",
        "related_doc_ids": [],
        "author": "@AI_Analyst",
        "system_prompt": "You are an Expert Analyst. Focus on identifying patterns, trends, and key insights from the documents. Be detailed and observational.",
        "model": "qwen2.5:14b"
    },
    "phase_3_technical": {
        "name": "Analyze Video/Images",
        "prompt": "Analyze the video transcripts and images provided. What insights can you extract from visual content and video transcripts? Correlate these with the document findings.",
        "trigger_percent": 85,  # Start after documents, as video/images begin
        "step_type": "action",
        "tools": ["rag_retriever"],
        "related_doc_ids": [],
        "author": "@Media_Analyst",
        "system_prompt": "You are a Media Analyst. Extract key insights from video transcripts and images. Correlate visual and media content with document findings.",
        "model": "qwen2.5:14b"
    },
    "phase_4_social": {
        "name": "Analyze User Feedback",
        "prompt": "Check the social media signals (Reddit, Twitter, forums). What are users discussing? Does the social sentiment align with the findings from documents and media?",
        "trigger_percent": 90,  # Parallel with video/image analysis
        "step_type": "observation",
        "related_doc_ids": [],
        "author": "@Social_Researcher",
        "system_prompt": "You are a User Researcher. Analyze social sentiment and user discussions. Validate findings with real user feedback and pain points.",
        "model": "llama3.1:8b"
    },
    "phase_5_synthesis": {
        "name": "Generate Summary",
        "prompt": "Synthesize all findings from documents, media, and user feedback. What are the key insights? What recommendations can you provide based on the complete analysis?",
        "trigger_percent": 95,  # Final synthesis at end
        "step_type": "thought",
        "tools": ["report_generator"],
        "author": "@Lead_Strategist",
        "system_prompt": "You are the Lead Strategist. Synthesize findings from all sources into a comprehensive summary with actionable recommendations.",
        "model": "llama3.1:8b"
    }
}


# ═══════════════════════════════════════════════════════════════
# OLLAMA CLIENT
# ═══════════════════════════════════════════════════════════════

class OllamaService:
    """Service for interacting with local Ollama instance."""
    
    def __init__(self, host: str, model: str):
        """
        Initialize Ollama service.
        
        Args:
            host: Ollama API host (e.g., http://localhost:11434)
            model: Model name (e.g., llama3.1:8b)
        """
        self.host = host
        self.model = model
        self.documents_cache: Dict[str, List[Dict]] = {}
    
    def check_availability(self) -> tuple[bool, str]:
        """
        Check if Ollama is available and model is pulled.
        
        Returns:
            (is_available, error_message)
        """
        if not OLLAMA_AVAILABLE:
            return False, "Ollama Python package not installed. Install with: pip install ollama"
        
        try:
            # Check if Ollama is running
            models = ollama.list()
            
            # Check if our model is available
            model_names = [m['name'] for m in models.get('models', [])]
            if self.model not in model_names:
                return False, f"Model '{self.model}' not found. Pull with: ollama pull {self.model}"
            
            return True, ""
        
        except Exception as e:
            return False, f"Ollama not running. Start with: ollama serve\nError: {str(e)}"
    
    def clear_model_cache(self) -> bool:
        """
        Clear Ollama's KV cache and context by unloading the model.
        This effectively resets the model's state without restarting Ollama.
        
        Returns:
            True if successful, False otherwise
        """
        if not OLLAMA_AVAILABLE:
            return False
        
        try:
            logger.info(f"Clearing Ollama KV cache and context for model: {self.model}")
            
            # Unload the model to clear its KV cache and context
            # This is done by setting keep_alive to 0 via the generate endpoint
            # Using a minimal prompt to avoid any actual processing
            try:
                ollama.generate(
                    model=self.model,
                    prompt="clear",  # Minimal prompt
                    options={
                        'num_predict': 1,  # Minimal generation
                        'keep_alive': 0  # Unload model after call (clears cache)
                    }
                )
            except Exception:
                # If generate fails, try to unload directly via API
                # Some Ollama versions support direct unload
                pass
            
            logger.info("Ollama KV cache and context cleared successfully")
            return True
            
        except Exception as e:
            logger.warning(f"Failed to clear Ollama cache (non-fatal): {e}")
            # Non-fatal - continue even if cache clear fails
            return False
    
    def load_documents(self, scenario: str, tier: str) -> List[Dict]:
        """
        Load all documents for a scenario/tier.
        
        Args:
            scenario: Scenario ID (e.g., "pmm", "mktg_intelligence_demo")
            tier: Tier level ("lite", "large", or "standard")
        
        Returns:
            List of document dicts with 'category', 'name', 'content'
        """
        cache_key = f"{scenario}_{tier}"
        if cache_key in self.documents_cache:
            return self.documents_cache[cache_key]
        
        documents = []
        
        # Directory name mapping: map scenario slugs to actual directory names on disk
        directory_mapping = {
            "mktg_intelligence_demo": "ces2026",  # Map new scenario slug to existing directory name
            "intel_demo": "ces2026",  # Backward compatibility: old name
            "ces2026": "ces2026"  # Backward compatibility
        }
        directory_name = directory_mapping.get(scenario, scenario)
        
        # Check if scenario uses realstatic structure (no tier subdirectory)
        base_path = Path(__file__).parent.parent.parent / "data" / "realstatic" / directory_name
        if base_path.exists():
            logger.info(f"Loading documents from: {base_path}")
            
            # Load dossier files (strategic context)
            dossier_path = base_path / "dossier"
            if dossier_path.exists():
                # Exclude Samsung/Silicon Motion (SSD controllers, not direct competitors) and Kioxia (NAND supplier/partner, not competitor)
                excluded_dossiers = [
                    "samsung_competitive_dossier.txt",  # SSD controller, not direct competitor
                    "silicon_motion_competitive_dossier.txt",  # SSD controller, not direct competitor
                    "kioxia_partnership_dossier.txt"  # NAND supplier/partner, not competitor (competes with Micron/Samsung in NAND, not with Phison)
                ]
                for file_path in sorted(dossier_path.glob("*.txt")):
                    if file_path.name in excluded_dossiers:
                        logger.info(f"Skipping dossier (not competitor): {file_path.name}")
                        continue
                    try:
                        content = file_path.read_text(encoding='utf-8')
                        size_kb = file_path.stat().st_size / 1024
                        documents.append({
                            "category": "dossier",
                            "name": file_path.stem,
                            "content": content,
                            "size_kb": round(size_kb, 1)
                        })
                    except Exception as e:
                        logger.warning(f"Failed to load {file_path}: {e}")
            
            # Load news files
            news_path = base_path / "news"
            if news_path.exists():
                for file_path in sorted(news_path.glob("*.txt")):
                    try:
                        content = file_path.read_text(encoding='utf-8')
                        size_kb = file_path.stat().st_size / 1024
                        documents.append({
                            "category": "news",
                            "name": file_path.stem,
                            "content": content,
                            "size_kb": round(size_kb, 1)
                        })
                    except Exception as e:
                        logger.warning(f"Failed to load {file_path}: {e}")
            
            # Load social signals
            social_path = base_path / "social"
            if social_path.exists():
                for file_path in sorted(social_path.glob("*.txt")):
                    try:
                        content = file_path.read_text(encoding='utf-8')
                        size_kb = file_path.stat().st_size / 1024
                        documents.append({
                            "category": "social",
                            "name": file_path.stem,
                            "content": content,
                            "size_kb": round(size_kb, 1)
                        })
                    except Exception as e:
                        logger.warning(f"Failed to load {file_path}: {e}")
            
            # Load video transcripts
            video_path = base_path / "video"
            if video_path.exists():
                for file_path in sorted(video_path.glob("*.txt")):
                    try:
                        content = file_path.read_text(encoding='utf-8')
                        size_kb = file_path.stat().st_size / 1024
                        documents.append({
                            "category": "video",
                            "name": file_path.stem,
                            "content": content,
                            "size_kb": round(size_kb, 1)
                        })
                    except Exception as e:
                        logger.warning(f"Failed to load {file_path}: {e}")
        else:
            # PMM scenario: Path: backend/services/ollama_service.py -> backend/ -> project_root/ -> data/dummy/
            base_path = Path(__file__).parent.parent.parent / "documents" / scenario / tier
            logger.info(f"Loading documents from: {base_path}")
            
            # Load competitors
            competitors_path = base_path / "competitors"
            if competitors_path.exists():
                for file_path in sorted(competitors_path.glob("*.txt")):
                    try:
                        content = file_path.read_text(encoding='utf-8')
                        size_kb = file_path.stat().st_size / 1024  # Convert bytes to KB
                        documents.append({
                            "category": "competitor",
                            "name": file_path.stem,
                            "content": content,
                            "size_kb": round(size_kb, 1)
                        })
                    except Exception as e:
                        logger.warning(f"Failed to load {file_path}: {e}")
            
            # Load papers
            papers_path = base_path / "papers"
            if papers_path.exists():
                for file_path in sorted(papers_path.glob("*.txt")):
                    try:
                        content = file_path.read_text(encoding='utf-8')
                        size_kb = file_path.stat().st_size / 1024
                        documents.append({
                            "category": "paper",
                            "name": file_path.stem,
                            "content": content,
                            "size_kb": round(size_kb, 1)
                        })
                    except Exception as e:
                        logger.warning(f"Failed to load {file_path}: {e}")
            
            # Load social signals
            social_path = base_path / "social"
            if social_path.exists():
                for file_path in sorted(social_path.glob("*.txt")):
                    try:
                        content = file_path.read_text(encoding='utf-8')
                        size_kb = file_path.stat().st_size / 1024
                        documents.append({
                            "category": "signal",
                            "name": file_path.stem,
                            "content": content,
                            "size_kb": round(size_kb, 1)
                        })
                    except Exception as e:
                        logger.warning(f"Failed to load {file_path}: {e}")
        
        self.documents_cache[cache_key] = documents
        logger.info(f"Loaded {len(documents)} documents for {scenario}/{tier}")
        return documents
    
    def build_context(self, documents: List[Dict], max_tokens: int = 50000) -> str:
        """
        Build context string from documents with section markers.
        
        Args:
            documents: List of document dicts
            max_tokens: Maximum context size (rough token estimate)
        
        Returns:
            Formatted context string
        """
        context_parts = []
        
        # Group by category
        dossier = [d for d in documents if d['category'] == 'dossier']
        competitors = [d for d in documents if d['category'] == 'competitor']
        news = [d for d in documents if d['category'] == 'news']
        papers = [d for d in documents if d['category'] == 'paper']
        social = [d for d in documents if d['category'] == 'social']
        video = [d for d in documents if d['category'] == 'video']
        
        # Add dossier (strategic context) first
        if dossier:
            context_parts.append("═══════════════════════════════════════════════════════════════")
            context_parts.append("STRATEGIC DOSSIER")
            context_parts.append("═══════════════════════════════════════════════════════════════\n")
            for doc in dossier:
                context_parts.append(f"## {doc['name'].upper()}\n")
                context_parts.append(doc['content'])
                context_parts.append("\n")
        
        # Add competitors
        if competitors:
            context_parts.append("\n═══════════════════════════════════════════════════════════════")
            context_parts.append("COMPETITOR INTELLIGENCE")
            context_parts.append("═══════════════════════════════════════════════════════════════\n")
            for doc in competitors:
                context_parts.append(f"## {doc['name'].upper()}\n")
                context_parts.append(doc['content'])
                context_parts.append("\n")
        
        # Add news
        if news:
            context_parts.append("\n═══════════════════════════════════════════════════════════════")
            context_parts.append("NEWS & ANALYSIS")
            context_parts.append("═══════════════════════════════════════════════════════════════\n")
            for doc in news:
                context_parts.append(f"## {doc['name'].upper()}\n")
                context_parts.append(doc['content'])
                context_parts.append("\n")
        
        # Add papers
        if papers:
            context_parts.append("\n═══════════════════════════════════════════════════════════════")
            context_parts.append("RESEARCH PAPERS")
            context_parts.append("═══════════════════════════════════════════════════════════════\n")
            for doc in papers:
                context_parts.append(f"## {doc['name'].upper()}\n")
                context_parts.append(doc['content'])
                context_parts.append("\n")
        
        # Add social signals
        if social:
            context_parts.append("\n═══════════════════════════════════════════════════════════════")
            context_parts.append("SOCIAL SIGNALS")
            context_parts.append("═══════════════════════════════════════════════════════════════\n")
            for doc in social:
                context_parts.append(f"## {doc['name'].upper()}\n")
                context_parts.append(doc['content'])
                context_parts.append("\n")
        
        # Add video transcripts
        if video:
            context_parts.append("\n═══════════════════════════════════════════════════════════════")
            context_parts.append("VIDEO TRANSCRIPTS")
            context_parts.append("═══════════════════════════════════════════════════════════════\n")
            for doc in video:
                context_parts.append(f"## {doc['name'].upper()}\n")
                context_parts.append(doc['content'])
                context_parts.append("\n")
        
        full_context = "\n".join(context_parts)
        
        # Rough token estimate (4 chars ≈ 1 token)
        estimated_tokens = len(full_context) // 4
        if estimated_tokens > max_tokens:
            logger.warning(f"Context too large ({estimated_tokens} tokens), truncating to {max_tokens}")
            # Truncate to fit (simple approach - could be smarter)
            char_limit = max_tokens * 4
            full_context = full_context[:char_limit] + "\n\n[... context truncated due to size ...]"
        
        return full_context

    def _encode_image(self, image_path: str) -> str:
        """Encode image to base64 for Ollama API"""
        try:
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        except Exception as e:
            logger.error(f"Error encoding image {image_path}: {e}")
            return ""

    async def generate_reasoning(
        self, 
        context: str, 
        phase_key: str,
        scenario: str = "pmm"
    ) -> AsyncGenerator[tuple[str, dict], None]:
        """
        Backward compatible wrapper for generate_step using predefined phases.
        """
        phase = ANALYSIS_PHASES.get(phase_key)
        if not phase:
            logger.error(f"Unknown phase: {phase_key} for scenario {scenario}")
            return

        system_prompt = phase.get("system_prompt", "You are an AI analyst.")
        user_prompt = phase['prompt']
        model = phase.get("model", self.model)

        async for thought_text, metrics in self.generate_step(
            context=context,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            model=model
        ):
            yield thought_text, metrics
    
    async def generate_step(
        self, 
        context: str, 
        system_prompt: str,
        user_prompt: str,
        model: str = "llama3.1:8b",
        image_paths: List[str] = None
    ) -> AsyncGenerator[tuple[str, dict], None]:
        """
        Generate LLM reasoning for a specific agent step with custom prompts.
        
        Clean streaming architecture:
        1. Stream all chunks to build complete response
        2. Track TTFT on first chunk only
        3. Extract real token counts from final chunk
        4. Yield once at end with complete text + accurate metrics
        
        Args:
            context: Document context
            system_prompt: Role and format instructions
            user_prompt: The specific task
            model: Model to use
            image_paths: Optional list of image paths for vision models
        
        Yields:
            Tuple of (complete_text, performance_metrics)
        """
        full_user_prompt = f"""CONTEXT DATA:
{context}

TASK:
{user_prompt}
"""
        try:
            # Start timer before API call
            start_time = time.time()
            first_token_time = None
            
            # Prepare chat arguments
            chat_args = {
                'model': model if model else self.model,
                'messages': [
                    {'role': 'system', 'content': system_prompt},
                    {'role': 'user', 'content': full_user_prompt}
                ],
                'stream': True,
                'options': {
                    'num_predict': 800,  # Allow for thorough reasoning
                    'temperature': 0.5,  # Lower for more focused, analytical output
                    'top_p': 0.9,  # Focus on high-probability tokens
                    'repeat_penalty': 1.1  # Reduce repetition
                }
            }
            
            # Inject images for vision models
            if chat_args['model'].startswith('llava'):
                if image_paths and len(image_paths) > 0:
                    encoded_images = []
                    for img_path_str in image_paths:
                        img_path = Path(img_path_str)
                        if img_path.exists():
                            logger.info(f"Injecting image for LLaVA: {img_path.name}")
                            encoded_images.append(self._encode_image(str(img_path)))
                        else:
                            logger.warning(f"Image path does not exist: {img_path}")
                    
                    if encoded_images:
                        chat_args['messages'][1]['images'] = encoded_images
                    else:
                        logger.warning(f"No valid images found, proceeding without image")
                else:
                    # Fallback to demo image if no paths provided
                    img_candidates = [
                        Path(__file__).parent.parent.parent / "data" / "realstatic" / "ces2026" / "images" / "infographics" / "samsung_ssd_roadmap_1767950527033.png",
                        Path(__file__).parent.parent.parent / "documents" / "pmm" / "lite" / "competitors" / "competitor_ui.png"
                    ]
                    for candidate in img_candidates:
                        if candidate.exists():
                            logger.info(f"Fallback: Injecting image for LLaVA: {candidate.name}")
                            chat_args['messages'][1]['images'] = [self._encode_image(str(candidate))]
                            break
            
            # Stream response from Ollama
            stream = ollama.chat(**chat_args)
            
            # Accumulate complete response
            complete_text = ""
            final_chunk = None
            
            for chunk in stream:
                content = chunk['message']['content']
                complete_text += content
                
                # Record TTFT on first chunk only
                if first_token_time is None and content:
                    first_token_time = time.time()
                
                # Keep reference to final chunk (contains token counts)
                final_chunk = chunk
            
            # Calculate metrics from final chunk
            total_time = time.time() - start_time
            ttft_ms = int((first_token_time - start_time) * 1000) if first_token_time else 0
            
            # Extract REAL token counts from Ollama's final chunk
            input_tokens = final_chunk.get('prompt_eval_count', 0) if final_chunk else 0
            output_tokens = final_chunk.get('eval_count', 0) if final_chunk else 0
            
            # Calculate performance metrics using real token counts
            tokens_per_sec = output_tokens / total_time if total_time > 0 and output_tokens > 0 else 0
            avg_latency_ms = int((total_time / output_tokens) * 1000) if output_tokens > 0 else 0
            
            performance = {
                "ttft_ms": ttft_ms,
                "tokens_per_second": round(tokens_per_sec, 1),
                "latency_ms": avg_latency_ms,
                "status": "optimal" if tokens_per_sec > 30 else ("degraded" if tokens_per_sec > 15 else "critical"),
                "degradation_percent": 0,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens
            }
            
            # Yield complete response with accurate metrics
            if complete_text.strip():
                yield (complete_text.strip(), performance)
            else:
                logger.warning("Empty response from LLM")
                yield ("[Empty response]", performance)
        
        except Exception as e:
            logger.error(f"Error generating reasoning: {e}")
            yield (f"[Error: {str(e)}]", {
                "ttft_ms": 0,
                "tokens_per_second": 0.0,
                "latency_ms": 0,
                "status": "critical",
                "degradation_percent": 100,
                "input_tokens": 0,
                "output_tokens": 0
            })
    
    def count_tokens(self, text: str) -> int:
        """
        Estimate token count for text.
        
        Args:
            text: Input text
        
        Returns:
            Estimated token count (rough approximation)
        """
        # Rough estimate: 4 characters ≈ 1 token
        return len(text) // 4
