"""
Data source abstraction layer.
Supports both generated (deterministic) and live (real-time) data sources.
"""

import logging
from typing import List, Dict, Optional, Literal
from pathlib import Path
from datetime import datetime, timedelta
import random
import json

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════
# DATA SOURCE MODE CONFIGURATION
# ═══════════════════════════════════════════════════════════════

# Default mode (can be overridden by config)
_DEFAULT_DATA_SOURCE_MODE = "generated"  # Options: "generated" | "live" | "hybrid"

# ═══════════════════════════════════════════════════════════════
# GENERATED DATA TEMPLATES (Deterministic, for dev/refinement)
# ═══════════════════════════════════════════════════════════════

NEWS_TEMPLATES = [
    {
        "title": "{company} Announces {product} with {memory}GB Memory",
        "content": """{company} Press Release - {date}

{company} today unveiled its {product} platform, featuring {memory}GB of {memory_type} memory. The announcement comes as the industry grapples with increasing memory demands from AI workloads.

KEY SPECIFICATIONS:
- Memory: {memory}GB {memory_type}
- Bandwidth: {bandwidth}GB/s
- Target Market: {market}
- Availability: {availability}

STRATEGIC IMPLICATIONS:
{implications}

This development {validation} the need for memory optimization solutions like aiDAPTIV+.""",
        "companies": ["NVIDIA", "AMD", "Intel", "Samsung", "Micron", "SK Hynix", "Kioxia"],
        "products": ["AI Accelerator", "Data Center Platform", "Workstation GPU", "Enterprise SSD"],
        "memory_types": ["HBM4", "LPDDR5X", "DDR5", "HBM3E"],
        "markets": ["AI Workloads", "Data Centers", "Edge Computing", "Enterprise"],
        "implications": [
            "Validates memory bottleneck concerns in AI infrastructure",
            "Highlights the gap between model requirements and available hardware",
            "Creates opportunity for SSD-based memory offloading solutions",
            "Demonstrates industry recognition of memory constraints"
        ],
        "validations": ["validates", "reinforces", "highlights", "demonstrates"]
    },
    {
        "title": "Market Report: {memory_type} Prices {trend} {percent}% in Q1 2026",
        "content": """Market Intelligence Report - {date}

According to {analyst_firm}, {memory_type} prices have {trend} by {percent}% in Q1 2026, driven by {driver}.

KEY FINDINGS:
- Price Change: {trend} {percent}%
- Supply: {supply_status}
- Demand: {demand_status}
- Impact: {impact}

COMPETITIVE LANDSCAPE:
{competitive_analysis}

STRATEGIC SIGNAL: {signal}""",
        "analyst_firms": ["TrendForce", "Gartner", "IDC", "Counterpoint Research"],
        "memory_types": ["DRAM", "NAND Flash", "HBM", "LPDDR"],
        "trends": ["increased", "decreased"],
        "drivers": [
            "AI-driven demand outpacing supply",
            "Supply chain constraints",
            "Manufacturing capacity limitations",
            "Increased enterprise adoption"
        ],
        "supply_statuses": ["Tight", "Adequate", "Oversupplied"],
        "demand_statuses": ["Strong", "Moderate", "Weak"],
        "signals": [
            "OPPORTUNITY - Price increases drive demand for cost-effective alternatives",
            "THREAT - Supply constraints could impact product availability",
            "VALIDATION - Market dynamics confirm memory bottleneck thesis"
        ]
    },
    {
        "title": "{oem} Launches {product} with {memory}GB Memory Configuration",
        "content": """{oem} Product Announcement - {date}

{oem} today announced the {product}, featuring up to {memory}GB of {memory_type} memory, targeting {market_segment}.

PRODUCT SPECIFICATIONS:
- Model: {product}
- Memory Options: {memory_options}
- Processor: {processor}
- Price: ${price}
- Availability: {availability}

MARKET POSITIONING:
{positioning}

MEMORY CONSTRAINTS:
{constraints}

STRATEGIC IMPLICATIONS:
{implications}""",
        "oems": ["Dell", "HP", "Lenovo", "ASUS", "MSI", "Razer"],
        "products": ["XPS 15", "EliteBook X", "ThinkPad X1", "ROG Strix", "Blade 18"],
        "memory_options": ["16GB/32GB/64GB", "32GB/64GB", "16GB/32GB"],
        "processors": ["Intel Core Ultra", "AMD Ryzen AI", "Apple M4"],
        "market_segments": ["AI PC", "Workstation", "Gaming", "Enterprise"],
        "constraints": [
            "Soldered memory limits upgradeability",
            "High memory configurations command premium pricing",
            "Supply chain pressures acknowledged by OEM",
            "Memory capacity constraints impact AI workload performance"
        ],
        "implications": [
            "OEM constraints create partnership opportunities for memory solutions",
            "Premium pricing validates market willingness to pay for memory",
            "Soldered configurations drive need for external memory solutions",
            "Supply chain pressures highlight need for alternative memory architectures"
        ]
    }
]

