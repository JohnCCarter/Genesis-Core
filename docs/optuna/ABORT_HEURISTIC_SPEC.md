# Abort Heuristic Specification

## Purpose

Prevent wasted compute on trials that will produce zero or very few trades due to overly restrictive thresholds.

## Trigger Conditions

### Early Abort (After 25% of backtest period)

Abort trial if **all** conditions met:

- `num_trades == 0` after processing ≥25% of bars
- `entry_conf_overall` ≥ 0.35 OR `signal_adaptation.zones.low.entry_conf_overall` ≥ 0.28
- `min_edge` ≥ 0.015

**Rationale:** If no trades after 25% with high thresholds, unlikely to recover.

### Mid-Point Abort (After 50% of backtest period)

Abort trial if:

- `num_trades <= 2` after processing ≥50% of bars
- Projected total trades < `min_trades` constraint

**Projection Formula:**

```python
projected_trades = (num_trades / bars_processed) * total_bars
if projected_trades < min_trades_constraint:
    abort()
```

## Implementation Location

### Option A: In BacktestEngine (Preferred)

- Add callback hook in `BacktestEngine.run()` loop
- Check conditions every N bars (e.g., N=50)
- Raise `TrialAbortedException` on trigger
- Runner catches and logs as "aborted_early"

### Option B: In Runner (Simpler)

- Post-backtest check (no early abort)
- If conditions met, mark trial as "zero_trade_preflight_failed"
- Skip constraint scoring, return large negative penalty

## Configuration (YAML)

```yaml
abort_heuristic:
  enabled: true
  early_abort:
    enabled: true
    min_progress_pct: 0.25
    max_entry_conf: 0.35
    max_low_zone_conf: 0.28
    max_min_edge: 0.015
  midpoint_abort:
    enabled: true
    min_progress_pct: 0.50
    min_trades_threshold: 2
```

## Metrics Impact

Aborted trials should be tracked separately:

```json
{
  "total_trials": 20,
  "completed": 17,
  "aborted_early": 2,
  "aborted_midpoint": 1,
  "constraints_ok": 15,
  "constraints_ok_rate": 0.88
}
```

## Penalty Value

- **Early abort:** Return score `-500` (worse than soft constraint penalty)
- **Midpoint abort:** Return score `-250`
- **Zero trades completed:** Return score `-100` (current behavior)

## Integration Steps

1. Add `abort_heuristic` config schema to `OptunaConfig` (optional section)
2. Implement `_check_abort_conditions()` in `BacktestEngine`
3. Add `TrialAbortedException` exception class
4. Update runner to catch and handle abort exceptions
5. Log abort reasons in trial JSON: `"abort_reason": "early_no_trades"`
6. Add abort metrics to summary aggregation

## Testing

Create test config with deliberately restrictive thresholds:

```yaml
thresholds:
  entry_conf_overall: 0.50 # Too high
  min_edge: 0.025 # Too high
```

Expected: Trial aborted after 25% with score -500.

## Rollout Strategy

1. **Phase 1:** Implement Option B (post-backtest check) for immediate safety
2. **Phase 2:** Test with restrictive configs, validate metrics
3. **Phase 3:** Implement Option A (in-engine abort) for compute savings
4. **Phase 4:** Enable by default with conservative thresholds

## Notes

- Heuristic should be **conservative** to avoid false positives
- Log detailed abort reasons for debugging
- Track abort rate in metrics (warn if >20%)
- Allow override via `GENESIS_DISABLE_ABORT_HEURISTIC=1` env var
