"""
Semantic Grounding Profile (SGP) Loader
Loads and provides access to SGP configuration for AI agents.
"""

import json
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class SGPLoader:
    """Loads and manages Semantic Grounding Profile configurations."""
    
    def __init__(self, sgp_path: str):
        """
        Initialize SGP loader.
        
        Args:
            sgp_path: Path to SGP JSON file
        """
        self.sgp_path = Path(sgp_path)
        self.sgp = self._load_sgp()
    
    def _load_sgp(self) -> dict:
        """Load SGP from JSON file."""
        try:
            with open(self.sgp_path, 'r', encoding='utf-8') as f:
                sgp = json.load(f)
            logger.info(f"Loaded SGP: {sgp.get('profile_name', 'Unknown')} v{sgp.get('version', '0.0')}")
            return sgp
        except Exception as e:
            logger.error(f"Failed to load SGP from {self.sgp_path}: {e}")
            return {}
    
    def build_system_prompt(self, focus: str = "competitive_intel") -> str:
        """
        Build a system prompt from the SGP.
        
        Args:
            focus: Focus area for the prompt (e.g., "competitive_intel", "technical_analysis")
        
        Returns:
            System prompt string
        """
        if not self.sgp:
            return "You are an AI analyst for competitive intelligence."
        
        identity = self.sgp.get('identity', {})
        problem = self.sgp.get('problem', '')
        solution = self.sgp.get('solution', '')
        guardrails = self.sgp.get('guardrails', {})
        heuristics = self.sgp.get('heuristics', [])
        frameworks = self.sgp.get('analytical_frameworks', {})
        competitive = self.sgp.get('competitive_landscape', {})
        
        # Build competitive context
        comp_context = ""
        if competitive:
            direct = competitive.get('direct_competitors', {})
            if direct:
                comp_context = "\\nKEY COMPETITORS:\\n"
                for name, details in direct.items():
                    threat = details.get('threat_level', 'Unknown')
                    comp_context += f"- {name}: {threat}\\n"
        
        # Build analytical frameworks section
        frameworks_text = ""
        if frameworks:
            frameworks_text = "\\nANALYTICAL FRAMEWORKS (apply these):\\n"
            for name, description in frameworks.items():
                frameworks_text += f"- {name.replace('_', ' ').title()}: {description}\\n"
        
        # Build evidence tiers section
        evidence = self.sgp.get('evidence_types', {})
        evidence_text = ""
        if evidence:
            evidence_text = "\\nEVIDENCE QUALITY TIERS:\\n"
            tiers = evidence.get('tiers', {})
            evidence_text += f"- Tier 1 (Hard): {', '.join(tiers.get('tier_1_hard_evidence', [])[:3])}...\\n"
            evidence_text += f"- Tier 2 (Credible): {', '.join(tiers.get('tier_2_soft_but_credible', [])[:3])}...\\n"
            evidence_text += f"- Tier 3 (Weak): {', '.join(tiers.get('tier_3_weak_signals', [])[:3])}...\\n"
            agent_rules = evidence.get('agent_rules', [])
            if agent_rules:
                evidence_text += "Rules: " + "; ".join(agent_rules[:2]) + "\\n"
        
        # Build actor incentives section
        incentives = self.sgp.get('actor_incentives', {})
        incentives_text = ""
        if incentives:
            incentives_text = "\\nACTOR INCENTIVE MODEL:\\n"
            inc_data = incentives.get('incentives', {})
            # Highlight key actors
            for actor in ['gpu_accelerator_vendors', 'pc_workstation_oems', 'cloud_providers']:
                if actor in inc_data:
                    incentives_text += f"- {actor.replace('_', ' ').title()}: {inc_data[actor][0]}\\n"
            rules = incentives.get('agent_rules', [])
            if rules:
                incentives_text += f"Key Rule: {rules[0]}\\n"
        
        prompt = f"""You are an expert analyst for {identity.get('product_name', 'aiDAPTIV+')}.

PRODUCT IDENTITY:
{identity.get('one_liner', '')}

PROBLEM CONTEXT:
{problem}

SOLUTION APPROACH:
{solution}{comp_context}{frameworks_text}{evidence_text}{incentives_text}

ANALYSIS FRAMEWORK (use these heuristics):
{chr(10).join(f"- {h}" for h in heuristics)}

CRITICAL CONSTRAINTS (NEVER claim):
{chr(10).join(f"- {c}" for c in guardrails.get('forbidden_claims', []))}

CAUTIONS:
{chr(10).join(f"- {c}" for c in guardrails.get('caution', []))}

OUTPUT STYLE:
- Be concise and specific
- Connect insights to memory pressure, DRAM/HBM constraints, local vs cloud economics
- Use conservative, qualitative language unless you have explicit data
- Apply analytical frameworks to identify patterns and second-order effects
- Weight evidence by tier and cite sources when possible
"""
        return prompt
    
    def get_classification_schema(self) -> dict:
        """
        Get the classification schema from SGP.
        
        Returns:
            Dict with categories and impact levels
        """
        return self.sgp.get('output_behavior', {}).get('classification', {})
    
    def get_relevance_signals(self) -> dict:
        """
        Get relevance signals from SGP.
        
        Returns:
            Dict with high_relevance and potential_headwinds lists
        """
        return self.sgp.get('signals', {})
    
    def check_against_guardrails(self, text: str) -> list[str]:
        """
        Check if text violates any guardrails.
        
        Args:
            text: Text to check
        
        Returns:
            List of violated guardrails (empty if none)
        """
        violations = []
        forbidden = self.sgp.get('guardrails', {}).get('forbidden_claims', [])
        
        text_lower = text.lower()
        for claim in forbidden:
            # Simple substring check (could be enhanced with NLP)
            if any(phrase in text_lower for phrase in claim.lower().split()):
                violations.append(claim)
        
        return violations
    
    def classify_relevance(self, content: str) -> dict:
        """
        Classify content relevance based on SGP signals.
        
        Args:
            content: Content to classify
        
        Returns:
            Dict with relevance_score, matching_signals, and is_headwind
        """
        signals = self.get_relevance_signals()
        high_rel = signals.get('high_relevance', [])
        headwinds = signals.get('potential_headwinds', [])
        
        content_lower = content.lower()
        
        # Check for high relevance signals
        matching_signals = []
        for signal in high_rel:
            # Simple keyword matching (could be enhanced)
            keywords = ['dram', 'hbm', 'vram', 'memory', 'ai pc', 'workstation', 
                       'local ai', 'inference', 'context', 'oom', 'bottleneck']
            if any(kw in content_lower for kw in keywords):
                matching_signals.append(signal)
                break
        
        # Check for headwind signals
        is_headwind = False
        for hw in headwinds:
            if 'cloud' in content_lower and 'cost' in content_lower and 'reduc' in content_lower:
                is_headwind = True
                break
        
        relevance_score = len(matching_signals) / max(len(high_rel), 1)
        
        return {
            'relevance_score': relevance_score,
            'matching_signals': matching_signals,
            'is_headwind': is_headwind,
            'is_relevant': relevance_score > 0 or is_headwind
        }
    
    def get_ecosystem_actors(self) -> dict:
        """Get ecosystem actors from SGP."""
        return self.sgp.get('ecosystem', {})
    
    def get_value_props(self) -> list[str]:
        """Get value propositions from SGP."""
        return self.sgp.get('value_props', [])
