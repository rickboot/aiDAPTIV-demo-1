"""
Script to generate sample documents for aiDAPTIV+ demo.
Run this to populate the documents/pmm directory.
"""

import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent.parent / "documents" / "pmm"

# ═══════════════════════════════════════════════════════════════
# PAPER TEMPLATES
# ═══════════════════════════════════════════════════════════════

PAPER_TEMPLATE = """arXiv Paper Analysis - {paper_id}

Title: {title}
Authors: {authors}
Published: {date}
Category: {category}

═══════════════════════════════════════════════════════════════
ABSTRACT
═══════════════════════════════════════════════════════════════

{abstract}

═══════════════════════════════════════════════════════════════
KEY FINDINGS
═══════════════════════════════════════════════════════════════

{findings}

═══════════════════════════════════════════════════════════════
RELEVANCE TO COMPETITIVE ANALYSIS
═══════════════════════════════════════════════════════════════

{relevance}
"""

PAPER_DATA = [
    {
        "title": "Agentic Architectures for Large Language Models",
        "category": "AI Systems",
        "abstract": "We present a comprehensive framework for building agentic systems using large language models. Our approach combines multi-step reasoning, tool use, and memory management to enable autonomous task completion.",
        "findings": "- Agent-based systems outperform single-shot LLM calls by 3.2x on complex tasks\n- Orchestration layer reduces latency through parallel execution\n- Memory management critical for context window optimization",
        "relevance": "Directly applicable to competitive product analysis. Competitors implementing these patterns show 40% improvement in user task completion rates."
    },
    {
        "title": "Multi-Agent Collaboration Patterns in Production Systems",
        "category": "Distributed Systems",
        "abstract": "Analysis of real-world multi-agent deployments reveals common collaboration patterns and anti-patterns. We identify key architectural decisions that impact system reliability and performance.",
        "findings": "- Hub-and-spoke topology most common (67% of deployments)\n- Consensus mechanisms reduce hallucination rates by 45%\n- Agent specialization improves accuracy vs. generalist agents",
        "relevance": "Competitor B's recent architecture blog post references these exact patterns. Suggests they're following academic best practices."
    },
    {
        "title": "Reasoning Traces and Explainability in AI Agents",
        "category": "AI Safety",
        "abstract": "We propose a framework for capturing and visualizing reasoning traces in agentic systems, enabling better debugging and user trust.",
        "findings": "- Reasoning traces increase user trust by 28%\n- Debug time reduced by 60% with trace visualization\n- Regulatory compliance improved through audit trails",
        "relevance": "Competitor A's new UI includes 'thinking' indicators - likely implementing reasoning trace visualization for end users."
    },
]

# ═══════════════════════════════════════════════════════════════
# SOCIAL SIGNALS TEMPLATE
# ═══════════════════════════════════════════════════════════════

SOCIAL_TEMPLATE = """Social Media Intelligence - Signal #{num}

Platform: {platform}
Date: {date}
Category: Competitive Intelligence

═══════════════════════════════════════════════════════════════
SIGNAL CONTENT
═══════════════════════════════════════════════════════════════

{content}

═══════════════════════════════════════════════════════════════
ANALYSIS
═══════════════════════════════════════════════════════════════

{analysis}
"""

SOCIAL_SIGNALS = [
    {
        "platform": "LinkedIn",
        "content": "CTO of Competitor A posted: 'Excited to share that we've rebuilt our entire platform on an agentic architecture. 6 months of work, but the results are incredible. Our users are seeing 3x productivity gains.'",
        "analysis": "Public confirmation of architectural shift. Timeline (6 months) suggests significant engineering investment. Productivity claims align with academic research on agentic systems."
    },
    {
        "platform": "Twitter",
        "content": "Thread from Competitor B's Head of Product: '1/7 Why we're betting big on AI agents... [detailed thread on agent orchestration, tool use, and autonomous workflows]'",
        "analysis": "Product leadership publicly evangelizing agentic approach. Thread received 12K likes, 3K retweets - strong market interest signal."
    },
    {
        "platform": "Hacker News",
        "content": "Competitor C's open-source agent framework reached #1 on HN. 847 points, 312 comments. Top comment: 'This is the future of SaaS'",
        "analysis": "Developer community validation. Open-source strategy building mindshare. Comments reveal strong interest from potential enterprise buyers."
    },
]

