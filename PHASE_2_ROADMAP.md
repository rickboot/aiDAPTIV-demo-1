# Phase 2 Roadmap - aiDAPTIV+ Demo

**Current Status:** Phase 1 (POC/MVP) - ✅ Complete  
**Next:** Phase 2 - Enhanced Realism & Polish

---

## Phase 1 Summary (What We Have)

✅ **Core Demo Functionality**
- Real-time WebSocket streaming
- Real system memory monitoring (psutil)
- Real LLM integration (Ollama)
- Multi-modal analysis (text, images, video)
- Crash detection and visualization
- "Two Worlds" UI (Userland + Customer Land)
- CES 2026 intelligence corpus

✅ **Working Features**
- Document processing and batching
- Agentic 5-phase analysis
- SGP (Semantic Grounding Profiles) integration
- Model swapping visualization
- Memory telemetry at 1Hz
- Metric extraction from LLM output

---

## Phase 2 Goals

**Primary Objective:** Bridge the gap between "simulated" and "real" to increase demo credibility and impact.

### Focus Areas

1. **Replace Simulated Components with Real Data**
2. **Improve Demo Reliability & Polish**
3. **Enhance Value Demonstration**

---

## Phase 2 Features

### 🔴 High Priority (Core Demo Improvements)

#### 1. Real Document Parsing & RAG Pipeline
**Current:** Virtual file placeholders, text files loaded but not parsed  
**Goal:** Real document parsing with vector storage

**Tasks:**
- [ ] Integrate ChromaDB for document storage
- [ ] Parse actual document content (not just metadata)
- [ ] Implement semantic search for context retrieval
- [ ] Replace virtual placeholders with real document grid

**Impact:** Makes demo more credible - shows real document processing

**Effort:** Medium (2-3 days)

---

#### 2. Real Analysis Metrics from LLM Output
**Current:** Regex extraction + two-pass LLM extraction  
**Goal:** Use LLM JSON mode for structured metric extraction

**Tasks:**
- [ ] Configure Ollama to use JSON mode responses
- [ ] Parse structured JSON for Topics/Patterns/Insights/Flags
- [ ] Remove regex fallback (or keep as backup)
- [ ] Update metrics in real-time from LLM responses

**Impact:** Metrics reflect actual analysis, not estimates

**Effort:** Low (1 day)

---

#### 3. Fix Broken Endpoints
**Current:** `vision_service_13b` undefined, image generation TODOs  
**Goal:** Remove or implement broken features

**Tasks:**
- [ ] Remove `/analyze/image` and `/analyze/video` endpoints (if not needed)
- [ ] OR implement proper vision service integration
- [ ] Remove or stub image generation endpoints
- [ ] Clean up TODO comments

**Impact:** Prevents demo crashes, cleaner codebase

**Effort:** Low (2-4 hours)

---

### 🟡 Medium Priority (Polish & Reliability)

#### 4. VLLM Integration for Accurate KV Cache Stats
**Current:** Algorithmic estimate of KV cache size  
**Goal:** Real KV cache memory stats from VLLM API

**Tasks:**
- [ ] Research VLLM API for memory stats
- [ ] Integrate VLLM client (if available)
- [ ] Replace estimate with real KV cache metrics
- [ ] Fallback to estimate if VLLM unavailable

**Impact:** Shows real memory pressure, more accurate telemetry

**Effort:** Medium-High (3-5 days, depends on VLLM availability)

**Note:** May be out of scope if VLLM not available or too complex

---

#### 5. Enhanced Error Recovery
**Current:** Basic error handling, some silent failures  
**Goal:** Graceful degradation during demo

**Tasks:**
- [ ] Add React Error Boundaries
- [ ] WebSocket auto-reconnection
- [ ] Better error messages for demo troubleshooting
- [ ] Fallback to canned responses if Ollama fails

**Impact:** Demo doesn't crash, handles network issues

**Effort:** Low-Medium (1-2 days)

---

#### 6. Demo Preparation Checklist
**Current:** Manual testing, no checklist  
**Goal:** Ensure demo runs smoothly every time

**Tasks:**
- [ ] Create pre-demo checklist (Ollama running, models pulled, etc.)
- [ ] Add health check endpoint for all services
- [ ] Frontend shows service status before starting
- [ ] Quick smoke test script

