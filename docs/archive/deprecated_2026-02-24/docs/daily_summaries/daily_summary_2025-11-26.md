# Daily Summary - 2025-11-26

## 1. Critical Findings

### Optimizer vs Manual Backtest Discrepancy Solved

- **Issue:** Manual backtests of Trial 1032 produced -16.65% return (1065 trades), while the optimizer reported +22.75% return (386 trades).
- **Root Cause:** The optimizer runs with specific environment variables (`GENESIS_FAST_WINDOW=1`, `GENESIS_PRECOMPUTE_FEATURES=1`) that trigger a "fast mode" in the feature calculation and backtest engine. Manual runs default to a "streaming mode" which behaves differently.
- **Resolution:** Confirmed that running manual backtests with these environment variables reproduces the optimizer's results exactly (+22.75%).
- **Action:** Created `scripts/run_backtest_fast.py` to easily run manual backtests in this mode.

## 2. New Tools & Scripts

- `scripts/run_backtest_fast.py`: A wrapper around `run_backtest.py` that automatically sets the required environment variables for reproducing optimizer results.
- `scripts/reproduce_trial_subprocess.py`: A forensic script used to isolate the issue, now restored to a working state for verification.

## 3. Documentation

- Created `docs/bugs/OPTIMIZER_REPRODUCTION_ENV_VARS_20251126.md` detailing the issue, root cause, and solution.

## 4. Next Steps

- Always use `scripts/run_backtest_fast.py` or manually set `GENESIS_FAST_WINDOW=1` and `GENESIS_PRECOMPUTE_FEATURES=1` when validating optimizer trials.
- Investigate why the "streaming mode" (default) diverges so significantly from the "fast mode". Ideally, they should produce identical results.

## 5. Feature Parity Investigation (LTF Fibonacci)

- **Change:** `src/core/strategy/features_asof.py` filtrerar nu bort prekompade swing-serier när `_global_index` visar att backtestfönstret börjar mitt i historiken (`window_start_idx > 0`). I dessa fall kör både streaming och precompute samma lokala swing-detektion (slow path).
- **Resultat:** `python scripts/diagnose_feature_parity.py --start-bar 190 --bars 40 --warmup 150 --config config/strategy/champions/tBTCUSD_1h.json` visar fortfarande 7 differenser (bar 210–228). ATR-paritet är redan verifierad, så kvarvarande avvikelser beror på LTF-swing-detektionen snarare än volatilitet eller HTF-data.
- **Observations:** När env-flaggan `GENESIS_PRECOMPUTE_FEATURES=1` sätts samtidigt som precompute-serier filtreras bort leder det till `RuntimeError: ... precomputed_features is empty`. I pipelinekörningar inträffar inte detta, men i manuella REPL-test behöver vi antingen slå av flaggan eller behålla endast de precompute-fält som faktiskt används.

## 6. Documentation Updates

- `AGENTS.md` uppdaterades med ett nytt "LTF PARITY INVESTIGATION"-avsnitt som beskriver det nya filtret, resultaten från diagnos-skriptet samt rekommenderade nästa steg (dumpa `swing_high/low` och instrumentera `debug_fib_flow`).

## 7. Outstanding Actions

1. Instrumentera `scripts/diagnose_feature_parity.py` eller `debug_fib_flow` för att logga `swing_high_idx/low_idx`, nivåer och toleranser per bar i både streaming- och precompute-läge.
2. Kör ytterligare paritetsdiagnostik efter instrumentation för att isolera varför bar 210–228 fortsätter att diffa.
3. Undersök om en hybridlösning där endast `fib_*`-serier filtreras (och övriga precompute-fält behålls) ger bättre balans mellan paritetskrav och performance.
