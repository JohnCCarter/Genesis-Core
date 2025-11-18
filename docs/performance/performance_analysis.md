# Performance Analysis: Model Testing Code

**Date:** 2025-11-10
**Scope:** Model testing, backtest engine, and training pipeline

## Executive Summary

This document analyzes performance bottlenecks in the Genesis-Core model testing infrastructure and provides actionable optimization recommendations.

## Baseline Measurements

### Test Suite Performance (Before Optimization)
```
Total: 47.09s for 378 tests

Slowest tests:
- test_engine_processes_correct_number_of_bars: 7.04s
- test_engine_equity_curve_tracking: 7.02s
- test_engine_handles_pipeline_errors_gracefully: 6.93s
- test_engine_results_format: 6.89s
- test_engine_closes_positions_at_end: 6.88s
- test_engine_run_with_minimal_data: 6.84s
- test_train_buy_sell_models_basic: 1.58s
```

### Test Suite Performance (After Optimization)
```
Total: 44.55s for 378 tests (5.4% improvement)

Slowest tests:
- test_engine_handles_pipeline_errors_gracefully: 6.83s
- test_engine_closes_positions_at_end: 6.82s
- test_engine_run_with_minimal_data: 6.82s
- test_engine_results_format: 6.79s
- test_engine_equity_curve_tracking: 6.77s
- test_engine_processes_correct_number_of_bars: 6.77s
- test_train_buy_sell_models_basic: 0.01s (158x faster!)
```

## Implemented Optimizations

### 1. Backtest Engine - Numpy Array Pre-conversion ✅

**Problem:** DataFrame slicing with `.iloc[]` and converting each Series to list with `.tolist()` on every bar iteration.

**Performance Impact:**
```python
# Benchmark (150 iterations, window size 50):
Method 1 (iloc + tolist):        0.0147s
Method 2 (iloc + values.tolist): 0.0149s
Method 3 (numpy slicing):        0.0007s (20x faster!)
```

**Solution:** Pre-convert DataFrame columns to numpy arrays in `load_data()` and use direct array slicing:

```python
# In __init__:
self._np_arrays: dict | None = None

# In load_data():
self._np_arrays = {
    "open": self.candles_df["open"].values,
    "high": self.candles_df["high"].values,
    # ... etc
}

# In _build_candles_window():
return {
    "open": self._np_arrays["open"][start_idx:end_idx+1].tolist(),
    # ... etc
}
```

**Result:** Window building overhead reduced from ~5% to 0.4% of total runtime.

**Note:** Backtest tests still run ~6.8s because the bottleneck is in `evaluate_pipeline()` (feature extraction, model inference, decision logic), not window building. This is expected and represents actual strategy computation time.

### 2. Model Registry - Enhanced Caching ✅

**Problem:** Registry JSON file read and parsed on every `get_meta()` call.

**Solution:** Added registry-level caching with mtime-based invalidation:

```python
def __init__(...):
    self._registry_cache: dict[str, Any] | None = None
    self._registry_mtime: float | None = None

def _get_registry(self) -> dict[str, Any]:
    if self.registry_path.exists():
        mtime = self.registry_path.stat().st_mtime
        if self._registry_cache is not None and self._registry_mtime == mtime:
            return self._registry_cache
        # ... load and cache
```

**Result:** Eliminated redundant file I/O across tests that use the same registry.

### 3. Training Pipeline - Fast Mode ✅

**Problem:** `GridSearchCV` with 3-fold cross-validation runs on every test, testing 3 different C values.

**Solution:** Added `fast_mode` parameter to skip expensive hyperparameter search:

```python
def train_buy_sell_models(..., fast_mode: bool = False):
    if fast_mode:
        # Use default params, no cross-validation
        buy_model = LogisticRegression(C=1.0, ...)
        buy_model.fit(X_train, buy_y_train)
        # ...
        return buy_model, sell_model, metrics

    # Original GridSearchCV code for production use
    # ...
```

**Result:**
- test_train_buy_sell_models_basic: 1.58s → 0.01s (158x faster)
- Full train_model suite: 2.75s → 1.03s (62% reduction)

## Additional Performance Issues Identified

### 4. FVG Filter - iterrows() Usage ⚠️

**File:** `src/core/strategy/fvg_filter.py:129`

**Problem:** Using `iterrows()` which is one of the slowest pandas operations.

**Code:**
```python
for idx, row in features_df.iterrows():
    fvg_features = {
        "fvg_present": float(row.get("fvg_present", 0.0)) if not pd.isna(...) else 0.0,
        # ... more feature extraction
    }
```

**Impact:** Not used in tests, so low priority. But could be slow for production use with large datasets.

**Suggested Fix:** Use vectorized operations or `.itertuples()`:

```python
# Option 1: Vectorized (best)
fvg_present = features_df["fvg_present"].fillna(0.0).astype(float).values
fvg_size_atr = features_df["fvg_size_atr"].fillna(0.0).astype(float).values

for idx in range(len(features_df)):
    fvg_features = {
        "fvg_present": fvg_present[idx],
        "fvg_size_atr": fvg_size_atr[idx],
        # ...
    }

# Option 2: itertuples (2-10x faster than iterrows)
for row in features_df.itertuples():
    fvg_features = {
        "fvg_present": float(row.fvg_present) if not pd.isna(row.fvg_present) else 0.0,
        # ...
    }
```

### 5. Trade Logger - apply() Usage ⚠️

**File:** `src/core/backtest/trade_logger.py:94`

