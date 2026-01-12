# Dead Code Analysis

**Date:** 2025-01-27

---

## 🔴 Confirmed Dead Code

### 1. `_generate_llm_thought()` method
**File:** `backend/services/orchestrator.py:881-975`

**Status:** ❌ **NEVER CALLED**

**Evidence:**
- Method is defined but no calls found in codebase
- The orchestrator uses `_run_agent_cycle()` instead
- This appears to be old code from before agent cycle was implemented

**Action:** Remove or keep as fallback? (Currently used as fallback in error handling)

**Lines:** ~95 lines of unused code

---

### 2. `_check_and_create_thought()` method  
**File:** `backend/services/orchestrator.py:843-879`

**Status:** ⚠️ **ONLY CALLED BY DEAD CODE**

**Evidence:**
- Only called by `_generate_llm_thought()` (which is never called)
- Used as fallback in error handling of `_generate_llm_thought()`

**Action:** Remove if `_generate_llm_thought()` is removed

**Lines:** ~37 lines

---

### 3. `PerformanceMonitor` class
**File:** `backend/services/performance_monitor.py`

**Status:** ⚠️ **CONDITIONALLY DEAD**

**Evidence:**
- Only used when `not self.use_ollama` (line 394)
- But Ollama is enabled by default and being used
- Real performance metrics come from Ollama responses

**Current Usage:**
```python
if not self.use_ollama:
    performance_metrics = self.performance_monitor.calculate_performance(...)
```

**Action:** Keep as fallback for non-Ollama mode, or remove if Ollama is always required

**Lines:** ~76 lines

---

### 4. Image Generation Endpoints (Unused)
**Files:** 
- `backend/api/scenarios.py:114-141` (`/generate/infographic`)
- `backend/api/scenarios.py:129-141` (`/generate/timeline`)

**Status:** ⚠️ **EXIST BUT NOT CALLED**

**Evidence:**
- Endpoints exist in API
- Frontend never calls them (no matches in `src/`)
- Service methods just return placeholder paths (don't actually generate images)
- TODOs indicate they're not implemented

**Action:** Remove endpoints or stub them properly

**Lines:** ~28 lines

---

### 5. `ImageGenService` class
**File:** `backend/services/image_gen_service.py`

**Status:** ⚠️ **PARTIALLY DEAD**

**Evidence:**
- Service exists and is imported
- Methods return placeholder paths only
- TODOs indicate actual generation not implemented
- Only used by unused endpoints

**Action:** Remove service or implement it

**Lines:** ~113 lines

---

## 🟡 Potentially Dead Code

### 6. `THOUGHT_PHASES_PMM` and `THOUGHT_PHASES_CES`
**File:** `backend/services/orchestrator.py:68-148`

**Status:** ⚠️ **ONLY USED BY DEAD CODE**

**Evidence:**
- Only used by `_check_and_create_thought()` 
- Which is only called by `_generate_llm_thought()`
- Which is never called

**Action:** Remove if dead methods are removed

**Lines:** ~80 lines

---

### 7. `_create_metric_updates()` method
**File:** `backend/services/orchestrator.py:976-1018`

**Status:** ⚠️ **COMMENTED OUT**

**Evidence:**
- Method exists but is commented out in `run_simulation()` (line 453-456)
- Comment says: "Metrics are now yielded directly from the agent cycle"
- So this method is no longer used

**Action:** Remove

**Lines:** ~43 lines

---

## 📊 Summary

| Item | Status | Lines | Action |
|------|--------|-------|--------|
| `_generate_llm_thought()` | Dead | ~95 | Remove or keep as fallback |
| `_check_and_create_thought()` | Dead | ~37 | Remove if above removed |
| `PerformanceMonitor` | Conditionally dead | ~76 | Keep as fallback or remove |
| Image gen endpoints | Unused | ~28 | Remove |
| `ImageGenService` | Partially dead | ~113 | Remove or implement |
| `THOUGHT_PHASES_*` | Potentially dead | ~80 | Remove if above removed |
| `_create_metric_updates()` | Commented out | ~43 | Remove |

**Total Dead Code:** ~472 lines (if all removed)

---

## 🎯 Recommended Actions

### Immediate (Safe to Remove)

1. ✅ **Remove `_create_metric_updates()`** - Already commented out
2. ✅ **Remove image generation endpoints** - Not called, not implemented
3. ✅ **Remove `ImageGenService`** - Not used, not implemented

### Conditional (Keep if Needed)

4. ⚠️ **`_generate_llm_thought()` and related** - Keep as fallback for error cases, or remove if agent cycle always works
5. ⚠️ **`PerformanceMonitor`** - Keep if you want non-Ollama fallback, remove if Ollama always required

---

## 🔍 How to Verify

Run these checks:

```bash
# Check if methods are called
grep -r "_generate_llm_thought(" backend/
grep -r "_check_and_create_thought(" backend/
grep -r "generate_infographic" src/
grep -r "generate_timeline" src/
```
