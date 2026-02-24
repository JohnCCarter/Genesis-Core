# Bug #2 Fix: ComponentContextBuilder Key Mapping

**Date**: 2026-02-02
**Branch**: `feature/composable-strategy-phase2`
**Status**: ✅ FIXED and validated
**Issue**: EVGate received degenerate EV=0.0 for all decisions

---

## Problem

**Symptom**: EVGate with `min_ev: 0.1` vetoed 100% of entries (2041/2041)

**Root Cause**: ComponentContextBuilder used wrong keys to extract probabilities:
```python
# BEFORE (INCORRECT)
context["ml_proba_long"] = probas.get("LONG", 0.0)   # Returns 0.0 (key not found)
context["ml_proba_short"] = probas.get("SHORT", 0.0) # Returns 0.0 (key not found)

# Actual model output
probas = {"buy": 0.6, "sell": 0.4, "hold": 0.0}  # Uses 'buy'/'sell' keys!
```

**Impact**: EV calculation received p_long=0, p_short=0 → expected_value=0 for ALL bars.

---

## Solution

**File**: `src/core/strategy/components/context_builder.py`

**Changes**:

1. **Robust key mapping** with case-insensitive normalization:
```python
# Normalize keys to handle both 'buy'/'sell' and 'LONG'/'SHORT'
probas_normalized = {k.lower(): v for k, v in probas.items()}

p_long = (
    probas_normalized.get("buy")   # Primary: model output
    or probas_normalized.get("long")  # Fallback: legacy
    or 0.0
)
p_short = (
    probas_normalized.get("sell")   # Primary: model output
    or probas_normalized.get("short")  # Fallback: legacy
    or 0.0
)

# Only set proba keys if we have valid values
if p_long > 0 or p_short > 0:
    context["ml_proba_long"] = p_long
    context["ml_proba_short"] = p_short
```

2. **No degenerate EV emission**:
```python
# Only emit EV fields when probas are valid (not both zero)
if "ml_proba_long" in context and "ml_proba_short" in context:
    p_long = context["ml_proba_long"]
    p_short = context["ml_proba_short"]

    if p_long > 0 or p_short > 0:  # Avoid degenerate case
        R = 1.0
        ev_long = p_long * R - p_short
        ev_short = p_short * R - p_long
        context["expected_value"] = max(ev_long, ev_short)
```

---

## Test Coverage

**26 new tests added** (all passing):

### Unit Tests (13 tests)
**File**: `tests/core/strategy/components/test_context_builder_key_mapping.py`

- **Key mapping coverage**:
  - ✅ Handles 'buy'/'sell' keys (primary)
  - ✅ Handles 'LONG'/'SHORT' keys (fallback)
  - ✅ Case-insensitive (Buy, BUY, buy all work)
  - ✅ Prefers 'buy'/'sell' over 'LONG'/'SHORT' when both present

- **EV field emission**:
  - ✅ EV fields present when probas valid
  - ✅ EV fields absent when probas missing
  - ✅ EV fields absent when probas both zero (degenerate)

- **EV monotonicity**:
  - ✅ EV increases with probability gap
  - ✅ EV positive when buy dominates
  - ✅ EV sign matches dominant direction
  - ✅ EV near zero when probas equal

- **Backward compatibility**:
  - ✅ ml_confidence single key still set
  - ✅ confidence dict still mapped

### Integration Tests (10 tests)
**File**: `tests/core/strategy/components/test_ev_gate_integration.py`

- ✅ EVGate receives non-zero EV with buy/sell keys
- ✅ EVGate veto logic works with corrected keys
- ✅ EVGate allows high EV signals
- ✅ EVGate defensive when EV missing
- ✅ Calibrated threshold behavior (p80, p90)

### Regression Tests (3 tests)
**File**: `tests/integration/test_composable_ev_gate_regression.py`

- ✅ Golden trace: EVGate with min_ev=0.1 → 45% veto (was 100%)
- ✅ High threshold vetoes most samples
- ✅ Low threshold allows most samples

---

## Validation Results

### Before Fix
- **EV values**: All 0.0 (degenerate)
- **EVGate veto rate** (min_ev=0.1): **100%** (2041/2041)
- **EVGate confidence**: min=0.000, max=0.000, avg=0.000

### After Fix
- **EV values**: Mean=0.064, Std=0.048, Range=[0.0, 0.276]
- **EVGate veto rate** (min_ev=0.1): **~45%** (golden trace)
- **EVGate confidence**: Functional (non-degenerate)

### Corrected EV Distribution (Q1 2024)
```
Percentiles:
  p50: 0.055
  p75: 0.093
  p80: 0.103 ← Recommended min_ev for 20% veto
  p90: 0.131 ← Recommended min_ev for 10% veto
  p95: 0.152
```

---

## Impact on Phase 3

### Unblocked
- ✅ EVGate now functional for component tuning
- ✅ Can proceed with v4/v5 config validation
- ✅ EV-based filtering ready for Optuna optimization

### Still Blocked
- ⚠️ Bug #1 (CooldownComponent) - 1871 vetoes with 0 trades
- ⚠️ Gap #3 (Execution layer) - 98.6% drop rate

---

## Files Changed

### Production Code
- `src/core/strategy/components/context_builder.py` (lines 36-101)

### Tests
- `tests/core/strategy/components/test_context_builder_key_mapping.py` (NEW, 13 tests)
- `tests/core/strategy/components/test_ev_gate_integration.py` (NEW, 10 tests)
- `tests/integration/test_composable_ev_gate_regression.py` (NEW, 3 tests)

### Documentation
- `docs/features/PHASE3_MILESTONE1_BLOCKER_INVESTIGATION.md` (updated status)
- `docs/features/COMPOSABLE_STRATEGY_PROJECT.md` (updated Phase 3 status)
- `docs/features/PHASE3_BUG2_FIX_SUMMARY.md` (this file)

---

## Next Steps

1. **Commit fix** with comprehensive tests
2. **Debug Bug #1** (CooldownComponent) - requires decision logging
3. **Re-run v4 validation** with corrected EVGate (should produce trades)
4. **Extended validation** (full 2024) after Bug #1 resolved

---

**Fix Status**: ✅ COMPLETE
**Test Coverage**: 26/26 passing
**Ready for**: Commit + Bug #1 debug