**Impact:** Reduces demo failures, professional presentation

**Effort:** Low (1 day)

---

### 🟢 Low Priority (Nice-to-Have)

#### 7. Multi-Scenario Support
**Current:** CES 2026 scenario, PMM references still in code  
**Goal:** Clean up or add second scenario

**Tasks:**
- [ ] Remove PMM scenario code (if not needed)
- [ ] OR fully implement PMM scenario
- [ ] Clean scenario switching logic

**Impact:** Cleaner codebase or more demo options

**Effort:** Low (1 day for cleanup, 3-5 days for full PMM)

---

#### 8. Session History UI
**Current:** Session manager exists but no UI  
**Goal:** Show previous demo runs

**Tasks:**
- [ ] Add session history view
- [ ] Display previous metrics/results
- [ ] Compare runs (with/without aiDAPTIV+)

**Impact:** Shows consistency, allows comparison

**Effort:** Medium (2-3 days)

---

#### 9. Performance Optimizations
**Current:** Works but could be faster  
**Goal:** Smoother demo experience

**Tasks:**
- [ ] Optimize context building (cache context strings)
- [ ] Reduce WebSocket message overhead
- [ ] Frontend performance (React optimizations)

**Impact:** Smoother demo, better UX

**Effort:** Medium (2-3 days)

**Note:** Only if demo feels sluggish

---

## Phase 2 Implementation Plan

**Approach:** Fast iteration with agentic IDE - tackle tasks in priority order, move quickly.

### Immediate Actions (Do These First)

**Priority 1: Fix Broken Code (Prevents Crashes)**
1. Fix `vision_service_13b` undefined reference
2. Remove/stub broken image/video endpoints
3. Clean up TODOs

**Priority 2: Improve Demo Reliability**
4. Add React Error Boundaries
5. WebSocket auto-reconnection
6. Better error messages

**Priority 3: Real Metrics (Better Demo)**
7. JSON mode for structured LLM responses
8. Parse metrics from JSON instead of regex

**Priority 4: Real Documents (More Credible)**
9. Integrate ChromaDB (if ready)
10. Real document parsing
11. Replace virtual placeholders

**Then (If Time/Value):**
- VLLM integration (if available)
- Demo checklist
- Performance optimizations

---

## Out of Scope for Phase 2

❌ **Do NOT prioritize:**
- User authentication (local demo only)
- Multi-model support (GPT-4, Claude) - Ollama is sufficient
- Production deployment (stays local)
- Comprehensive test suite (manual testing OK)
- PDF parsing (text files sufficient for demo)

---

## Success Criteria for Phase 2

**Demo is Phase 2 complete when:**
1. ✅ All broken endpoints fixed or removed
2. ✅ Metrics come from real LLM analysis (not estimates)
3. ✅ Documents are real (not virtual placeholders)
4. ✅ Demo runs reliably (error recovery works)
5. ✅ Pre-demo checklist ensures smooth presentation

**Optional but valuable:**
- Real KV cache stats (if VLLM available)
- Session history UI
- Performance optimizations

---

## Phase 3 (Future - Not Phase 2)

**Only consider after Phase 2 complete:**
- Multi-model support (GPT-4, Claude, Gemini)
- Advanced RAG features
- PDF parsing
- Production deployment considerations
- Comprehensive testing

---

## Quick Start: What to Do Next

**Immediate Next Steps (This Week):**

1. **Fix broken endpoints** (2-4 hours)
   ```bash
   # Remove or stub vision_service_13b references
   # Clean up image generation TODOs
   ```

2. **Implement JSON mode metrics** (1 day)
   ```python
   # Update OllamaService to use JSON mode
   # Parse structured responses for metrics
   ```

3. **Add error boundaries** (4 hours)
   ```typescript
   // Wrap Dashboard in ErrorBoundary
   // Add WebSocket reconnection
   ```

**These 3 items will significantly improve demo reliability and realism.**

---

## Questions to Answer Before Starting

1. **VLLM Integration:** Is VLLM available/accessible? Worth the effort?
2. **ChromaDB:** Is it already set up? Just needs integration?
3. **PMM Scenario:** Remove or implement?
4. **Image Generation:** Remove endpoints or implement?

**Answer these to finalize Phase 2 scope.**

---

*Last Updated: 2025-01-27*
