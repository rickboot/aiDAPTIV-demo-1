# CES 2026 INTELLIGENCE CORPUS - DOCUMENT INDEX

## Overview
This corpus contains realistic intelligence documents for the "CES 2026 Supply Chain Monitor" demo scenario. All documents are based on actual web research conducted January 8, 2026.

## Document Categories

### Dossier Files (Strategic Context)
Located in: `documents/ces2026/dossier/`

1. **phison_profile.txt**
   - Company overview, aiDAPTIV+ technology
   - Partnerships (Kioxia, OEMs)
   - Competitive landscape
   - Strategic position Q1 2026

2. **strategic_context.txt**
   - Intelligence framework and inference rules
   - Entity priority matrix
   - Topic keywords for auto-flagging
   - Expected output format

### News & Analysis
Located in: `documents/ces2026/news/`

1. **nvidia_vera_rubin_announcement.txt**
   - NVIDIA CES 2026 keynote
   - Vera Rubin platform specs (1.5TB memory, agentic processing)
   - Inference Context Memory Storage Platform
   - **Strategic Signal**: Validates memory bottleneck (cloud solution)

2. **trendforce_dram_shortage_q1_2026.txt**
   - DRAM price forecast: +55-60% Q1 2026
   - SK Hynix capacity sold out
   - Impact on consumer electronics
   - **Strategic Signal**: OPPORTUNITY (drives demand for offload)

3. **dell_xps_ces2026_memory_analysis.txt**
   - Dell XPS 14/16: 32GB LPDDR5X (soldered)
   - Memory supply pressures acknowledged
   - AI workload implications
   - **Strategic Signal**: OEM constraints = partnership opportunity

4. **kioxia_bics10_production_ramp.txt**
   - 332-layer NAND mass production 2026
   - Phison partnership mentioned
   - Supply security advantages
   - **Strategic Signal**: Partner strength validation

5. **samsung_pm9e1_competitive_threat.txt**
   - Samsung AI SSD with 5nm controller
   - Direct competition to Phison E26
   - Vertical integration strategy
   - **Strategic Signal**: THREAT (competitive pressure)

6. **hp_elitebook_64gb_announcement.txt**
   - HP EliteBook X G1a: 64GB LPDDR5x
   - Premium AI PC positioning
   - Supply chain implications
   - **Strategic Signal**: Market validation + potential partner

7. **trendforce_nand_undersupply_2026.txt**
   - NAND demand +20-22% vs. supply +15-17%
   - Enterprise SSD becoming largest segment
   - Price increases +33-38% Q1
   - **Strategic Signal**: MIXED (higher costs, but Kioxia advantage)

### Social/Grassroots Signals
Located in: `documents/ces2026/social/`

1. **reddit_localllama_memory_pain.txt**
   - Developer pain points: 24GB VRAM insufficient
   - KV cache quadratic growth with context
   - SSD offload experiments mentioned
   - **Strategic Signal**: Market demand validation

2. **twitter_karpathy_agentic_memory.txt**
   - Andrej Karpathy thread on agentic AI memory challenges
   - Context windows outpacing VRAM capacity
   - Phison official account reply
   - **Strategic Signal**: Influencer validation + engagement opportunity

## Expected Intelligence Insights

When analyzed through the strategic context, these documents should generate insights like:

### OPPORTUNITIES
- **DRAM Shortage**: TrendForce report validates aiDAPTIV+ value proposition
- **OEM Constraints**: Dell/HP memory limitations create partnership openings
- **Developer Pain**: Reddit/Twitter signals show grassroots demand
- **Partner Strength**: Kioxia production ramp provides supply security

### THREATS
- **Samsung Competition**: PM9E1 directly competes with E26-based solutions
- **Market Volatility**: NAND price increases could impact aiDAPTIV+ economics

### VALIDATIONS
- **NVIDIA Cloud Solutions**: Proves memory bottleneck is real (different market segment)
- **HP Premium Pricing**: Shows willingness to pay for memory (64GB EliteBook)
- **Influencer Signals**: Karpathy validates agentic AI memory challenges

## Usage in Demo

The orchestrator should:
1. Read dossier files first to establish strategic context
2. Analyze news/social documents through strategic lens
3. Generate insights based on inference rules
4. Display reasoning chain showing how context informed interpretation

## Data Authenticity

All documents based on:
- Actual NVIDIA Vera Rubin specs (CES 2026)
- Real TrendForce market forecasts
- Genuine Dell/HP product specifications
- Authentic Reddit/Twitter discussion patterns
- Verified Kioxia/Samsung technology roadmaps

This ensures the demo feels realistic and credible to industry professionals.
