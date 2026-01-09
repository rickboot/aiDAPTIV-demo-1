"""
Ollama service for real LLM integration.
Handles document loading, context building, and LLM streaming.
"""

import logging
from pathlib import Path
from typing import AsyncGenerator, List, Dict
import asyncio

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
        "name": "Document Review",
        "prompt": "First, review the list of competitors, research papers, and social signals provided. Briefly summarize what data sources you have available for analysis.",
        "trigger_percent": 5,
        "step_type": "plan",
        "tools": ["document_loader"],
        "related_doc_ids": ["Comp_UI_1", "Comp_UI_2"],
        "author": "@Orchestrator",
        "system_prompt": "You are the Orchestrator. Your role is to survey available data and plan the analysis resources. maintain a high-level operational tone.",
        "model": "llama3.1:8b"
    },
    "phase_2_patterns": {
        "name": "Pattern Detection",
        "prompt": "Now analyze the competitor descriptions and UI changes. What patterns do you notice in their product interfaces and architectures? Be specific about which competitors show similar changes.",
        "trigger_percent": 15,  # Trigger earlier to ensure model swap happens
        "step_type": "thought",
        "related_doc_ids": ["Comp_UI_1", "Comp_UI_2", "Comp_Archive_X"],
        "author": "@AI_Analyst",
        "system_prompt": "You are an Expert UI Analyst. Focus strictly on visual patterns, interface elements, and user experience changes. Be detailed and observational.",
        "model": "qwen2.5:14b"
    },
    "phase_3_technical": {
        "name": "Technical Cross-Reference",
        "prompt": "Cross-reference the UI patterns you found with the technical research papers. Do any papers discuss agentic architectures, multi-agent systems, or autonomous workflows that align with what you're seeing in competitor products?",
        "trigger_percent": 50,
        "step_type": "action",
        "tools": ["rag_retriever"],
        "related_doc_ids": ["arXiv_2401.12847"],
        "author": "@Tech_Specialist",
        "system_prompt": "You are a Chief Software Architect. Focus on backend infrastructure, agentic frameworks, and technical feasibility. Ignore marketing fluff.",
        "model": "qwen2.5:14b"
    },
    "phase_4_social": {
        "name": "Social Signal Validation",
        "prompt": "Check the social media signals from CTOs and product leaders. Do their posts, blog articles, or conference talks corroborate your technical findings? What are they saying about AI agents and architecture shifts?",
        "trigger_percent": 70,
        "step_type": "observation",
        "related_doc_ids": ["Social_Signal_5", "Social_Signal_8"],
        "author": "@Market_Researcher",
        "system_prompt": "You are a Market Researcher. Analyze social sentiment, industry buzz, and thought leader opinions. Look for validation of technical trends.",
        "model": "llama3.1:8b"
    },
    "phase_5_synthesis": {
        "name": "Synthesis & Recommendations",
        "prompt": "Synthesize your findings. How many competitors show strong evidence of architectural shifts toward agentic systems? What's the strength of evidence (UI changes + papers + social signals)? What should our product team do in response?",
        "trigger_percent": 90,
        "step_type": "thought",
        "tools": ["report_generator"],
        "author": "@Lead_Strategist",
        "system_prompt": "You are the Lead Strategist. Synthesize findings from the analyst, architect, and researcher into a decisive executive recommendation. Be business-focused.",
        "model": "llama3.1:8b"
    }
}

