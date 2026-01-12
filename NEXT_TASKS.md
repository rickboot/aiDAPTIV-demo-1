# Next Tasks - Phase 2

**Approach:** Fast iteration, tackle in priority order

---

## 🔴 Priority 1: Fix Broken Code (Do First)

### Task 1.1: Fix `vision_service_13b` undefined
**File:** `backend/api/scenarios.py:139`

**Issue:** References undefined `vision_service_13b`

**Fix Options:**
- **Option A (Recommended):** Remove the endpoints if not needed
- **Option B:** Stub them with placeholder responses
- **Option C:** Implement if actually needed for demo

**Action:** Remove `/analyze/image` and `/analyze/video` endpoints (lines 114-179)

---

### Task 1.2: Clean Up Image Generation TODOs
**File:** `backend/services/image_gen_service.py`

**Issue:** TODOs for unimplemented features

**Fix Options:**
- **Option A:** Remove endpoints if not needed
- **Option B:** Return placeholder/stub responses
- **Option C:** Implement basic version

**Action:** Stub with placeholder responses for now

---

## 🟡 Priority 2: Demo Reliability (Quick Wins)

### Task 2.1: Add React Error Boundary
**File:** `src/App.tsx` or new `ErrorBoundary.tsx`

**Action:**
```typescript
// Wrap Dashboard in ErrorBoundary
// Prevents white screen on errors
```

**Time:** 15 minutes

---

### Task 2.2: WebSocket Auto-Reconnection
**File:** `src/ScenarioContext.tsx`

**Action:**
```typescript
// Add exponential backoff reconnection
// Handle connection drops gracefully
```

**Time:** 30 minutes

---

### Task 2.3: Better Error Messages
**Files:** `backend/services/orchestrator.py`, `backend/api/websocket.py`

**Action:**
- Add more context to error logs
- Return user-friendly error messages
- Log document name, phase, etc. in errors

**Time:** 30 minutes

---

## 🟢 Priority 3: Real Metrics (Better Demo)

### Task 3.1: JSON Mode for LLM Responses
**File:** `backend/services/ollama_service.py`

**Action:**
```python
# Update generate_step to use JSON mode
# Request structured output from Ollama
# Parse JSON for Topics/Patterns/Insights/Flags
```

**Changes:**
- Add `format: "json"` to Ollama chat options
- Update prompts to request JSON structure
- Parse JSON response instead of regex

**Time:** 2-3 hours

---

### Task 3.2: Remove Regex Fallback (or keep as backup)
**File:** `backend/services/orchestrator.py:_extract_metrics()`

**Action:**
- Use JSON parsing as primary
- Keep regex as fallback if JSON fails
- Log which method was used

**Time:** 30 minutes

---

## 🔵 Priority 4: Real Documents (More Credible)

### Task 4.1: Check ChromaDB Status
**File:** `backend/vector_db/chroma_client.py`

**Action:**
- Verify ChromaDB is initialized
- Check if documents are already stored
- Test basic operations

**Time:** 30 minutes

---

### Task 4.2: Integrate ChromaDB for Document Storage
**File:** `backend/services/context_manager.py`

**Action:**
- Use ChromaDB to store document embeddings
- Retrieve documents for context building
- Replace virtual placeholders with real documents

**Time:** 4-6 hours (depends on ChromaDB setup)

---

### Task 4.3: Real Document Parsing
**Files:** `backend/services/ollama_service.py`, `backend/services/orchestrator.py`

**Action:**
- Parse actual document content
- Extract meaningful chunks
- Build context from real content

**Time:** 2-3 hours

---

## 📋 Quick Reference: Task Order

**Do These Now (1-2 hours total):**
1. ✅ Fix `vision_service_13b` (15 min)
2. ✅ Clean up image gen TODOs (15 min)
3. ✅ Add Error Boundary (15 min)
4. ✅ WebSocket reconnection (30 min)

**Then (3-4 hours):**
5. ✅ JSON mode metrics (2-3 hours)
6. ✅ Better error messages (30 min)

**Then (6-9 hours if needed):**
7. ⚪ ChromaDB integration (4-6 hours)
8. ⚪ Real document parsing (2-3 hours)

---

## 🚀 Ready to Execute?

**Start with Task 1.1** - Fix the broken endpoint reference. This prevents potential demo crashes.

**Which task should we tackle first?**