SOCIAL_TEMPLATES = [
    {
        "platform": "Reddit",
        "template": """Reddit Discussion - r/{subreddit}

User: {username}
Date: {date}
Upvotes: {upvotes}
Comments: {comments}

POST:
{post_content}

TOP COMMENTS:
{comments_content}

ANALYSIS:
{analysis}""",
        "subreddits": ["LocalLLaMA", "MachineLearning", "hardware", "buildapc", "artificial"],
        "post_templates": [
            "Just hit OOM trying to run {model} on my {gpu}. Only have {vram}GB VRAM. Anyone else struggling with this?",
            "Is {vram}GB VRAM enough for {model}? Getting crashes during inference.",
            "KV cache is eating all my memory. Context window of {context}k tokens requires {memory}GB. This is insane.",
            "Anyone tried SSD offloading for LLM inference? Running out of VRAM options here.",
            "Why is {company} not addressing the memory bottleneck? {model} needs {memory}GB but most GPUs only have {vram}GB."
        ],
        "models": ["Llama-3-70B", "Mixtral-8x7B", "Qwen2.5-72B", "GPT-4", "Claude-3"],
        "gpus": ["RTX 4090", "RTX 5090", "RTX 3090", "A100", "H100"],
        "vram_amounts": ["24", "32", "40", "48", "80"],
        "context_amounts": ["128", "256", "512", "1024"],
        "memory_amounts": ["40", "60", "80", "100", "120"]
    },
    {
        "platform": "Twitter/X",
        "template": """Twitter Thread - @{username}

Date: {date}
Likes: {likes}
Retweets: {retweets}
Replies: {replies}

THREAD:
{thread_content}

ENGAGEMENT:
{engagement}

ANALYSIS:
{analysis}""",
        "usernames": ["karpathy", "sama", "ylecun", "JeffDean", "AndrewYNg"],
        "thread_templates": [
            "1/{count} The memory bottleneck in AI is real. {model} requires {memory}GB but most hardware only provides {vram}GB. We need better solutions.\n\n2/{count} KV cache grows quadratically with context length. A {context}k context window needs {cache}GB just for cache.\n\n3/{count} This is why we're seeing more interest in offloading strategies - SSD, system RAM, anything to break the VRAM wall.",
            "Interesting observation: {company}'s new {product} addresses memory constraints by {approach}. This validates the market need for {solution_type}.",
            "The AI hardware stack is fundamentally memory-constrained. {stat}% of inference failures are OOM errors. We need architectural changes, not just bigger GPUs."
        ]
    }
]

# ═══════════════════════════════════════════════════════════════
# DATA SOURCE INTERFACE
# ═══════════════════════════════════════════════════════════════

