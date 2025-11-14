### Performance Guide (Genesis-Core)

This guide summarizes opt-in performance switches and how to benchmark.

- Environment flags (recommended)
  - GENESIS_FAST_WINDOW=1: enable zero-copy windows in backtest engine
  - GENESIS_PRECOMPUTE_FEATURES=1: reuse precomputed indicator outputs when available
  - GENESIS_RANDOM_SEED=42: deterministic seeding for reproducibility
  - GENESIS_FEATURE_CACHE_SIZE=500: LRU size for feature cache (default 500)
  - GENESIS_FAST_HASH=1: fast feature-cache key (asof_bar:last_close); use only if exact collisions are acceptable risk for speed
  - GENESIS_OPTIMIZER_JSON_CACHE=1: cache results JSON by mtime during optimizer runs

- Quick benchmark

```bash
python scripts/benchmark_backtest.py --symbol tBTCUSD --timeframe 1h --bars 1000
```

- Notes
  - Flags are environment-based for compatibility. A thin CLI wrapper can set them if desired.
  - Fast hash mode is optional and off by default (SHA256 remains the default to minimize collision risk).
