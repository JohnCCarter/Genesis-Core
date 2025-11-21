# Optuna Performance Analysis - Additional Opportunities

## Executive Summary

Analysis of `src/core/optimizer/runner.py` identifies **3 additional optimization opportunities** beyond the extensive optimizations already implemented. These focus on reducing redundant operations during trial execution.

## Context

Previous optimizations already achieved significant improvements:
- Trial key caching (1.25x speedup)
- Optimized trial loading (50% faster)
- SQLite batch operations (402x speedup)
- Parameter signature caching (3x speedup)

## New Optimization Opportunities

### 1. Cache Default Configuration Loading ⭐ **HIGH IMPACT**

**Location:** `runner.py` lines 601-605

**Problem:**
```python
# Called for EVERY trial
from core.config.authority import ConfigAuthority

authority = ConfigAuthority()
default_cfg_obj, _, _ = authority.get()
default_cfg = default_cfg_obj.model_dump()
```

The default configuration is loaded from disk and converted to dict for every single trial, even though it never changes during an optimization run.

**Impact Analysis:**
- For 100 trials: 100 redundant file reads + 100 Pydantic model dumps
- For 1000 trials: 1000 redundant operations
- Each `model_dump()` is expensive (validates and serializes entire config tree)

**Solution:**
```python
# Module-level cache
_DEFAULT_CONFIG_CACHE: dict[str, Any] | None = None
_DEFAULT_CONFIG_LOCK = threading.Lock()

def _get_default_config() -> dict[str, Any]:
    """Get default config with thread-safe caching."""
    global _DEFAULT_CONFIG_CACHE
    
    with _DEFAULT_CONFIG_LOCK:
        if _DEFAULT_CONFIG_CACHE is None:
            from core.config.authority import ConfigAuthority
            authority = ConfigAuthority()
            default_cfg_obj, _, _ = authority.get()
            _DEFAULT_CONFIG_CACHE = default_cfg_obj.model_dump()
        return _DEFAULT_CONFIG_CACHE

# In run_trial:
default_cfg = _get_default_config()
```

**Expected Impact:**
- **Estimated savings: 1-2s per 100 trials** (depending on config complexity)
- Eliminates N file reads where N = trial count
- Eliminates N expensive Pydantic serializations
- Thread-safe for concurrent trial execution

**Risk:** LOW - Default config doesn't change during optimization runs

### 2. Avoid Redundant glob() Operations

**Location:** `runner.py` lines 696-700

**Problem:**
```python
results_path = sorted(
    (Path(__file__).resolve().parents[3] / "results" / "backtests").glob(
        f"{trial.symbol}_{trial.timeframe}_*.json"
    )
)[-1]
```

After every successful backtest, `glob()` searches the entire directory to find the newest file. This becomes slower as the directory accumulates results files.

**Impact Analysis:**
- Directory listing is O(n) where n = number of result files
- For 1000 trials in same dir: each glob scans 1000+ files
- Cumulative cost grows quadratically

**Solution:**
The backtest script should return the result file path directly (check if it already does). If not:

```python
# Option 1: Use predictable naming with timestamp
results_path = results_dir / f"{trial.symbol}_{trial.timeframe}_{timestamp}.json"

# Option 2: Pass output path to backtest script
cmd.extend(["--output-file", str(results_path)])
```

**Expected Impact:**
- **Estimated savings: 0.5-1s per 100 trials** (grows with trial count)
- Eliminates O(n) directory scans
- More predictable performance

**Risk:** MEDIUM - Requires coordination with backtest script

### 3. Optimize _expand_dict for Large Search Spaces

**Location:** `runner.py` lines 361-374

**Problem:**
```python
def _expand_dict(spec: dict[str, Any]) -> Iterable[dict[str, Any]]:
    items = [(key, _expand_value(value)) for key, value in spec.items()]

    def _recurse(idx: int, current: dict[str, Any]) -> Iterable[dict[str, Any]]:
        if idx >= len(items):
            yield current
            return
        key, values = items[idx]
        for value in values:
            next_config = dict(current)  # Creates new dict every recursion
            next_config[key] = value
            yield from _recurse(idx + 1, next_config)
```

Creates a new dictionary at every recursion level. For large search spaces, this allocates many intermediate dictionaries.

