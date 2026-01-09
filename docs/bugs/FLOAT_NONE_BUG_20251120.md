# Critical Bug: float(None) TypeError Blocking All Trades

**Date:** 2025-11-20
**Severity:** CRITICAL
**Impact:** Zero trades generated despite valid candidates
**Status:** RESOLVED

## Problem Description

The strategy was generating 0 trades across all backtests despite:

- Valid candidate selection (100+ CANDIDATE_SELECTED events)
- Candidates passing all visible gates (confidence, regime, fibonacci)
- Very loose thresholds (entry_conf 0.38, zone thresholds 0.4/0.46/0.52)

## Root Cause

Line 942 in `src/core/strategy/decision.py`:

```python
min_edge = float((cfg.get("thresholds") or {}).get("min_edge", 0.0))
```

**Problem:** When `cfg.get("thresholds")` returned a dict but that dict contained `"min_edge": None` (explicitly set to null in config), the `.get("min_edge", 0.0)` would return `None` instead of using the default `0.0`.

This caused:

```python
float(None)  # TypeError: float() argument must be a string or a real number, not 'NoneType'
```

The exception was **silently caught** by the backtest engine's error handling, returning `"NONE"` action without logging the error clearly, making it appear as if a gate was blocking trades.

## Investigation Process

1. **Initial hypothesis:** Fibonacci gates blocking (disabled them → still 0 trades)
2. **Second hypothesis:** Confidence thresholds too high (lowered to 0.38 → still 0 trades)
3. **Forensic logging:** Added debug logs at each gate to trace execution flow
4. **Discovery:** Code reached confidence gate but never reached edge gate
5. **Pinpoint:** Exception thrown at `float(None)` on min_edge calculation

## Solution

Created `safe_float()` helper function:

```python
def safe_float(value: Any, default: float = 0.0) -> float:
    """Safely convert value to float, handling None and invalid types."""
    if value is None:
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default
```

Applied fix:

```python
# BEFORE (crashes on None):
min_edge = float((cfg.get("thresholds") or {}).get("min_edge", 0.0))

# AFTER (handles None):
min_edge = safe_float((cfg.get("thresholds") or {}).get("min_edge"), 0.0)
```

## Results

**Before fix:**

- champion_base.json: 0 trades
- balanced.json: 0 trades

**After fix:**

- champion_base.json: 3 trades (-0.08%, PF 0.84, Win Rate 66.7%)
- balanced.json: 2147 trades (-31.73%, PF 0.88)

## Lessons Learned

1. **Dict.get() default doesn't protect against explicit None values**

   - `.get("key", default)` only uses default if key is missing
   - If key exists with value `None`, you get `None`, not the default

2. **Silent exception handling can hide critical bugs**

   - The TypeError was caught somewhere up the stack without clear logging
   - Made it appear as a logic issue rather than a crash

3. **Systematic debugging wins**
   - Adding forensic logging at each gate pinpointed the exact failure line
   - Try/except around suspect code revealed the TypeError

## Prevention

1. **Use `safe_float()` for all config value conversions**
2. **Add explicit None checks before float() conversions**
3. **Log exceptions with full context in decision logic**
4. **Test with configs that have explicit `null` values**

## Related Issues

- Similar pattern may exist with other config value retrievals
- Consider auditing all `float()` calls for None handling
- May want to add config schema validation to reject `null` for numeric fields

## Files Modified

- `src/core/strategy/decision.py`: Added `safe_float()` helper and applied fix
- `config/tmp/balanced.json`: Added `missing_policy: "pass"` for fib gates
- `docs/bugs/FLOAT_NONE_BUG_20251120.md`: This documentation
