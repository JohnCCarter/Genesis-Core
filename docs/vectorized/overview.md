# Vectorized Overview

## Syfte

- Snabbare feature-beräkning (25-50×) via `calculate_all_features_vectorized()`
- Möjlighet att använda precomputade features i backtest och Optuna

## Mål

1. Feature-paritet mot `_extract_asof()` (inkl. HTF/LTF meta)
2. Flagga i pipeline/backtest (`use_vectorized_features`)
3. Cache-workflow för precompute (Feather/Parquet)
4. Paritetstester (scripts + pytest)
5. Dokumentation i AGENTS/CHANGELOG + här

## Flagga

- `RuntimeConfig.vectorized.use_cache` styr om `_extract_vectorized()` ska nyttjas.
- `RuntimeConfig.vectorized.version` (default `v17`) väljer vilken precompute-version som laddas via `load_features()`.
- `RuntimeConfig.vectorized.path` kan peka på en explicit Feather/Parquet-fil för ad hoc-körningar.
- CLI: `scripts/run_backtest.py` accepterar `--use-vectorized`, `--vectorized-cache` och `--vectorized-version` och sätter ovanstående värden innan backtest startar.
- Optimizer: ange `meta.vectorized` i `config/optimizer/*.yaml` för att slå på samma flagga i Optuna/grid-körningar.

## Nyckelskript

- `scripts/precompute_features_fast.py`
- `scripts/validate_vectorized_features.py`
- (kommande) `scripts/compare_vectorized_vs_live.py`