ANALYSIS_PHASES_CES = {
    "phase_1_review": {
        "name": "Intelligence Briefing",
        "prompt": "Review the provided competitive dossiers (Samsung, Silicon Motion, Kioxia) and CES news. Summarize the key competitive threats identified in these documents.",
        "trigger_percent": 5,
        "step_type": "plan",
        "tools": ["dossier_analysis"],
        "related_doc_ids": ["samsung_competitive_dossier", "silicon_motion_dossier"],
        "author": "@Orchestrator",
        "system_prompt": "You are the Intelligence Orchestrator. Summarize the strategic landscape based on the dossiers. Be concise and threat-focused.",
        "model": "llama3.1:8b"
    },
    "phase_2_patterns": {
        "name": "Threat Vector Analysis",
        "prompt": "Analyze the technical specifications in the news (Intel, AMD, Samsung PM9E1). How do these hardware announcements impact the 'AI PC' memory bottleneck? Is there a pattern of on-device memory limitation?",
        "trigger_percent": 15,
        "step_type": "thought",
        "related_doc_ids": ["intel_core_ultra", "amd_ryzen_ai"],
        "author": "@Hardware_Analyst",
        "system_prompt": "You are a Hardware Architect. Analyze the specs. Look for memory constraints that validate our swappable model thesis.",
        "model": "qwen2.5:14b"
    },
    "phase_3_technical": {
        "name": "Video Signal Correlation",
        "prompt": "Correlate the video transcripts (NVIDIA Keynote, Linus Tech Tips) with the hardware trends. Are industry leaders (Jensen Huang, Linus) explicitly talking about the memory wall or model size constraints?",
        "trigger_percent": 50,
        "step_type": "action",
        "tools": ["video_transcript_analyzer"],
        "related_doc_ids": ["nvidia_keynote", "linus_review"],
        "author": "@Media_Analyst",
        "system_prompt": "You are a Media Analyst. Extract key quotes and sentiment from the video transcripts that support the memory bottleneck thesis.",
        "model": "qwen2.5:14b"
    },
    "phase_4_social": {
        "name": "User Sentiment Validation",
        "prompt": "Check the Reddit and Twitter discussions. Are real users complaining about VRAM limitations? Does the social sentiment align with the hardware constraints we identified?",
        "trigger_percent": 70,
        "step_type": "observation",
        "related_doc_ids": ["reddit_localllama", "karpathy_tweet"],
        "author": "@Social_Researcher",
        "system_prompt": "You are a User Researcher. Validate technical findings with real user pain points from social media.",
        "model": "llama3.1:8b"
    },
    "phase_5_synthesis": {
        "name": "Strategic Recommendation",
        "prompt": "Synthesize all findings (Dossiers + Hardware Specs + Video Signals + User Pain). Does the evidence support an accelerated roadmap for Phison aidAPTIV+? Provide a decisive recommendation.",
        "trigger_percent": 90,
        "step_type": "thought",
        "tools": ["strategy_engine"],
        "author": "@Lead_Strategist",
        "system_prompt": "You are the Chief Strategy Officer. Synthesize all intelligence into a final go/no-go recommendation for the product roadmap.",
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
    
    def load_documents(self, scenario: str, tier: str) -> List[Dict]:
        """
        Load all documents for a scenario/tier.
        
        Args:
            scenario: Scenario ID (e.g., "pmm", "ces2026")
            tier: Tier level ("lite", "large", or "standard" for ces2026)
        
        Returns:
            List of document dicts with 'category', 'name', 'content'
        """
        cache_key = f"{scenario}_{tier}"
        if cache_key in self.documents_cache:
            return self.documents_cache[cache_key]
        
        documents = []
        
        # CES 2026 has different directory structure (no tier subdirectory)
        if scenario == "ces2026":
            base_path = Path(__file__).parent.parent.parent / "documents" / "ces2026"
            logger.info(f"Loading CES 2026 documents from: {base_path}")
            
            # Load dossier files (strategic context)
            dossier_path = base_path / "dossier"
            if dossier_path.exists():
                for file_path in sorted(dossier_path.glob("*.txt")):
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
            # PMM scenario: Path: backend/services/ollama_service.py -> backend/ -> project_root/ -> documents/
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
    
    async def generate_reasoning(
        self, 
        context: str, 
        phase_key: str,
        scenario: str = "pmm"
    ) -> AsyncGenerator[tuple[str, dict], None]:
        """
        Generate LLM reasoning for a specific analysis phase with performance tracking.
        
        Args:
            context: Full document context
            phase_key: Phase identifier (e.g., "phase_1_review")
            scenario: Current scenario ID
        
        Yields:
            Tuple of (thought_text, performance_metrics)
        """
        phases = ANALYSIS_PHASES_CES if scenario == "ces2026" else ANALYSIS_PHASES
        phase = phases.get(phase_key)
        if not phase:
            logger.error(f"Unknown phase: {phase_key} for scenario {scenario}")
            return
        
        # Build simplified prompt - don't send full context to reduce processing time
        system_prompt = phase.get("system_prompt", """You are an AI analyst for competitive intelligence. 
Provide concise, specific insights based on the analysis phase.""")
        
        user_prompt = f"""CONTEXT DATA:
{context}

ANALYSIS TASK:
{phase['prompt']}

Provide a brief 1-2 sentence insight for this phase of analysis based strictly on the provided context."""
        
        try:
            import time
            first_token_time = None
            token_count = 0
            ttft_ms = 0  # Store TTFT once calculated
            
            # Start timer immediately before API call to measure actual LLM performance
            start_time = time.time()
            
            # Prepare args
            chat_args = {
                'model': phase.get("model", self.model),
                'messages': [
                    {'role': 'system', 'content': system_prompt},
                    {'role': 'user', 'content': user_prompt}
                ],
                'stream': True
            }
            
            # For LLaVA (Vision), inject the mock UI screenshot if it exists
            if chat_args['model'] == 'llava':
                # Path: backend/services/ollama_service.py -> backend/ -> project_root/ -> documents/
                img_path = Path(__file__).parent.parent.parent / "documents" / "pmm" / "lite" / "competitors" / "competitor_ui.png"
                if img_path.exists():
                    logger.info(f"Injecting image for LLaVA: {img_path}")
                    # LLaVA expects image in the user message
                    chat_args['messages'][1]['images'] = [str(img_path)]
            
            stream = ollama.chat(**chat_args)
            
            buffer = ""
            for chunk in stream:
                content = chunk['message']['content']
                buffer += content
                token_count += 1
                
                # Record time to first token (only once)
                if first_token_time is None:
                    first_token_time = time.time()
                    ttft_ms = int((first_token_time - start_time) * 1000)
                
                # Yield complete sentences for better readability
                if any(punct in buffer for punct in ['. ', '! ', '? ', '\n']):
                    # Calculate current performance (cumulative)
                    elapsed = time.time() - start_time
                    tokens_per_sec = token_count / elapsed if elapsed > 0 else 0
                    avg_latency_ms = int((elapsed / token_count) * 1000) if token_count > 0 else 0
                    
                    performance = {
                        "ttft_ms": ttft_ms,  # Keep constant after first token
                        "tokens_per_second": round(tokens_per_sec, 1),
                        "latency_ms": avg_latency_ms,
                        "status": "optimal" if tokens_per_sec > 30 else ("degraded" if tokens_per_sec > 15 else "critical"),
                        "degradation_percent": 0
                    }
                    
                    yield (buffer.strip(), performance)
                    buffer = ""
            
            # Yield any remaining content
            if buffer.strip():
                elapsed = time.time() - start_time
                tokens_per_sec = token_count / elapsed if elapsed > 0 else 0
                avg_latency_ms = int((elapsed / token_count) * 1000) if token_count > 0 else 0
                
                performance = {
                    "ttft_ms": ttft_ms,  # Keep constant
                    "tokens_per_second": round(tokens_per_sec, 1),
                    "latency_ms": avg_latency_ms,
                    "status": "optimal" if tokens_per_sec > 30 else ("degraded" if tokens_per_sec > 15 else "critical"),
                    "degradation_percent": 0
                }
                
                yield (buffer.strip(), performance)
        
        except Exception as e:
            logger.error(f"Error generating reasoning: {e}")
            yield (f"[Error: {str(e)}]", {
                "ttft_ms": 0,
                "tokens_per_second": 0.0,
                "latency_ms": 0,
                "status": "critical",
                "degradation_percent": 100
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
