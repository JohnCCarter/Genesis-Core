# Research code experiment RI regime calibration slice 1 execution review

Date: 2026-03-27
Status: tracked / partial execution complete / full classification blocked
Lane: `run_intent: research_code_experiment`
Slice: `ri regime calibration slice 1`

## Result

- The code-level research seam is implemented and verified.
- Full backtest classification of the hypothesis is blocked on missing local market data.

## What completed successfully

- An explicit research-only override seam now exists for isolated model metadata.
- Active production model metadata paths under `config/models/**` are rejected for research override use.
- Default behavior remains unchanged when no research override path is supplied.
- Research-only override requires `run_intent: research_code_experiment`.

## Verification completed

- `black --check` PASS
- `ruff check` PASS
- `pytest -q tests/integration/test_prob_model_integration.py tests/backtest/test_evaluate_pipeline_config_isolation.py tests/governance/test_regime_intelligence_cutover_parity.py::test_cutover_pipeline_hash_stability` PASS

## What blocked full classification

- The bounded control backtest for `tBTCUSD 3h` on `2024-07-01..2024-12-31` failed before execution because no local parquet candle data was available.
- The engine reported no file at:
  - `data/raw/tBTCUSD_3h_frozen.parquet`
  - `data/curated/v1/candles/tBTCUSD_3h.parquet`
  - `data/candles/tBTCUSD_3h.parquet`

## Decision

- Do not claim `improvement`, `plateau`, or `degradation` from backtest performance yet.
- Classify the slice as:
  - seam implementation: complete
  - full hypothesis execution: blocked by missing data

## Next admissible move

- provide or materialize the required `tBTCUSD 3h` candle data on one of the expected non-production local data paths
- then rerun the already prepared control and candidate research backtests without widening scope
