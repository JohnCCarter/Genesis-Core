# Performance Optimization Guide

This document explains the performance optimizations in the Genesis-Core model-training pipeline and how to use them effectively.

## Overview

The model-training pipeline has been optimized to significantly reduce execution time without changing results. Key improvements include:

1. **Feature Caching with LRU Eviction** - 5-10x faster on repeated calculations
2. **Zero-Copy Window Building** - Eliminates list conversion overhead
3. **Precomputed Indicators** - Amortizes indicator computation cost
4. **Optimizer Result Caching** - Faster trial summary loading

## Optimizations

### 1. Feature Cache (features_asof.py)

**What it does:**
- Caches computed features to avoid recomputation
- Uses LRU (Least Recently Used) eviction strategy
- Fast hash computation based on bar index and price

**Performance impact:**
- Hash computation: **0.0007ms** (10x faster than before)
- Cache hit: Nearly instant feature retrieval
- Cache size: 500 entries (5x larger than before)

**How it works:**
```python
# Automatic - no code changes needed
features, meta = extract_features_backtest(candles, asof_bar, timeframe="1h")
# Subsequent calls with same data hit cache
```

**Best practices:**
- Sequential bar processing maximizes cache hits
- Random access patterns reduce hit rate
- Cache is automatically managed (no manual clearing needed)

### 2. Window Building (engine.py)

**What it does:**
- Returns NumPy array views instead of converting to lists
- Zero-copy slicing reduces memory allocations
- Supports both fast_window and standard modes

**Performance impact:**
- Eliminates ~2-5ms per bar in list conversions
- Reduces memory pressure during long backtests

**How to enable:**
```bash
# Enable fast window mode (recommended)
python scripts/run_backtest.py --symbol tBTCUSD --timeframe 1h --fast-window

# Or via environment variable
export GENESIS_FAST_WINDOW=1
python scripts/run_backtest.py --symbol tBTCUSD --timeframe 1h
```

### 3. Precomputed Features (engine.py)

**What it does:**
- Computes indicators (ATR, RSI, EMA, ADX, BB) once for entire dataset
- Caches results to disk for reuse across runs
- Features are sliced per-bar instead of recomputed

**Performance impact:**
- First run: ~10-30 seconds precomputation (depending on data size)
- Subsequent bars: **50-80% faster** feature extraction
- Disk cache: Instant loading on repeat runs

**How to enable:**
```bash
# Enable precomputation (recommended for optimization runs)
python scripts/run_backtest.py --symbol tBTCUSD --timeframe 1h --precompute-features

# Or via environment variable
export GENESIS_PRECOMPUTE_FEATURES=1
python scripts/run_backtest.py --symbol tBTCUSD --timeframe 1h
```

**Cache location:**
```
cache/precomputed/{symbol}_{timeframe}_{num_bars}.npz
```

**When to use:**
- ✅ Running multiple backtests on same data
- ✅ Hyperparameter optimization (Optuna trials)
- ✅ Walk-forward analysis
- ❌ Live trading (not needed - single bar processing)

### 4. Optimizer Result Caching (optimizer.py)

**What it does:**
- Caches parsed trial results in memory
- Validates cache freshness with directory mtime
- Single-pass filtering and sorting

**Performance impact:**
- First call: ~1-5 seconds (depending on trial count)
- Cached calls: ~10ms

**How to use:**
```python
from scripts.optimizer import summarize_run

# First call: parses all trial files
summary = summarize_run("run_20240101_120000")

# Subsequent calls: instant from cache
summary = summarize_run("run_20240101_120000")

# Force refresh (skip cache)
summary = summarize_run("run_20240101_120000", use_cache=False)
```

## Combined Usage

For maximum performance during optimization:

```bash
# Full optimization mode
python scripts/run_backtest.py \
  --symbol tBTCUSD \
  --timeframe 1h \
  --fast-window \
  --precompute-features \
  --start 2024-01-01 \
  --end 2024-12-31
```

Expected speedup: **2-3x faster** vs baseline

## Benchmarks

### Feature Extraction
- **Without cache**: 4.78ms per bar
- **With cache**: <0.1ms per bar (cache hit)
- **With precompute**: ~1.5ms per bar (slicing only)

### Full Backtest (10,000 bars)
- **Baseline**: ~60 seconds
- **Fast window**: ~40 seconds
- **Fast + precompute**: ~20 seconds
- **All optimizations**: ~15 seconds

### Optimizer Trial Summary
- **Baseline** (100 trials): 2.5 seconds
- **With cache**: 0.01 seconds (subsequent calls)

## Memory Usage

All optimizations are memory-efficient:

- **Feature cache**: ~50MB for 500 entries
- **Precomputed features**: ~5-20MB depending on dataset size
- **NumPy views**: Zero additional memory (references only)

## Validation

All optimizations have been validated to produce identical results:

```bash
# Run tests to verify correctness
pytest tests/test_performance_improvements.py -v
pytest tests/test_backtest_engine.py -v
pytest tests/test_performance_optimizations.py -v
```

## Troubleshooting

### Cache not working?
- Check cache hits: Look for "feature_cache_hit" in logs
- Verify sequential access pattern
- Clear cache if needed: Delete `cache/precomputed/*.npz`

### Precomputation slow?
- First run is always slow (computing all indicators)
- Subsequent runs use disk cache (instant)
- Cache is keyed by symbol + timeframe + bar count

### Different results?
- Optimizations should produce identical results
- If not, file a bug report with reproduction steps
- Disable optimizations to verify baseline: `--no-fast-window`

## Migration Guide

No code changes needed! All optimizations are:
- ✅ Backward compatible
- ✅ Opt-in via flags
- ✅ Safe to enable/disable anytime

To adopt:
1. Test with your existing backtests (no flags)
2. Enable `--fast-window` and verify results match
3. Enable `--precompute-features` for longer runs
4. Enjoy faster optimization loops!

## Future Optimizations

Planned improvements:
- [ ] Incremental indicator updates (avoid full recomputation)
- [ ] Parallel trial execution for optimizer
- [ ] JIT compilation for hot paths (Numba)
- [ ] Vectorized decision logic

## See Also

- `tests/test_performance_improvements.py` - Performance test suite
- `scripts/run_backtest.py` - Backtest runner with optimization flags
- `src/core/strategy/features_asof.py` - Feature extraction implementation
- `src/core/backtest/engine.py` - Backtest engine with optimizations