# ═══════════════════════════════════════════════════════════════
# GENERATION FUNCTIONS
# ═══════════════════════════════════════════════════════════════

def generate_papers(tier: str, count: int):
    """Generate paper documents."""
    papers_dir = BASE_DIR / tier / "papers"
    papers_dir.mkdir(parents=True, exist_ok=True)
    
    for i in range(count):
        paper_id = f"2401.{12800 + i}"
        data_idx = i % len(PAPER_DATA)
        data = PAPER_DATA[data_idx]
        
        content = PAPER_TEMPLATE.format(
            paper_id=paper_id,
            title=f"{data['title']} (Variant {i+1})",
            authors=f"Smith et al., Research Lab {i % 5 + 1}",
            date=f"January {(i % 28) + 1}, 2026",
            category=data['category'],
            abstract=data['abstract'],
            findings=data['findings'],
            relevance=data['relevance']
        )
        
        filepath = papers_dir / f"arxiv_{i+1:03d}.txt"
        filepath.write_text(content)
    
    print(f"Generated {count} papers for {tier} tier")


def generate_social(tier: str, count: int):
    """Generate social signal documents."""
    social_dir = BASE_DIR / tier / "social"
    social_dir.mkdir(parents=True, exist_ok=True)
    
    for i in range(count):
        data_idx = i % len(SOCIAL_SIGNALS)
        data = SOCIAL_SIGNALS[data_idx]
        
        content = SOCIAL_TEMPLATE.format(
            num=i+1,
            platform=data['platform'],
            date=f"January {(i % 28) + 1}, 2026",
            content=data['content'],
            analysis=data['analysis']
        )
        
        filepath = social_dir / f"social_signal_{i+1}.txt"
        filepath.write_text(content)
    
    print(f"Generated {count} social signals for {tier} tier")


def generate_competitors_large():
    """Generate additional competitors for large tier."""
    competitors_dir = BASE_DIR / "large" / "competitors"
    competitors_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy lite tier competitors first
    lite_dir = BASE_DIR / "lite" / "competitors"
    for comp_file in lite_dir.glob("*.txt"):
        target = competitors_dir / comp_file.name
        target.write_text(comp_file.read_text())
    
    # Generate 9 more competitors (d through l)
    for i in range(9):
        letter = chr(100 + i)  # d, e, f, ...
        content = f"""Competitor {letter.upper()} - Product Intelligence Analysis

Company: Competitor {letter.upper()} (Market Player #{i+4})
Analysis Date: January 2026
Category: Competitive Intelligence

═══════════════════════════════════════════════════════════════
RECENT PRODUCT UPDATES
═══════════════════════════════════════════════════════════════

Recent developments indicate exploration of agentic capabilities.
Product roadmap mentions "AI-powered automation" and "intelligent workflows".
Beta program launched for "autonomous task execution" features.

═══════════════════════════════════════════════════════════════
TECHNICAL OBSERVATIONS
═══════════════════════════════════════════════════════════════

Architecture Signals:
- API changes suggest backend modernization
- New endpoints for asynchronous task processing
- Webhook integration for event-driven workflows
- Increased focus on developer experience

Market Positioning:
- Following industry trend toward agentic systems
- Emphasis on automation and productivity
- Targeting mid-market segment
- Competitive pricing strategy

═══════════════════════════════════════════════════════════════
STRATEGIC IMPLICATIONS
═══════════════════════════════════════════════════════════════

Threat Level: Medium
- Not yet a market leader in agentic space
- Watching closely for acceleration signals
- Could become more competitive with proper execution
"""
        filepath = competitors_dir / f"competitor_{letter}.txt"
        filepath.write_text(content)
    
    print(f"Generated 12 total competitors for large tier")


# ═══════════════════════════════════════════════════════════════
# MAIN EXECUTION
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("Generating document corpus for aiDAPTIV+ demo...")
    print("=" * 60)
    
    # LITE TIER (already have 3 competitors)
    generate_papers("lite", 10)
    generate_social("lite", 5)
    
    # LARGE TIER
    generate_competitors_large()
    generate_papers("large", 234)
    generate_social("large", 22)
    
    print("=" * 60)
    print("Document generation complete!")
    print(f"Lite tier: 18 documents (3 competitors + 10 papers + 5 social)")
    print(f"Large tier: 268 documents (12 competitors + 234 papers + 22 social)")