**Problem:** Using `.apply()` which can be slow for large DataFrames.

**Code:**
```python
trades_df["entry_reasons"] = trades_df["entry_reasons"].apply(
    lambda x: json.dumps(x) if isinstance(x, dict) else x
)
```

**Impact:** Moderate - runs once per backtest at save time.

**Suggested Fix:** Use list comprehension with values:

```python
# Faster for large DataFrames
trades_df["entry_reasons"] = [
    json.dumps(x) if isinstance(x, dict) else x
    for x in trades_df["entry_reasons"].values
]
```

### 6. Evaluate Pipeline Performance 🔍

**Observation:** The backtest engine tests spend 99.6% of time in `evaluate_pipeline()`.

**Profile breakdown (estimated):**
- Feature extraction: ~40%
- Model inference: ~30%
- Decision logic: ~20%
- Other: ~10%

**Potential optimizations:**
1. **Feature caching:** If features are computed multiple times for the same data
2. **Batch inference:** If model supports batch prediction
3. **Lazy evaluation:** Only compute features needed for decision
4. **JIT compilation:** Use Numba for hot loops in feature computation

**Next steps:** Profile `evaluate_pipeline()` in detail to identify specific bottlenecks.

## Optimization Guidelines

### When to Optimize

✅ **Optimize when:**
- Code is in hot loop (called 100+ times per test)
- Clear performance issue (>1s for simple operation)
- Used in production critical path
- Easy win with minimal code change

❌ **Don't optimize when:**
- Code is rarely called (setup/teardown)
- Already fast enough (<0.1s)
- Optimization adds significant complexity
- No clear measurement showing it's a bottleneck

### Quick Wins Checklist

For pandas operations:
- [ ] Replace `.apply()` with vectorized operations or list comprehension
- [ ] Replace `.iterrows()` with `.itertuples()` or numpy arrays
- [ ] Use `.values` when converting to lists/numpy
- [ ] Cache expensive DataFrame operations

For file I/O:
- [ ] Add caching with mtime validation
- [ ] Use binary formats (parquet, feather) over text (CSV, JSON)
- [ ] Lazy load data only when needed

For ML operations:
- [ ] Use `fast_mode` or simplified models for tests
- [ ] Cache model predictions for repeated inputs
- [ ] Use batch prediction when possible
- [ ] Consider warm_start for iterative training

## Testing Best Practices

### Fast Test Data

```python
# ✅ Good: Small synthetic data
@pytest.fixture
def sample_data():
    return pd.DataFrame({
        'close': [100 + i for i in range(50)],
        # ... minimal data
    })

# ❌ Bad: Loading full production data
def test_something():
    df = pd.read_parquet('data/full_dataset.parquet')  # 100MB+
```

### Mock Expensive Operations

```python
# ✅ Good: Mock expensive calls
@patch('core.strategy.model_registry.ModelRegistry.get_meta')
def test_evaluate(mock_get_meta):
    mock_get_meta.return_value = {...}
    # ... test logic

# ❌ Bad: Actually loading models
def test_evaluate():
    registry = ModelRegistry()
    meta = registry.get_meta(...)  # Loads from disk
```

### Parameterize for Speed

```python
# ✅ Good: Fast mode for tests
def train_model(X, y, fast_mode=False):
    if fast_mode:
        return LogisticRegression().fit(X, y)
    return GridSearchCV(...).fit(X, y)

# ❌ Bad: Always slow
def train_model(X, y):
    return GridSearchCV(...).fit(X, y)  # 3-fold CV always
```

## Measurement Tools

### Pytest Duration Report
```bash
pytest --durations=20 tests/
```

### Python Profiling
```python
import cProfile
cProfile.run('expensive_function()', 'output.prof')
```

### Line Profiler
```python
from line_profiler import LineProfiler
profiler = LineProfiler()
profiler.add_function(function_to_profile)
profiler.run('function_to_profile()')
profiler.print_stats()
```

### Memory Profiler
```python
from memory_profiler import profile

@profile
def my_func():
    # ...
```

## Recommendations

### Immediate Actions (High Impact, Low Effort)
1. ✅ **DONE:** Add numpy array caching in backtest engine
2. ✅ **DONE:** Add fast_mode to training pipeline
3. ✅ **DONE:** Enhance model registry caching
4. ⏭️ **SKIP:** Fix FVG filter iterrows (not used in tests)
5. ⏭️ **SKIP:** Fix trade logger apply (minor impact)

### Future Improvements (Medium Priority)
1. Profile evaluate_pipeline() in detail
2. Add feature computation caching
3. Implement parallel test execution
4. Create shared test fixtures for common data
5. Add performance regression tests

### Long-term Optimizations (Low Priority)
1. Use Numba JIT for hot numeric loops
2. Implement batch processing for backtests
3. Add incremental feature computation
4. Consider using Polars instead of Pandas
5. Optimize model inference with ONNX

## Conclusion

We achieved a 5.4% overall test suite speedup with targeted optimizations:
- Training tests: 62% faster
- Window building: 20x faster (but small % of total)
- Model registry: Eliminated redundant I/O

The remaining bottleneck is in strategy evaluation logic, which represents actual computation cost rather than inefficiency. Further optimization requires profiling the evaluate_pipeline() function to identify specific hot spots.

**Key takeaway:** Focus optimization efforts on frequently-called code in critical paths. Many "obvious" inefficiencies (like iterrows) may not matter if they're rarely executed.