class DataSource:
    """Abstract base class for data sources."""
    
    def fetch_news(self, count: int, category: Optional[str] = None) -> List[Dict]:
        """Fetch news articles."""
        raise NotImplementedError
    
    def fetch_social(self, count: int, platform: Optional[str] = None) -> List[Dict]:
        """Fetch social media signals."""
        raise NotImplementedError
    
    def fetch_dossiers(self) -> List[Dict]:
        """Fetch strategic dossiers."""
        raise NotImplementedError


class GeneratedDataSource(DataSource):
    """Deterministic generated data source for dev/refinement."""
    
    def __init__(self, seed: Optional[int] = None):
        self.seed = seed
        if seed:
            random.seed(seed)
    
    def fetch_news(self, count: int, category: Optional[str] = None) -> List[Dict]:
        """Generate news articles."""
        articles = []
        base_date = datetime(2026, 1, 10)
        
        for i in range(count):
            template = random.choice(NEWS_TEMPLATES)
            
            # Fill template with realistic data
            if "company" in template.get("title", ""):
                company = random.choice(template.get("companies", []))
                product = random.choice(template.get("products", []))
                memory = random.choice([32, 64, 128, 256, 512])
                memory_type = random.choice(template.get("memory_types", []))
                bandwidth = random.choice([800, 1200, 1600, 2400, 3200])
                market = random.choice(template.get("markets", []))
                availability = random.choice(["Q1 2026", "Q2 2026", "Immediate", "H2 2026"])
                implications = random.choice(template.get("implications", []))
                validation = random.choice(template.get("validations", []))
                
                title = template["title"].format(
                    company=company, product=product, memory=memory, memory_type=memory_type
                )
                content = template["content"].format(
                    company=company, product=product, memory=memory, memory_type=memory_type,
                    bandwidth=bandwidth, market=market, availability=availability,
                    implications=implications, validation=validation,
                    date=(base_date + timedelta(days=i)).strftime("%B %d, %Y")
                )
            elif "Market Report" in template.get("title", ""):
                analyst_firm = random.choice(template.get("analyst_firms", []))
                memory_type = random.choice(template.get("memory_types", []))
                trend = random.choice(template.get("trends", []))
                percent = random.randint(15, 60)
                driver = random.choice(template.get("drivers", []))
                supply_status = random.choice(template.get("supply_statuses", []))
                demand_status = random.choice(template.get("demand_statuses", []))
                signal = random.choice(template.get("signals", []))
                
                title = template["title"].format(
                    memory_type=memory_type, trend=trend, percent=percent
                )
                content = template["content"].format(
                    analyst_firm=analyst_firm, memory_type=memory_type, trend=trend,
                    percent=percent, driver=driver, supply_status=supply_status,
                    demand_status=demand_status, signal=signal,
                    date=(base_date + timedelta(days=i)).strftime("%B %d, %Y"),
                    competitive_analysis=f"{analyst_firm} notes that supply constraints are driving {trend} in {memory_type} pricing, creating opportunities for alternative memory architectures.",
                    impact=f"Price {trend} of {percent}% expected to impact {memory_type} adoption rates and drive demand for cost-effective alternatives."
                )
            else:  # OEM announcement
                oem = random.choice(template.get("oems", []))
                product = random.choice(template.get("products", []))
                memory = random.choice([32, 64, 128])
                memory_type = random.choice(["LPDDR5X", "DDR5", "LPDDR5"])
                memory_options = random.choice(template.get("memory_options", []))
                processor = random.choice(template.get("processors", []))
                price = random.randint(1500, 5000)
                availability = random.choice(["Q1 2026", "Q2 2026", "Immediate"])
                market_segment = random.choice(template.get("market_segments", []))
                constraints = random.choice(template.get("constraints", []))
                implications = random.choice(template.get("implications", []))
                
                title = template["title"].format(
                    oem=oem, product=product, memory=memory, memory_type=memory_type
                )
                content = template["content"].format(
                    oem=oem, product=product, memory=memory, memory_type=memory_type,
                    memory_options=memory_options, processor=processor, price=price,
                    availability=availability, market_segment=market_segment,
                    constraints=constraints, implications=implications,
                    date=(base_date + timedelta(days=i)).strftime("%B %d, %2026"),
                    positioning=f"{oem} positions the {product} as a premium {market_segment} solution, emphasizing memory capacity as a key differentiator."
                )
            
            articles.append({
                "name": f"{title.lower().replace(' ', '_').replace(':', '')}_{i}.txt",
                "category": "news",
                "content": content,
                "size_kb": len(content) / 1024,
                "source": "generated",
                "timestamp": (base_date + timedelta(days=i)).isoformat()
            })
        
        return articles
    
    def fetch_social(self, count: int, platform: Optional[str] = None) -> List[Dict]:
        """Generate social media signals."""
        signals = []
        base_date = datetime(2026, 1, 10)
        
        for i in range(count):
            template_data = random.choice(SOCIAL_TEMPLATES)
            template = template_data["template"]
            platform = template_data["platform"]
            
            if platform == "Reddit":
                subreddit = random.choice(template_data.get("subreddits", []))
                username = f"u/user_{random.randint(1000, 9999)}"
                post_template = random.choice(template_data.get("post_templates", []))
                model = random.choice(template_data.get("models", []))
                gpu = random.choice(template_data.get("gpus", []))
                vram = random.choice(template_data.get("vram_amounts", []))
                context = random.choice(template_data.get("context_amounts", []))
                memory = random.choice(template_data.get("memory_amounts", []))
                
                post_content = post_template.format(
                    model=model, gpu=gpu, vram=vram, context=context, memory=memory,
                    company=random.choice(["NVIDIA", "AMD", "Intel"])
                )
                
                comments_content = f"""u/dev_help: 'Same issue here. {vram}GB isn't enough for {model}.'
u/ai_researcher: 'KV cache is the problem. You need {memory}GB+ for {context}k context.'
u/hardware_guru: 'This is why SSD offloading is becoming popular.'"""
                
                analysis = f"Developer community expressing frustration with VRAM limitations. {model} requires {memory}GB+ but most GPUs only have {vram}GB. Strong signal for memory offloading solutions."
                
                content = template.format(
                    subreddit=subreddit, username=username,
                    date=(base_date + timedelta(days=i)).strftime("%B %d, %Y"),
                    upvotes=random.randint(50, 500),
                    comments=random.randint(10, 100),
                    post_content=post_content,
                    comments_content=comments_content,
                    analysis=analysis
                )
            else:  # Twitter
                username = random.choice(template_data.get("usernames", []))
                thread_template = random.choice(template_data.get("thread_templates", []))
                model = random.choice(["Llama-3-70B", "GPT-4", "Claude-3"])
                memory = random.choice(["40", "60", "80"])
                vram = random.choice(["24", "32", "40"])
                context = random.choice(["128", "256", "512"])
                cache = random.choice(["20", "30", "40"])
                company = random.choice(["NVIDIA", "AMD", "Intel"])
                product = random.choice(["AI Accelerator", "GPU", "Platform"])
                approach = random.choice(["SSD offloading", "system RAM expansion", "memory pooling"])
                solution_type = random.choice(["memory optimization", "offloading", "alternative architectures"])
                stat = random.randint(60, 85)
                
                thread_content = thread_template.format(
                    count=random.randint(3, 7), model=model, memory=memory, vram=vram,
                    context=context, cache=cache, company=company, product=product,
                    approach=approach, solution_type=solution_type, stat=stat
                )
                
                engagement = f"Thread received {random.randint(500, 5000)} likes, {random.randint(100, 1000)} retweets, and {random.randint(50, 500)} replies. High engagement indicates strong community interest."
                analysis = f"Influencer validation of memory bottleneck. {username} has {random.randint(100000, 1000000)} followers. High engagement suggests broad awareness of the issue."
                
                content = template.format(
                    username=username,
                    date=(base_date + timedelta(days=i)).strftime("%B %d, %Y"),
                    likes=random.randint(500, 5000),
                    retweets=random.randint(100, 1000),
                    replies=random.randint(50, 500),
                    thread_content=thread_content,
                    engagement=engagement,
                    analysis=analysis
                )
            
            signals.append({
                "name": f"{platform.lower()}_signal_{i}.txt",
                "category": "social",
                "content": content,
                "size_kb": len(content) / 1024,
                "source": "generated",
                "platform": platform,
                "timestamp": (base_date + timedelta(days=i)).isoformat()
            })
        
        return signals
    
    def fetch_dossiers(self, scenario_slug: str = "mktg_intelligence_demo") -> List[Dict]:
        """Load existing dossiers (not generated)."""
        # Dossiers are strategic context - keep them real/manual
        # Directory name mapping: map scenario slugs to actual directory names on disk
        directory_mapping = {
            "mktg_intelligence_demo": "ces2026",  # Map new scenario slug to existing directory name
            "intel_demo": "ces2026",  # Backward compatibility: old name
            "ces2026": "ces2026"  # Backward compatibility
        }
        directory_name = directory_mapping.get(scenario_slug, scenario_slug)
        dossier_path = Path(__file__).parent.parent.parent / "data" / "realstatic" / directory_name / "dossier"
        dossiers = []
        
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
                    dossiers.append({
                        "name": file_path.name,
                        "category": "dossier",
                        "content": content,
                        "size_kb": file_path.stat().st_size / 1024,
                        "source": "file"
                    })
                except Exception as e:
                    logger.warning(f"Failed to load dossier {file_path}: {e}")
        
        return dossiers


