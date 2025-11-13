# Performance Analysis and Optimization Recommendations

## Executive Summary

This document identifies performance bottlenecks in the Genesis-Core codebase and provides specific optimization recommendations. Analysis focused on hot paths: optimizer runner, backtest engine, and feature computation.

## Critical Findings

### 1. Optimizer Runner (`src/core/optimizer/runner.py`)

#### Issue 1.1: Excessive Deep Copying
**Location:** Lines 280, 282, 286, 287  
**Impact:** High - Called for every grid value during parameter expansion  
**Status:** ✅ FIXED

**Problem:**
```python
# Before: Deepcopy even for primitive values
return [copy.deepcopy(v) for v in values]
return [copy.deepcopy(node.get("value"))]
return [copy.deepcopy(node)]
```

**Solution Implemented:**
```python
# After: Only deepcopy mutable containers
if values and any(isinstance(v, (dict, list)) for v in values):
    return [copy.deepcopy(v) for v in values]
return list(values)  # Primitives don't need deepcopy
```

**Expected Impact:** ~50% reduction in grid expansion time for configs with many primitive values

#### Issue 1.2: Trial Key Cache Size
**Location:** Lines 119-127  
**Impact:** Medium - Cache eviction every 10,000 trials  
**Status:** ⚠️ SUGGESTED

**Current Implementation:**
- Cache capped at 10,000 entries
- Eviction keeps last 8,000 entries
- Uses SHA256 hash for keys

**Recommendation:**
Consider using LRU cache from `functools.lru_cache` for automatic eviction:

```python
from functools import lru_cache

@lru_cache(maxsize=8192)
def _trial_key_cached(params_json: str) -> str:
    return params_json

def _trial_key(params: dict[str, Any]) -> str:
    canonical = canonicalize_config(params or {})
    key = json.dumps(canonical, sort_keys=True, separators=(",", ":"))
    return _trial_key_cached(key)
```

#### Issue 1.3: Repeated JSON Serialization
**Location:** Multiple locations (lines 116, 630, 705, 731, etc.)  
**Impact:** Medium - JSON dumps called multiple times for same data  
**Status:** ⚠️ SUGGESTED

**Recommendation:**
Cache serialization of frequently accessed objects or use `orjson` consistently (already imported but not always used).

### 2. Backtest Engine (`src/core/backtest/engine.py`)

#### Issue 2.1: Pandas iloc in Hot Loop
**Location:** Line 444  
**Impact:** High - Called for every bar in backtest  
**Status:** ⚠️ SUGGESTED

**Current Implementation:**
```python
for i in range(len(self.candles_df)):
    bar = self.candles_df.iloc[i]  # Slow pandas lookup
    timestamp = bar["timestamp"]
    close_price = bar["close"]
```

**Recommendation:**
Convert to numpy arrays before loop or use itertuples():

```python
# Option 1: Numpy arrays (fastest)
timestamps = self.candles_df["timestamp"].values
close_prices = self.candles_df["close"].values
for i in range(len(self.candles_df)):
    timestamp = timestamps[i]
    close_price = close_prices[i]
    # ...

# Option 2: itertuples() (cleaner, still fast)
for i, bar in enumerate(self.candles_df.itertuples(index=False)):
    if i < self.warmup_bars:
        continue
    timestamp = bar.timestamp
    close_price = bar.close
    # ...
```

**Expected Impact:** ~10-20% reduction in backtest time for typical runs

#### Issue 2.2: List Append in Equity Curve
**Location:** `position_tracker.py` line 510  
**Impact:** Low - List append is generally efficient, but pre-allocation could help  
**Status:** ℹ️ LOW PRIORITY

### 3. Feature Computation (`src/core/strategy/features_asof.py`)

#### Issue 3.1: Cache Hash Computation
**Location:** Lines 44-59  
**Impact:** Medium - Called for every feature extraction  
**Status:** ✅ ALREADY OPTIMIZED

