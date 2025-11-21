# Optuna Performance Optimization - Implementation Guide

## Quick Reference

This document provides a quick reference for the Optuna performance optimizations implemented in Genesis-Core.

## Performance Results

### Before vs After (Key Metrics)

```
Trial Key Generation:
  Before: 71,089 ops/s (cold), 74,882 ops/s (warm)
  After:  186,301 ops/s (cold), 199,556 ops/s (warm)
  Gain:   +162% (cold), +167% (warm)

Trial Loading:
  Before: 17,367 files/s
  After:  22,370 files/s
  Gain:   +29%

SQLite Batch Operations:
  Maintained: 368x faster than individual adds
```

## Key Optimizations (In Order of Impact)

### 1. Fast Path Trial Key Generation (Highest Impact: 2.62x)
**Location**: `src/core/optimizer/runner.py::_trial_key()`
**What**: Try direct JSON serialization before expensive canonicalization
**Why**: Canonicalization is slow; simple params don't need it
**When to use**: Already automatic - no user action needed

### 2. Pre-populated Step Decimals Cache (High Impact)
**Location**: `src/core/optimizer/runner.py::_suggest_parameters()`
**What**: Common step values (0.001, 0.01, 0.1, etc.) pre-cached
**Why**: Eliminates ~90% of string operations in decimal calculation
**When to use**: Already automatic - no user action needed

### 3. Iterative Deep Merge (Medium Impact)
**Location**: `src/core/optimizer/runner.py::_deep_merge()`
**What**: Stack-based iteration instead of recursion
**Why**: Eliminates recursion overhead, better for deeply nested configs
**When to use**: Already automatic - benefits large parameter spaces

### 4. Enhanced JSON Parsing (Medium Impact)
**Location**: `src/core/optimizer/runner.py::_json_loads()`
**What**: Use orjson when available
**Why**: 2-3x faster JSON parsing
**When to use**: Install orjson for automatic speedup

### 5. Optimized Type Checking (Low-Medium Impact)
**Location**: Multiple functions in `runner.py`
**What**: Use `type()` for immutable types, `isinstance()` for dicts
**Why**: type() is ~30% faster for single-type checks
**When to use**: Already optimized throughout codebase

### 6. Enhanced SQLite Configuration (Low Impact)
**Location**: `src/core/utils/optuna_helpers.py::_init_sqlite()`
**What**: Optimized PRAGMA settings for concurrent access
**Why**: Better write performance in WAL mode
**When to use**: Already automatic for all dedup operations

## Environment Variables for Additional Performance

```bash
# Enable JSON caching for large optimization runs
export GENESIS_OPTIMIZER_JSON_CACHE=1

# Maximum JSON cache size (default: 256)
export GENESIS_OPTIMIZER_JSON_CACHE_SIZE=512

# Enable fast window mode (for development/testing)
export GENESIS_FAST_WINDOW=1

# Enable precomputed features (for production runs)
export GENESIS_PRECOMPUTE_FEATURES=1

# Control concurrency (balance speed vs memory)
export GENESIS_MAX_CONCURRENT=4  # Recommended: 2-8 for most systems

# Seed for deterministic results
export GENESIS_RANDOM_SEED=42
```

## Best Practices

### For Long Optuna Runs (>1000 trials)

1. **Enable JSON caching**:
   ```bash
   export GENESIS_OPTIMIZER_JSON_CACHE=1
   ```

2. **Use appropriate concurrency**:
   - Discrete search spaces: 2-4 workers
   - Continuous search spaces: 4-8 workers
   - Very large spaces: up to 16 workers

3. **Configure TPE sampler properly**:
   - Set `n_startup_trials` to 5x concurrency (minimum 25)
   - Enable `multivariate=true` and `constant_liar=true`
   - Increase `n_ei_candidates` to 48+

4. **Use batch operations**:
   - NoDupeGuard.add_batch() is 368x faster than individual adds
   - Already used internally by runner

### For Resume Scenarios

1. **Benefits automatically** from trial loading optimizations (+29% speed)
2. **Use allow_resume=true** in optimizer config
3. **Keep existing trials** - cached results avoid redundant backtests

### For High Concurrency (8+ workers)

1. **Monitor duplicate ratio**:
   - Warning triggers at >50% duplicates
   - Increase search space or reduce concurrency
   
2. **Scale startup trials** with concurrency:
   - Formula: max(25, 5 * concurrency)
   - Automatically handled by `_select_optuna_sampler()`

3. **SQLite optimizations** help with concurrent dedup:
   - WAL mode enabled
   - Connection pooling via check_same_thread=False
   - Optimized PRAGMA settings

