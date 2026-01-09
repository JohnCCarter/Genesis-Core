# Phase 2d Optimization Summary (2025-11-21)

## Status: SUCCESS (Trades Unlocked)

After correcting the "Phase 2d" configuration (v6 - Lowered Thresholds), the optimization successfully generated trades, resolving the "Zero Trades" issue that plagued v5.

### Key Results (Run `run_20251121_103811`)

- **Total Trials**: 50
- **Valid Trials**: 0 (All failed strict constraints PF > 1.1 / DD < 0.25)
- **Trade Volume**: Healthy (~100-120 trades/year)
- **Profit Factor**: Low (~0.96 - 1.04)
- **Win Rate**: ~20-22%
- **Drawdown**: ~5-15%

### Best Trials (Relative Performance)

| Trial   | Score (Raw) | Trades | Return | PF   | DD    | Params (Key)                           |
| ------- | ----------- | ------ | ------ | ---- | ----- | -------------------------------------- |
| **001** | -150.09     | 107    | +1.41% | 1.04 | 5.6%  | Entry 0.28, LowZone 0.26, MidZone 0.30 |
| **040** | -150.11     | 119    | +1.64% | 1.03 | 11.1% | Entry 0.26, LowZone 0.22, MidZone 0.28 |
| **025** | -150.13     | 119    | +0.97% | 1.02 | 7.9%  | Entry 0.26, LowZone 0.24, MidZone 0.28 |

### Analysis

1.  **Thresholds are Viable**: The lowered thresholds (Entry ~0.24-0.28, Zones ~0.22-0.30) are correctly identifying market activity.
2.  **Quality is Marginal**: The strategy is breaking even. To become profitable (PF > 1.5), we need to filter out the losing trades without losing the winners.
3.  **Search Space**: The current space is "Trade Rich but Profit Poor".

### Next Steps: Phase 3 (Fine Tuning)

We will launch a **Phase 3 Optimization** focused on quality improvement.

- **Center Point**: Based on Trial 001/040.
- **Strategy**:
  - **Slightly Tighten Entry**: Raise `entry_conf` slightly (e.g., 0.26-0.32).
  - **Optimize Exits**: Focus heavily on `exit_conf_threshold`, `max_hold_bars`, and `trailing_stop`.
  - **Risk Management**: Tune `risk_map` to bet heavier on high-confidence setups.

### Recommended Configuration (Phase 3)

```yaml
thresholds:
  entry_conf_overall: 0.26 - 0.32
  signal_adaptation:
    zones:
      low: 0.24 - 0.30
      mid: 0.28 - 0.34
      high: 0.34 - 0.40
exit:
  exit_conf_threshold: 0.35 - 0.50 # Wider search here
  max_hold_bars: 12 - 48 # Wider search here
```
