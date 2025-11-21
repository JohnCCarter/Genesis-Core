# Performance Improvements 2025-11-21

## Summary

This document describes performance optimizations implemented on 2025-11-21 to reduce bottlenecks identified through profiling analysis of the Genesis-Core backtest engine.

## Profiling Analysis

**Baseline (before optimizations):**
- Total runtime: 100.7 seconds
- Function calls: 75M
- Data source: `reports/profiling/golden_run_after.cprofile`

**Key Bottlenecks Identified:**

1. **Champion Loader Cache**: 8.2s spent in file I/O (123K `nt.stat()` calls)
2. **Percentile Calculations**: 10.6s spent in `numpy.percentile()` (103K calls)
3. **Pandas Series Creation**: 19.6s spent creating pandas Series unnecessarily

## Optimizations Implemented

### 1. Champion Loader Cache Fix

**Problem:**
The `_needs_reload()` method had debug code that always returned `True` when a champion file existed, completely disabling the cache. This caused 17K+ unnecessary file system calls per backtest run.

**Solution:**
```python
# Before (always reloaded)
if exists and entry.exists:
    return True  # Debug code - always reload

# After (only reload on modification)
if entry.exists != exists:
    return True
if exists and entry.mtime != mtime:
    return True
return False
```

**Impact:**
- Reduced file I/O from 17K+ stat calls to ~1 per champion
- Cache hits are now ~1000x faster than disk reads
- **Estimated speedup: 8s → ~0s (8s saved)**

**File Changed:** `src/core/strategy/champion_loader.py`

**Test Coverage:** `tests/test_performance_improvements_2025.py::TestChampionLoaderCache`

### 2. Batch Percentile Calculations

**Problem:**
Computing two percentiles (p40 and p80) required two separate `np.percentile()` calls, each with its own sorting overhead.

**Solution:**
```python
# Before (two separate calls)
"p40": float(np.percentile(window, 40)),
"p80": float(np.percentile(window, 80)),

# After (single batched call)
p40, p80 = np.percentile(window, [40, 80])
atr_percentiles[str(period)] = {
    "p40": float(p40),
    "p80": float(p80),
}
```

**Impact:**
- Single sort operation instead of two
- Reduced numpy function call overhead
- **Estimated speedup: 10.6s → ~5.3s (50% reduction, ~5.3s saved)**

**File Changed:** `src/core/strategy/features_asof.py`

**Test Coverage:** `tests/test_performance_improvements_2025.py::TestPercentileOptimization`

### 3. Avoid Redundant Pandas Series Creation

**Problem:**
The `_to_series()` function was creating new pandas Series even when the input was already a pandas Series, causing unnecessary memory allocations and type conversions.

**Solution:**
```python
# Before (always creates new Series)
highs = pd.Series([float(x) for x in data.get("high", [])])

# After (reuses existing Series)
high_data = data.get("high", [])
if isinstance(high_data, pd.Series):
    highs = high_data
else:
    highs = pd.Series(high_data, dtype=float)
```

**Impact:**
- Eliminated redundant Series creation for OHLCV data
- Reduced memory allocations
- **Estimated speedup: 19.6s → reduced (significant portion eliminated)**

**File Changed:** `src/core/indicators/htf_fibonacci.py`

**Test Coverage:** `tests/test_performance_improvements_2025.py::TestPandasSeriesOptimization`

## Overall Impact

**Expected Runtime Improvement:**
- Champion loader cache: ~8s saved
- Percentile batch: ~5.3s saved  
- Series optimization: ~4-6s saved (estimated)
- **Total estimated savings: 17-19s (15-19% improvement)**

**Expected new runtime: ~81-84 seconds** (from 100.7s baseline)

## Validation

### Test Results
```bash
$ pytest tests/test_performance_improvements_2025.py -v
================================================= test session starts ==================================================
tests/test_performance_improvements_2025.py::TestChampionLoaderCache::test_cache_prevents_redundant_file_stats PASSED
tests/test_performance_improvements_2025.py::TestChampionLoaderCache::test_cache_detects_file_modifications PASSED
tests/test_performance_improvements_2025.py::TestPercentileOptimization::test_batch_percentile_faster_than_separate PASSED
tests/test_performance_improvements_2025.py::TestPercentileOptimization::test_batch_percentile_correctness PASSED
tests/test_performance_improvements_2025.py::TestPandasSeriesOptimization::test_to_series_avoids_redundant_series_creation PASSED
tests/test_performance_improvements_2025.py::TestPandasSeriesOptimization::test_to_series_creates_series_when_needed PASSED
tests/test_performance_improvements_2025.py::TestPandasSeriesOptimization::test_to_series_performance_with_series_input PASSED
================================================== 7 passed in 0.42s ===================================================
```

### Full Test Suite
```bash
$ pytest -x --ignore=tests/test_rest_public_symbols.py --ignore=tests/test_ws_public_symbols.py
453 passed, 1 skipped in 11.95s
```

All existing tests continue to pass, confirming no regressions.

## Future Optimization Opportunities

Based on profiling, remaining bottlenecks to address:

1. **DataFrame Column Access** (8.5s): 34K calls to pandas `__getitem__`
   - Already has `fast_window` mode that pre-extracts arrays
   - Ensure `fast_window=True` is used in production backtests
   
2. **Feature Cache Fingerprinting** (6.8s): 17K calls to `make_indicator_fingerprint`
   - Consider simplifying fingerprint algorithm
   - Cache fingerprints for unchanged data windows
   
3. **JSON Encoding** (0.9s): 17K JSON encode operations
   - Consider using `orjson` (already attempted in code)
   - Batch or reduce frequency of JSON operations

## Recommendations

1. **Always use fast_window mode**: Set `GENESIS_FAST_WINDOW=1` environment variable
2. **Enable precompute features**: Set `GENESIS_PRECOMPUTE_FEATURES=1` 
3. **Monitor cache hit rates**: Add metrics for champion loader cache effectiveness
4. **Profile regularly**: Run profiling after significant changes to catch new bottlenecks

## References

- Profiling data: `reports/profiling/golden_run_after.cprofile`
- Previous optimizations: `docs/performance/PERFORMANCE_OPTIMIZATION_SUMMARY_.md`
- Test suite: `tests/test_performance_improvements_2025.py`
