# Daily Summary: 2025-12-11

## 1. Stabilization Phase Completed ✅

We have successfully completed the 9-step stabilization plan. The backtesting engine is now fully deterministic and reproducible.

- **Frozen Data**: `tBTCUSD_1h_frozen.parquet` is the single source of truth.
- **Determinism**: Global seeding and process isolation are enforced.
- **Pipeline**: Unified `GenesisPipeline` handles environment setup.
- **Verification**: Smoke tests confirm parity between manual backtests and Optuna runs.

## 2. Optimization Phase 3: The Fee Reality Check

### V3 Run (Baseline)

- **Goal**: Optimize the stabilized engine with standard parameters.
- **Result**: **Failure**.
- **Metrics**: Profit Factor ~0.89.
- **Analysis**: The strategy generates many trades (high frequency), but the **0.5% fee structure** (0.2% commission + 0.3% slippage) erodes all profits. The average trade edge is < 0.5%.

### V4 Run (Sniper Mode)

- **Hypothesis**: Increase `min_edge` (>1.0%) and `entry_conf` to select only high-quality trades that can survive the 0.5% fee.
- **Configuration**: `tBTCUSD_1h_optuna_phase3_stabilized_v4.yaml` (10 trials).
- **Result**: **Failure**.
  - **Scenario A (min_edge 1.0-2.2%)**: Still too many trades (~1300), massive losses (PF ~0.66). The model's predicted "edge" is not realizing actual profits after fees.
  - **Scenario B (min_edge > 2.5%)**: **Zero trades**. The filter becomes too strict.
- **Conclusion**: There is no "sweet spot" in the current 1h model that beats a 0.5% fee. The signal-to-noise ratio is too low for this cost structure.

## 3. Technical Observations

- **Feature Caching**: Observed `[FEATURES] Fast path hits: 0` in some logs. This indicates that while the first run in a process might use the fast path, subsequent runs (or specific configurations) might be missing the precomputed cache or resetting counters incorrectly. This is a minor performance/logging issue, not a correctness issue.
- **Execution Speed**: The engine is fast (~280s for 2 years of 1h data), but optimization is blocked by strategy viability, not speed.

## 4. Critical Decision Point

The current 1h strategy cannot survive a 0.5% round-trip cost. We have three paths forward:

1.  **Change Timeframe**: Move to **4h or Daily**. Capturing larger moves (5-10%) makes the 0.5% fee negligible.
2.  **Improve Signal**: The current ML model/features are not predictive enough for 1h scalping. We need better features (e.g., order flow, liquidation data) or a better model.
3.  **Re-evaluate Fees**: Is 0.5% realistic?
    - Bitfinex Taker Fee: 0.2% (Standard).
    - Slippage: 0.3% (Conservative estimate for 1h market orders).
    - _If_ we can use Limit Orders (Maker 0.1%), the cost drops to ~0.1-0.2%. But backtesting limit orders requires a more complex engine (fill probability).

## 5. Next Steps

- **Immediate**: Pause 1h optimization.
- **Action**: Discuss fee assumptions or pivot to 4h timeframe.
