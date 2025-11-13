### Optimization Summary

Implemented (Phase-7d):

- Feature cache
  - LRU `OrderedDict`, configurable size via `GENESIS_FEATURE_CACHE_SIZE` (default 500)
  - Optional fast-hash via `GENESIS_FAST_HASH=1` (default stays SHA256)

- Zero-copy / NumPy paths
  - Backtest engine: zero-copy windows and numpy-backed main loop
  - Indicators: `fibonacci.py`, `htf_fibonacci.py`, `volume.py` hot loops avoid `.iloc`
  - Features: `features_asof.py` avoids `.iloc` and unnecessary list↔Series conversions

- Optimizer
  - Duplicate precheck in Optuna objective, no backtest on duplicates
  - Optional JSON mtime cache via `GENESIS_OPTIMIZER_JSON_CACHE=1`

Usage:

```powershell
$Env:GENESIS_FAST_WINDOW='1'
$Env:GENESIS_PRECOMPUTE_FEATURES='1'
$Env:GENESIS_RANDOM_SEED='42'
python scripts/benchmark_backtest.py --symbol tBTCUSD --timeframe 1h --bars 1000
```

Risk notes:

- Fast-hash key is opt-in only.
- JSON mtime cache is in-memory and scoped to a single process run.
