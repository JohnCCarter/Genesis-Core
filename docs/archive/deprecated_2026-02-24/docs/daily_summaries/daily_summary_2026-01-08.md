# Daily Summary - 2026-01-08

## Summary of Work

Dagens fokus var att få bort “inerta HTF-parametrar” och Optuna-degeneracy genom att:

1. göra HTF-availability synlig i artifacts, och
2. tillhandahålla 1D-candles så HTF-exits kan aktiveras, samt
3. fixa en blockerande precompute-bugg som gjorde att smoke-runs prunades.

## Key Changes

- **1D candles (HTF input)**:

  - Lade till `scripts/curate_1d_candles.py` för att resampla 1h → 1D med UTC-daggränser.
  - Skrev ut:
    - `data/curated/v1/candles/tBTCUSD_1D.parquet`
    - `data/raw/tBTCUSD_1D_frozen.parquet`

- **Optuna / artifact-diagnostik**:

  - Lade till `scripts/analyze_optuna_run_identity.py` som:
    - läser `results/hparam_search/<run_id>/trial_###.json`
    - beräknar trade-fingerprint och grupperar identiska utfall
    - skriver ut `backtest_info.htf` för att se om HTF faktiskt var aktivt

- **Backtest HTF-status i results**:

  - `src/core/backtest/engine.py`: inkluderar `backtest_info.htf` (t.ex. `htf_candles_loaded`, `use_new_exit_engine`, `htf_context_seen`).

- **Bugfix: precompute cache-hit + HTF mapping**:
  - Root cause: `fib_cfg` definierades bara i cache-miss path och blev odefinierad vid cache-hit.
  - Fix: `src/core/backtest/engine.py` definierar nu `fib_cfg` innan cache-branching.
  - Test: `tests/test_backtest_engine.py::test_engine_precompute_cache_hit_htf_mapping_does_not_require_local_fib_cfg`.

## Verification

- Riktat pytest-test för regressionen passerar.
- Smoke-run med `GENESIS_FAST_WINDOW=1`, `GENESIS_PRECOMPUTE_FEATURES=1`, `GENESIS_HTF_EXITS=1` når:

  - `Precompute: mapping HTF Fibonacci levels`
  - `Precompute: HTF Fibonacci mapping complete`

- Identitetsanalys på senaste smoke-run visar `htf_candles_loaded=True` men fortfarande 0 trades i fönstret (dvs kvarvarande problem är thresholds/gates/period snarare än HTF/precompute).

## Next Steps

- **Få igenom minst några trades i smoke-fönstret**:
  - Sänk/vidga entry-trösklar eller kör ett längre sample-range så vi inte drar slutsatser på 43 bars efter warmup.
- **Verifiera HTF-context-flöde**:
  - Sikta på att se `backtest_info.htf.htf_context_seen=True` i åtminstone någon run.
- **Re-run identity check**:
  - Kör `scripts/analyze_optuna_run_identity.py` på nya run-dir och följ hur identitetsgrupper förändras när HTF påverkar exits.
