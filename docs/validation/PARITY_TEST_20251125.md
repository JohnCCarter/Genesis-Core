# Parity Test Report - 2025-11-25

## Objective

Verify that the Optuna optimization pipeline (`core.optimizer.runner`) produces mathematically identical results to the manual backtest script (`scripts/run_backtest.py`) when given identical parameters.

## Initial Discrepancy

- **Optuna Run**: 386 trades, -0.85% return.
- **Manual Run**: 386 trades, +0.46% return.
- **Cause**: Difference in `warmup_bars`.
  - `scripts/run_backtest.py` defaults to `120` bars.
  - `config/optimizer/parity_test.yaml` specified `150` bars.
  - The 30-bar difference (30 hours) shifted the start of trading, altering the net return despite identical trade logic for the rest of the period.

## Resolution

Running the manual backtest with explicit warmup matching the Optuna config:

```powershell
python scripts/run_backtest.py ... --warmup 150
```

## Final Results (Parity Achieved)

| Metric | Optuna Runner | Manual Runner | Match |
| ------ | ------------- | ------------- | ----- |
| Trades | 386           | 386           | ✅    |
| Return | -0.85%        | -0.85%        | ✅    |
| PF     | 0.99          | 0.99          | ✅    |
| Max DD | 9.57%         | 9.57%         | ✅    |

## Conclusion

The optimization pipeline is **deterministic and accurate**. The initial mismatch was a configuration alignment issue (warmup period), not a logic or execution engine flaw.