**Current Implementation:**
- Only hashes last 100 bars (good)
- Uses numpy sum for efficiency (good)
- Cache limited to 100 entries (reasonable)

**Observation:** This is already well-optimized. No changes needed.

#### Issue 3.2: Series Creation in Hot Path
**Location:** Lines 214, 270  
**Impact:** Low - Only a few Series created per feature extraction  
**Status:** ℹ️ ACCEPTABLE

**Current Code:**
```python
atr_series = pd.Series(atr_vals) if atr_vals else pd.Series(dtype=float)
pd.Series(highs), pd.Series(lows), pd.Series(closes), fib_config
```

**Note:** Creating Series is necessary for indicator functions that expect pandas input. The performance cost is acceptable.

### 4. Position Tracker (`src/core/backtest/position_tracker.py`)

#### Issue 4.1: Multiple List Appends
**Location:** Lines 301, 306, 366, 368, 404, 493, 510  
**Impact:** Low - List append is O(1) amortized  
**Status:** ℹ️ LOW PRIORITY

**Observation:** Python's list append is already well-optimized with geometric reallocation. Pre-allocation would only help if the final size is known, which it isn't for trades/equity_curve.

## Performance Testing

### Existing Tests
- ✅ `tests/test_performance_regression.py` - Swing detection performance
- ✅ `tests/test_optimizer_performance.py` - 14 tests passing

### Recommended New Tests

1. **Grid Expansion Performance Test**
```python
def test_grid_expansion_performance():
    """Verify grid expansion completes quickly for typical configs."""
    config = {
        "param1": {"type": "grid", "values": list(range(100))},
        "param2": {"type": "grid", "values": [0.1, 0.2, 0.3]},
    }
    start = time.time()
    expansions = list(_expand_dict(config))
    elapsed = time.time() - start
    assert elapsed < 0.1  # Should be very fast for 300 combinations
```

2. **Backtest Loop Performance Test**
```python
def test_backtest_loop_performance():
    """Verify backtest loop runs at acceptable speed."""
    # Test with 1000 bars
    # Should complete in < 5 seconds for simple strategy
```

## Implementation Priority

### High Priority (Implement Now)
1. ✅ **DONE:** Optimize deepcopy in `_expand_value()`
2. 🔄 **IN PROGRESS:** Optimize backtest engine iloc usage

### Medium Priority (Next Sprint)
3. Implement LRU cache for trial keys
4. Batch JSON serialization where possible
5. Add performance regression tests for optimizer

### Low Priority (Future)
6. Review list pre-allocation opportunities
7. Profile memory usage in long optimization runs

## Measurement & Validation

### Before Optimization
- Grid expansion: ~X ms for typical config (needs baseline measurement)
- Backtest loop: ~Y seconds for 1000 bars (needs baseline measurement)
- Feature cache hit rate: Monitor via metrics

### After Optimization (Expected)
- Grid expansion: 50% faster for primitive-heavy configs
- Backtest loop: 10-20% faster with numpy array access
- No regression in test suite

## Monitoring Recommendations

1. **Add timing metrics** to critical paths:
```python
from core.observability.metrics import metrics

with metrics.timer("grid_expansion"):
    expansions = list(_expand_dict(config))
```

2. **Track cache hit rates:**
```python
# Already implemented via metrics.inc("feature_cache_hit/miss")
```

3. **Profile long-running optimizations:**
```python
# Use cProfile for detailed analysis
python -m cProfile -o profile.stats scripts/run_optimizer.py
```

## Conclusion

The codebase already demonstrates good performance practices (caching, numpy usage, etc.). The identified optimizations are incremental improvements rather than critical fixes. The main bottleneck for optimization runs is likely the inherent cost of running many backtests, not the optimizer framework itself.

**Estimated Total Impact:** 10-30% improvement in optimization run time, depending on configuration characteristics.