class LiveDataSource(DataSource):
    """Live data source - fetches real-time data from APIs."""
    
    def __init__(self):
        # Try OAuth Reddit client first, fallback to simple (no auth) client
        self.reddit_client = None
        
        # Try OAuth client (requires credentials)
        try:
            import config
            if config.REDDIT_API_ENABLED:
                from services.live_feeds.reddit_api import create_reddit_client
                self.reddit_client = create_reddit_client()
                if self.reddit_client:
                    logger.info("LiveDataSource: Reddit OAuth client initialized")
        except Exception as e:
            logger.debug(f"LiveDataSource: OAuth Reddit client not available: {e}")
        
        # Fallback to simple client (no auth needed)
        if not self.reddit_client:
            try:
                from services.live_feeds.reddit_simple import create_reddit_simple_client
                self.reddit_client = create_reddit_simple_client()
                logger.info("LiveDataSource: Reddit simple client initialized (no auth required)")
            except Exception as e:
                logger.warning(f"LiveDataSource: Could not initialize Reddit client: {e}")
                self.reddit_client = None
    
    def fetch_news(self, count: int, category: Optional[str] = None) -> List[Dict]:
        """
        Fetch live news articles.
        
        Note: Live news fetching is not yet implemented. Current implementation
        uses static news files from the data directory. Future implementation
        could integrate NewsAPI, RSS feeds, or web scraping with rate limiting.
        """
        logger.warning("LiveDataSource: News fetching not yet implemented, using static files")
        return []
    
    def fetch_social(self, count: int, platform: Optional[str] = None) -> List[Dict]:
        """Fetch live social media signals."""
        if not self.reddit_client:
            logger.warning("LiveDataSource: Reddit client not available")
            return []
        
        # Relevant subreddits for AI/memory/hardware topics
        subreddits = [
            "LocalLLaMA",      # Local LLM discussions
            "MachineLearning", # ML community
            "hardware",        # Hardware discussions
            "buildapc",        # PC building (memory discussions)
            "artificial",      # AI discussions
        ]
        
        # Calculate posts per subreddit
        posts_per_sub = max(1, count // len(subreddits))
        
        try:
            posts = self.reddit_client.fetch_multiple_subreddits(
                subreddits=subreddits,
                limit_per_sub=posts_per_sub
            )
            
            # Filter by keywords (AI, memory, GPU, LLM, etc.) and exclude irrelevant content
            keywords = ["ai", "memory", "gpu", "llm", "vram", "ram", "dram", "nand", "ssd", "model", "training", "inference", "hardware"]
            filtered_posts = []
            excluded_keywords = ["self-promotion", "weekly discussion", "megathread", "meta thread"]
            
            for post in posts:
                content_lower = post.get("content", "").lower()
                metadata = post.get("metadata", {})
                author = metadata.get("author", "").lower()
                
                # Skip bot/administrative accounts
                if author in ["automoderator", "[deleted]", "reddit"]:
                    continue
                
                # Skip administrative/meta posts
                if any(kw in content_lower for kw in excluded_keywords):
                    continue
                
                # Only include posts with relevant keywords
                if any(kw in content_lower for kw in keywords):
                    filtered_posts.append(post)
                    if len(filtered_posts) >= count:
                        break
            
            # If we don't have enough filtered posts, add more (but still exclude bots/admin)
            if len(filtered_posts) < count:
                for post in posts:
                    if post in filtered_posts:
                        continue
                    metadata = post.get("metadata", {})
                    author = metadata.get("author", "").lower()
                    content_lower = post.get("content", "").lower()
                    
                    # Still exclude bots/admin even if no keywords match
                    if author in ["automoderator", "[deleted]", "reddit"]:
                        continue
                    if any(kw in content_lower for kw in excluded_keywords):
                        continue
                    
                    filtered_posts.append(post)
                    if len(filtered_posts) >= count:
                        break
            
            logger.info(f"LiveDataSource: Fetched {len(filtered_posts)} social signals from Reddit")
            return filtered_posts[:count]
        except Exception as e:
            logger.error(f"LiveDataSource: Error fetching social signals: {e}")
            return []
    
    def fetch_dossiers(self) -> List[Dict]:
        """Dossiers are still manual/strategic - use file-based."""
        return GeneratedDataSource().fetch_dossiers()


class HybridDataSource(DataSource):
    """Hybrid: Use generated for some categories, live for others."""
    
    def __init__(self):
        self.generated = GeneratedDataSource()
        self.live = LiveDataSource()
    
    def fetch_news(self, count: int, category: Optional[str] = None) -> List[Dict]:
        """Use live news if available, fallback to generated."""
        try:
            return self.live.fetch_news(count, category)
        except:
            logger.warning("Live news unavailable, using generated")
            return self.generated.fetch_news(count, category)
    
    def fetch_social(self, count: int, platform: Optional[str] = None) -> List[Dict]:
        """Use live social if available, fallback to generated."""
        try:
            return self.live.fetch_social(count, platform)
        except:
            logger.warning("Live social unavailable, using generated")
            return self.generated.fetch_social(count, platform)
    
    def fetch_dossiers(self) -> List[Dict]:
        """Always use file-based dossiers."""
        return self.generated.fetch_dossiers()


# ═══════════════════════════════════════════════════════════════
# FACTORY FUNCTION
# ═══════════════════════════════════════════════════════════════

def get_data_source(mode: Optional[str] = None) -> DataSource:
    """Get data source based on configuration."""
    if mode is None:
        # Try to import config, fallback to default
        try:
            import config as app_config
            mode = app_config.DATA_SOURCE_MODE
        except:
            mode = _DEFAULT_DATA_SOURCE_MODE
    
    if mode == "live":
        return LiveDataSource()
    elif mode == "hybrid":
        return HybridDataSource()
    else:  # "generated" (default)
        return GeneratedDataSource(seed=42)  # Deterministic seed for reproducibility