**Impact Analysis:**
- For search space with 5 parameters × 10 values each = 100,000 configs
- Creates 5 × 100,000 = 500,000 intermediate dictionaries
- Most garbage collected immediately

**Solution:**
Use in-place modification with backtracking:

```python
def _expand_dict(spec: dict[str, Any]) -> Iterable[dict[str, Any]]:
    items = [(key, _expand_value(value)) for key, value in spec.items()]
    
    def _recurse(idx: int, current: dict[str, Any]) -> Iterable[dict[str, Any]]:
        if idx >= len(items):
            yield dict(current)  # Only copy at leaf nodes
            return
        key, values = items[idx]
        for value in values:
            current[key] = value  # Modify in place
            yield from _recurse(idx + 1, current)
            # Backtrack handled by next iteration
```

**Expected Impact:**
- **Estimated savings: 0.2-0.5s for large grid searches** (10k+ configs)
- Reduces memory allocations by 80%
- Minimal benefit for small search spaces

**Risk:** LOW - Well-tested pattern, only affects grid search

## Priority Ranking

1. **Cache Default Configuration** (HIGH priority)
   - Affects every trial
   - Easy to implement
   - Low risk
   - Clear performance benefit

2. **Avoid Redundant glob()** (MEDIUM priority)
   - Impact grows with trial count
   - Requires coordination with backtest script
   - Medium risk

3. **Optimize _expand_dict** (LOW priority)
   - Only affects grid search initialization
   - Small impact unless search space is massive
   - Low risk

## Implementation Plan

### Phase 1: Cache Default Config (Recommended)
1. Add `_get_default_config()` function with thread-safe cache
2. Replace direct ConfigAuthority usage in `run_trial()`
3. Add test validating cache behavior
4. Measure impact on 100-trial optimization run

### Phase 2: Results Path Optimization (Optional)
1. Check if backtest script can return result path
2. If yes, capture and use it directly
3. If no, consider passing output path as argument
4. Test with concurrent trials to ensure no conflicts

### Phase 3: Grid Expansion (Optional)
1. Implement in-place modification with backtracking
2. Add regression test with large search space
3. Validate no behavior changes

## Benchmarking

To validate these optimizations:

```python
# Test default config caching
import time
from core.config.authority import ConfigAuthority

# Measure without cache
times_cold = []
for _ in range(100):
    start = time.perf_counter()
    authority = ConfigAuthority()
    cfg_obj, _, _ = authority.get()
    cfg = cfg_obj.model_dump()
    times_cold.append(time.perf_counter() - start)

print(f"Cold config load: {sum(times_cold):.3f}s for 100 iterations")

# Measure with cache
_cache = None
times_warm = []
for _ in range(100):
    start = time.perf_counter()
    if _cache is None:
        authority = ConfigAuthority()
        cfg_obj, _, _ = authority.get()
        _cache = cfg_obj.model_dump()
    cfg = _cache
    times_warm.append(time.perf_counter() - start)

print(f"Cached config load: {sum(times_warm):.3f}s for 100 iterations")
print(f"Speedup: {sum(times_cold) / sum(times_warm):.1f}x")
```

## Existing Optimizations (Already Implemented)

For reference, these optimizations are already in place:

✅ Trial key caching with thread-safe LRU (10k entries)
✅ Optimized trial loading with pre-allocated dicts
✅ Step decimal caching for parameter suggestions
✅ Batched metadata updates (40% fewer file I/O)
✅ SQLite WAL mode + 10MB cache + batch operations (402x speedup)
✅ Parameter signature caching with LRU (5k entries)
✅ Single-pass trial processing
✅ JSON mtime caching (opt-in via env var)
✅ Progress bar disabled for batch runs

## Conclusion

The primary optimization opportunity is **caching the default configuration**, which will provide consistent benefits for all optimization runs with minimal risk. The other opportunities are lower priority but may be worth implementing for very large-scale optimizations (1000+ trials).

**Estimated Total Impact:** 1.5-3.5s savings per 100 trials (1.5-3.5% for typical 100s runs)

## References

- Existing optimizations: `docs/optuna/OPTUNA_PERFORMANCE_SUMMARY.md`
- Benchmark script: `scripts/benchmark_optuna_performance.py`
- Runner implementation: `src/core/optimizer/runner.py`
