# Golden Trace Snapshots

This directory contains golden snapshots for trace tests.

## Required Files

Before running golden trace tests, you must generate the baseline snapshots:

```bash
# 1. Copy a known-good champion config
cp config/strategy/champions/tBTCUSD_1h.json tests/golden_traces/snapshots/golden_champion_params.json

# 2. Generate all snapshots
python scripts/rebaseline_golden_traces.py --all

# 3. Run tests to verify
pytest tests/golden_traces/ -v
```

## Expected Files

- `golden_champion_params.json` - Champion parameters for testing
- `golden_features_v1.json` - Feature extraction baseline
- `golden_decision_v1.json` - Decision logic baseline
- `golden_backtest_v1.json` - End-to-end backtest baseline
- `tBTCUSD_1h_sample_100bars.parquet` - Frozen candle data (100 bars)

## Snapshot Format Examples

See `tests/golden_traces/README.md` for detailed format specifications.

## Note

Golden snapshots are intentionally NOT checked into git initially.
Each team should generate their own baseline from a known-good state.

To create your baseline:
1. Ensure you're on a commit with verified strategy behavior
2. Run the rebaseline script
3. Commit the generated snapshots with git SHA and explanation