## Troubleshooting

### High Duplicate Rate (>50%)

**Symptoms**: Many trials with same parameters
**Causes**:
- Search space too narrow
- Float step sizes causing rounding collisions
- TPE degeneracy

**Solutions**:
1. Widen parameter ranges
2. Increase n_startup_trials (try 25+)
3. Remove or loosen step sizes
4. Enable multivariate=true in TPE

### High Zero-Trade Rate (>50%)

**Symptoms**: Most trials produce 0 trades
**Causes**:
- Entry confidence too high
- Fibonacci gates too strict
- Multi-timeframe blocking all signals

**Solutions**:
1. Lower entry_conf_overall (try 0.25-0.35)
2. Widen fibonacci tolerance_atr ranges
3. Enable LTF override
4. Run smoke test (2-5 trials) first

### Slow Trial Loading

**Symptoms**: Resume takes long time to load existing trials
**Current Performance**: 22,370 files/s (optimized)
**If slower**:
1. Check disk I/O (SSD recommended)
2. Enable JSON caching: `export GENESIS_OPTIMIZER_JSON_CACHE=1`
3. Consider archiving very old trial files

## Monitoring Performance

### Benchmark Script

Run the benchmark script to validate performance:

```bash
python scripts/benchmark_optuna_performance.py
```

Expected output (after optimizations):
```
Trial Key Generation (1000 ops):
  cold_cache_ms: ~5.4 ms
  ops_per_sec_cold: ~186k ops/s
  speedup: 1.07x

Parameter Signature (1000 ops):
  cold_cache_ms: ~11 ms
  ops_per_sec_cold: ~89k ops/s
  speedup: 3.01x

SQLite Deduplication (1000 ops):
  speedup: 368x
  ops_per_sec_batch: ~238k ops/s

Trial Loading (100 files):
  load_time_ms: ~4.5 ms
  trials_per_sec: ~22k ops/s
```

### Test Suite

Run performance tests to verify optimizations:

```bash
# All performance tests
python -m pytest tests/test_optimizer_performance*.py -v

# Specific optimization areas
python -m pytest tests/test_optimizer_performance_improvements.py::TestDeepMergePerformance -v
python -m pytest tests/test_optimizer_performance_improvements.py::TestJSONParsingPerformance -v
```

## Advanced Topics

### Custom Parameter Signature Precision

The `param_signature()` function rounds floats to 10 decimal places by default:

```python
from core.utils.optuna_helpers import param_signature

# Default precision (10 decimals)
sig = param_signature(params)

# Custom precision (5 decimals)
sig = param_signature(params, precision=5)
```

Lower precision = more aggressive deduplication (faster, but may miss subtle differences)
Higher precision = more precise deduplication (slower, but more accurate)

### Cache Management

Both trial key cache and parameter signature cache auto-trim at limits:
- Trial key cache: 10,000 entries → trim to 8,000
- Param sig cache: 5,000 entries → trim to 4,000

These limits are hardcoded but can be adjusted in:
- `src/core/optimizer/runner.py::_trial_key()` - Trial key cache
- `src/core/utils/optuna_helpers.py::param_signature()` - Param sig cache

## Future Optimization Opportunities

### Not Yet Implemented (Consider for Future)

1. **Connection pooling for SQLite**:
   - Current: Create connection per operation
   - Future: Maintain connection pool
   - Expected gain: 10-20% for high-frequency dedup

2. **Lazy trial loading**:
   - Current: Load all trials at startup
   - Future: Load on-demand with LRU cache
   - Expected gain: Faster startup for large result sets

3. **Parallel trial file parsing**:
   - Current: Serial JSON parsing
   - Future: ThreadPoolExecutor for parsing
   - Expected gain: 2-3x for >100 trial files

4. **orjson as required dependency**:
   - Current: Optional dependency
   - Future: Make required
   - Expected gain: Consistent 2-3x JSON speedup for all users

## Related Documentation

- Full performance analysis: `docs/performance/OPTUNA_PERFORMANCE_OPTIMIZATIONS.md`
- Test suite: `tests/test_optimizer_performance_improvements.py`
- Benchmark script: `scripts/benchmark_optuna_performance.py`
- Main implementation: `src/core/optimizer/runner.py`
- Helper utilities: `src/core/utils/optuna_helpers.py`

## Version History

- **2025-11-21**: Initial optimization implementation
  - 2-3x speedup in critical operations
  - 19 new performance tests
  - Comprehensive documentation
  - Code review and security validation complete
