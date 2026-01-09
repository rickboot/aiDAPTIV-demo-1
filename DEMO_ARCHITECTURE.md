# aiDAPTIV+ Demo Architecture & Design Philosophy

## Core Concept: "The Two Worlds"

The demo is designed to simulate a real-world workload to prove the value of the hardware. To do this effectively, it must present two distinct, simultaneous details:

### 1. Userland (The "Movie")
**Persona:** Business Analyst, Intelligence Officer, Researcher.
**Context:** A "War Room" dashboard for competitive intelligence.
**Goal:** Process massive amounts of data to find competitors, trends, and risks.
**Philosophy:** "I don't care about memory, I don't care about SSDs. I just need to process these 500 PDFs and get answers *now*."

**UI Elements:**
*   **Main Dashboard:** The "mission control" interface.
*   **Reasoning Chain:** The stream of "thought" showing the AI working on the problem.
*   **Data Sources Grid:** The raw material being processed.
*   **Business Metrics:** Indicators of *value* generated.

### 2. Customer Land (The "Reality")
**Persona:** IT Director, System Architect, Hardware Buyer (The person buying the SSD).
**Context:** Observing the system strain under the massive workload.
**Goal:** Prevent OOM (Out of Memory) crashes, reduce cloud costs, and enable local large-model inference.
**Philosophy:** "How are they running a 70B model with 128k context on a workstation? Ah, it's aiDAPTIV+."

**UI Elements:**
*   **Hardware Monitor (Sidebar):** The real-time "truth" of the system resources.
*   **Crash Screen (The Failure):** The consequence of *not* having the hardware.
*   **Success Overlay (The Reveal):** The bridge between the two worlds—showing how the hardware enabled the business result.

---

## Metrics Strategy

The metrics are strictly divided to serve these two personas without confusion.

### Userland Metrics (Analyst Dashboard)
These metrics measure **Work & Value**. They tell the story of the *analysis*.

1.  **KEY TOPICS** (Breadth)
    *   *Formerly: Entities Extracted / Competitors Tracked*
    *   **Meaning:** Distinct subjects, companies, or themes identified across documents.
    *   **Signal:** "The AI is reading widely."

2.  **PATTERNS DETECTED** (Depth)
    *   *Formerly: Visual Updates*
    *   **Meaning:** Recurring trends found by correlating multiple documents.
    *   **Signal:** "The AI is reasoning, not just retrieving."

3.  **INSIGHTS GENERATED** (Value)
    *   *Formerly: Papers Analyzed*
    *   **Meaning:** Actionable conclusions synthesized from raw data.
    *   **Signal:** "This is useful output."

4.  **CRITICAL FLAGS** (Urgency)
    *   *Formerly: Signals Detected*
    *   **Meaning:** High-priority anomalies requiring human review.
    *   **Signal:** "The system is protecting us from risk."

### Customer Land Metrics (Hardware Monitor)
These metrics measure **Pressure & Capacity**. They tell the story of the *system*.

1.  **Context Tokens**: The sheer volume of data "held in mind" (e.g., 60k / 128k).
    *   *Narrative:* "Look how fast the context grows. This is impossible for normal RAM."
2.  **KV Cache (GB)**: The memory cost of that context.
    *   *Narrative:* "The hidden killer. 60k tokens = ~1GB+ of loss. With aiDAPTIV+, this goes to SSD."
3.  **Model Weights (GB)**: The baseline cost.
    *   *Narrative:* "The 70B model takes most of the RAM. There's no room left for Context involved."
4.  **Swap / Offload (GB)**: The hero metric.
    *   *Narrative:* "Here is the overflowing memory being safely handled by the SSD."

---

## Interaction Model

1.  **The Trigger**: The simulated workload (Userland) dumps hundreds of documents into the context.
2.  **The Pressure**: The Hardware Monitor (Customer Land) shows RAM filling up and Context Tokens skyrocketing.
3.  **The Crisis**:
    *   *Without aiDAPTIV+:* The system OOMs. The Userland "Movie" stops abruptly.
    *   *With aiDAPTIV+:* The "Offload" metric activates. The simulation continues.
4.  **The Payoff**: The Success Overlay appears. It explicitly links the two worlds:
    *   "Because you offloaded **20GB** (Customer Land)..."
    *   "...you successfully identified **12 Critical Flags** (Userland)."

---

## Reality Matrix: What is Real vs. Simulated?

To ensure transparency and trust, here is the breakdown of the demo's current implementation state.

### ✅ What is REAL (The Engine)
*   **System Telemetry:** All RAM, Swap, and SSD usage metrics are pulled directly from the OS kernel via `psutil`. If the system runs out of memory, it is a real physical event.
*   **Crash Logic:** The "Crash" is triggered by actual system metrics (Swap Delta > 2GB), not a timer.
*   **LLM Generation:** The "Reasoning Chain" text is generated in real-time by a local Ollama model (e.g., Llama 3).
*   **Hardware Offload:** If aiDAPTIV+ software is installed on the host, the offloading shown in telemetry is physically happening.

### 🎭 What is SIMULATED (The Movie)
*   **Business Metrics:** "Key Topics", "Patterns Detected", etc., are narrative counters incremented based on progress percentage. They simulate the *results* of analysis.
*   **Document Loading:** The 268+ files in the grid are virtual placeholders. We simulate the *computational load* of reading them (by feeding tokens to the model), but we are not parsing physical PDF files from disk.
*   **KV Cache Logic:** The "KV Cache (GB)" metric is an algorithmic estimate based on token count, as most OS drivers do not expose this granular VRAM statistic easily across platforms.

### 🚀 Future Roadmap: Bridging the Gap
1.  **Real Document Parsing:** Replace virtual file placeholders with a real locally vector-stored RAG pipeline.
2.  **VLLM Integration:** Connect directly to the VLLM API to retrieve exact KV Cache memory stats instead of estimating them.
3.  **Real Analysis Metrics:** Use the LLM's actual output (e.g., JSON mode) to count "Entities Found" dynamically.
