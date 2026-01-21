# Golden Trace Tests

## Purpose

Golden trace tests lock the causal chain from parameters to PnL by asserting that identical inputs produce identical outputs at each stage. These tests are designed to catch **semantic drift** - subtle changes in behavior that don't cause obvious test failures but change strategy outcomes.

## Test Structure

### Test 1: Parameter → Feature Determinism
**File**: `test_param_to_feature_trace.py`

Verifies that feature extraction (indicators, Fibonacci swings) is deterministic.

**Catches drift in**:
- Indicator calculations (ATR, EMA, RSI, Bollinger Bands, ADX)
- Fibonacci swing point detection
- Feature preprocessing

**Golden snapshot**: `snapshots/golden_features_v1.json`

### Test 2: Feature → Decision Determinism
**File**: `test_feature_to_decision_trace.py`

Verifies that decision logic (entry gates, sizing) is deterministic.

**Catches drift in**:
- Confidence calculation
- Entry gate logic (Fibonacci gates, thresholds, regime adaptation)
- Position sizing (risk map)
- Decision blocking logic

**Golden snapshot**: `snapshots/golden_decision_v1.json`

### Test 3: End-to-End Backtest Determinism
**File**: `test_backtest_e2e_trace.py`

Verifies that a complete backtest produces identical results.

**Catches drift in**:
- Entire execution pipeline
- Fill simulation (slippage, commission)
- PnL calculation
- Metrics calculation
- **Any semantic changes to strategy logic**

**Golden snapshot**: `snapshots/golden_backtest_v1.json`

## Running Tests

```bash
# Run all golden trace tests
pytest tests/golden_traces/ -v

# Run specific test
pytest tests/golden_traces/test_backtest_e2e_trace.py -v

# Run with detailed output on failure
pytest tests/golden_traces/ -v --tb=long
```

## Re-baselining Snapshots

Golden snapshots should ONLY be updated when you intentionally change strategy logic.

### When to Re-baseline

✅ **YES - Re-baseline when:**
- Intentionally changing indicator formulas (e.g., ATR calculation method)
- Modifying entry gate logic (e.g., adding new Fibonacci gate)
- Changing position sizing algorithm
- Updating confidence calculation
- Fixing a known bug in strategy logic

❌ **NO - Investigate first if:**
- Tests fail unexpectedly without code changes
- Only some metrics differ slightly
- Changes are in non-strategy code (e.g., logging, observability)

### How to Re-baseline

```bash
# Re-baseline all golden traces
python scripts/rebaseline_golden_traces.py --all

# Re-baseline specific test
python scripts/rebaseline_golden_traces.py --test test_param_to_feature_trace

# Dry-run (show what would be updated)
python scripts/rebaseline_golden_traces.py --all --dry-run
```

**Important**: When re-baselining, include the git SHA of the commit in a comment:

```json
{
  "_baseline_meta": {
    "version": "v2",
    "git_sha": "abc123...",
    "date": "2026-01-21",
    "reason": "Updated ATR calculation to use Wilder's smoothing"
  },
  "features": { ... }
}
```

## Snapshot Format

### `golden_features_v1.json`
```json
{
  "atr_14": 123.45,
  "atr_50": 145.67,
  "ema_20": 50123.45,
  "ema_50": 49987.32,
  "rsi_14": 58.32,
  "bb_position_20_2": 0.65,
  "adx_14": 24.3,
  "swing_high": 51234.56,
  "swing_low": 49876.54,
  "close": 50000.0,
  "htf_fib": { ... },
  "ltf_fib": { ... }
}
```

### `golden_decision_v1.json`
```json
{
  "action": "LONG",
  "size": 0.045,
  "confidence": 0.58,
  "reasons": ["HTF_ALIGNED", "LTF_BOUNCE"],
  "blocked_by": null
}
```

### `golden_backtest_v1.json`
```json
{
  "trades": [
    {
      "side": "LONG",
      "entry_price": 50134.56,
      "exit_price": 51234.78,
      "pnl": 1100.22,
      "pnl_pct": 2.19,
      "exit_reason": "FIB_0.618",
      ...
    }
  ],
  "summary": {
    "final_capital": 10336.45,
    ...
  },
  "metrics": {
    "total_trades": 164,
    "total_return": 0.0336,
    "profit_factor": 1.25,
    "max_drawdown": 0.0297,
    "sharpe_ratio": 0.87,
    ...
  }
}
```

## CI Integration

Golden trace tests are part of the CI pipeline and will fail builds if snapshots drift:

```yaml
# .github/workflows/ci.yml
- name: Golden Trace Tests
  run: pytest tests/golden_traces/ -v --strict-markers
```

**To skip golden trace tests in CI** (emergency only):
```bash
pytest tests/golden_traces/ -v -m "not golden_trace"
```

## Troubleshooting

### Test fails with "Frozen candles not found"
Run the rebaseline script to generate the frozen data:
```bash
python scripts/rebaseline_golden_traces.py --all
```

### Test fails with small numeric differences (1e-14)
This is usually due to platform differences (Linux vs macOS, CPU architecture).
Consider slightly relaxing the tolerance in the test (e.g., `rtol=1e-10` → `rtol=1e-8`).

### All tests fail after refactoring
This is expected! Re-baseline after verifying the refactoring is correct:
```bash
# 1. Verify refactoring is correct (manual testing, other unit tests)
# 2. Re-baseline
python scripts/rebaseline_golden_traces.py --all
# 3. Re-run tests
pytest tests/golden_traces/ -v
```

## Maintenance Notes

- **Snapshot versioning**: Use `v1`, `v2`, etc. in filenames when making breaking changes
- **Backward compatibility**: Keep old snapshots when introducing new versions
- **Documentation**: Always document why a snapshot was re-baselined
- **Review process**: Re-baseline PRs should include explanation of what changed

## See Also

- [Runtime Reality Map](../../docs/analysis/RUNTIME_REALITY_MAP.md) - Complete execution path documentation
- [Stabilization Plan](../../docs/roadmap/STABILIZATION_PLAN_9_STEPS.md) - Determinism guarantees
