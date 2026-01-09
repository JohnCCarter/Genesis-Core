# Risk Map Confidence Tuning – 2025-10-27

## Context
- Phase-7b debugging uncovered why six-month backtests reported zero trades despite relaxed Fibonacci gates and entry thresholds.
- `tmp_reason_counts.py` diagnostics showed multiple `ENTRY_LONG`/`ENTRY_SHORT` candidates with confidence hovering around 0.52–0.58 but size remained `0.0`.

## Root Cause
- Runtime risk map (`config/runtime.json`) only allocates size once confidence ≥ 0.6, stepping up at 0.7/0.8/0.9.
- Current classifier distribution (post fib fixes) does not reach those higher cells, so sizing collapses to zero.
- Backtest engine interprets zero-sized entries as “no trade”, producing the earlier zero-trade runs.

## Resolution
- Added temporary override in `tmp_relaxed_combo_ltf.json`:
  - Risk map ladder: [0.45 → 1%], [0.50 → 1.5%], [0.55 → 2%], [0.60 → 2.5%], [0.65 → 3%], [0.70 → 4%].
  - Same thresholds (`entry_conf_overall` and Fibonacci gates) as previous relaxed config.
- Re-ran six-month backtest (`python scripts/run_backtest.py --symbol tBTCUSD --timeframe 1h --start 2025-04-27 --end 2025-10-27 --config-file tmp_relaxed_combo_ltf.json --no-save`).
- Result: 5 trades, +1.41% return, risk events aligned with expected sizing (e.g., `TP1` partial fills around 1% risk).

## Implications
- Confidence thresholds and risk map need to stay synchronized after classifier/feature changes; otherwise the pipeline silently suppresses trades.
- Diagnostic tooling (`tmp_reason_counts.py`) should remain part of smoke suite to catch future sizing misalignments.
- Before promoting overrides to runtime, re-evaluate capital usage targets and potentially smooth the risk ladder based on new confidence histograms.

## Next Steps
1. Decide on production risk map (possibly adaptive) once more backtests confirm stability.
2. Re-run optimizer/backtest suites with updated sizing to validate PnL distribution.
3. Document final risk-map choice in `README.agents.md` and update SSOT when ready.
