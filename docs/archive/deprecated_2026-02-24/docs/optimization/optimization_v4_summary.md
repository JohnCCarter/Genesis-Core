# Optimization Report: Phase 3 Stabilized V4 (Sniper Mode)

## Run Details 2025-12-11

- **Run ID**: run_20251211_150945 (Reused)
- **Trials**: 10
- **Strategy**: Sniper Mode (High Edge, Low Frequency)
- **Fee Structure**: 0.5% (0.2% commission + 0.3% slippage)

## Results Summary

The optimization produced polarized results:

1.  **High Frequency / Low Quality**:

    - Trials with `min_edge` ~1.0% - 2.2% produced **1300-1800 trades**.
    - **Profit Factor**: ~0.66 (Heavy losses).
    - **Return**: -23% to -25%.
    - **Conclusion**: The model frequently predicts >1% edge, but these trades do not survive the 0.5% fee. The "edge" is likely overestimated or not robust.

2.  **Zero Trades**:
    - Trials with `min_edge` ~2.5% produced **0 trades**.
    - **Conclusion**: Raising the bar to 2.5% eliminates all signals.

## Key Insights

- **Fee Impact**: The 0.5% fee is a massive hurdle. A strategy with PF 0.66 implies the gross profit is significantly lower than the fees + losses.
- **Edge Calibration**: The model's "1% edge" is not translating to realized profit. This suggests the probability calibration might be off, or the market regime classification is failing to filter bad trades.
- **Sniper Failure**: The attempt to filter for "high quality" trades by simply raising `min_edge` failed. It either lets in too much junk (at 1-2%) or nothing (at 2.5%).

## Recommendations

1.  **Re-evaluate Fees**: Confirm if 0.5% is the realistic floor. If so, the strategy needs a fundamental rethink (e.g., much longer timeframes, 4h/daily).
2.  **Improve Signal**: The current 1h model does not have enough predictive power to beat 0.5% fees.
3.  **Regime Filter**: Focus on `regime_proba` to filter trades. The current run had wide ranges for regime. Maybe we only trade in very strong trends?
