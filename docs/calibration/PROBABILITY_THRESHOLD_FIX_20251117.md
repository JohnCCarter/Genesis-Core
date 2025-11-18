# Probability Threshold Bottleneck Fix

**Date:** 2025-11-17  
**Issue:** Champion config producing 0 trades despite correct fibonacci gate setup  
**Root Cause:** `thresholds.regime_proba` values too high (0.70-0.80)  
**Solution:** Lowered to match model output range (0.42-0.52)

## Problem Discovery

### Systematic Investigation

1. **Initial Hypothesis:** Fibonacci gates blocking all signals
   - Created `scripts/calibrate_fib_gates.py` to test 5 configurations
   - ALL configs produced 0 trades → fib gates NOT the bottleneck

2. **Log Analysis:**
   ```
   [FIB-FLOW] decide() called with cfg keys: ['thresholds', 'risk', 'exit', 'gates', 'htf_exit_config', 'warmup_bars', 'ltf_fib', 'htf_fib', 'ev', 'multi_timeframe', 'meta']
   [FIB-FLOW] Early return: proba threshold not met (buy_pass=False sell_pass=False)
   ```
   - **Key Insight:** Signals blocked BEFORE reaching fibonacci gates
   - Probability threshold check happens upstream in decision pipeline

3. **Diagnostic Logging:**
   ```
   [DEBUG] Proba threshold check FAILED: p_buy=0.4187 p_sell=0.5813 thr=0.8000 regime=ranging
   ```
   - Model predictions: 0.42-0.64 (reasonable)
   - Threshold: 0.80 (too high!)

## Decision Flow Architecture

```
1. EV filter
2. Signal adaptation zones (ATR-based entry thresholds)
3. → Probability threshold check ← BLOCKING HERE
4. Tie-break logic
5. HTF/LTF fibonacci gates (never reached)
6. Final confidence checks
```

**Critical Finding:** `thresholds.regime_proba` in top-level config controls the probability threshold check, NOT `signal_adaptation.zones.*.regime_proba`.

## Configuration Structure

### Champion Config (Before Fix)
```json
{
  "thresholds": {
    "regime_proba": {
      "ranging": 0.8,    // TOO HIGH
      "bull": 0.7,       // TOO HIGH
      "bear": 0.7,       // TOO HIGH
      "balanced": 0.7    // TOO HIGH
    },
    "signal_adaptation": {
      "zones": {
        "low": { "regime_proba": { "ranging": 0.50, ... } },
        "mid": { "regime_proba": { "ranging": 0.55, ... } },
        "high": { "regime_proba": { "ranging": 0.60, ... } }
      }
    }
  }
}
```

**Issue:** Top-level `thresholds.regime_proba` was 0.70-0.80, while nested zones were 0.45-0.60. Decision logic uses top-level values.

### Champion Config (After Fix)
```json
{
  "thresholds": {
    "regime_proba": {
      "ranging": 0.52,   // Lowered to match model output
      "bull": 0.42,      // Lowered to match model output
      "bear": 0.42,      // Lowered to match model output
      "balanced": 0.48   // Lowered to match model output
    }
  }
}
```

## Results

### Test Period: 2024-10-22 to 2024-11-22 (1 month)
**Before Fix:**
- Trades: 0
- Return: 0.00%
- Issue: All signals blocked at probability threshold

**After Fix:**
- Trades: 2
- Return: +0.49%
- Win Rate: 100%
- Profit Factor: inf

### Extended Period: 2024-10-22 to 2024-12-31 (2.5 months)
- **Trades:** 7
- **Win Rate:** 71.4%
- **Return:** +4.37% ($437.38 on $10k)
- **Profit Factor:** 8.85
- **Max Drawdown:** 1.31%
- **Sharpe Ratio:** 0.676
- **Avg Win:** $107.98
- **Avg Loss:** -$30.51
- **Commission:** -$27.78

## Key Learnings

1. **Decision Pipeline Order Matters**
   - Upstream filters can completely block downstream logic
   - Fibonacci gates were correctly configured but never reached
   - Always verify signal flow reaches intended gates

2. **Model Output Range**
   - Current model produces probabilities in 0.42-0.64 range
   - Thresholds must match actual model behavior
   - Default config values (0.70-0.80) were calibrated for different model

3. **Configuration Hierarchy**
   - Top-level `thresholds.regime_proba` controls probability check
   - Nested `signal_adaptation.zones.*.regime_proba` used for different purpose
   - Deep merge doesn't automatically sync these values

4. **Diagnostic Approach**
   - Systematic isolation testing (change one variable at a time)
   - Log analysis critical for understanding execution flow
   - Test multiple configurations to identify actual bottleneck

## Implementation Notes

### Files Changed
1. `config/strategy/champions/tBTCUSD_1h.json`
   - Lowered `thresholds.regime_proba` values from 0.70-0.80 to 0.42-0.52

2. `src/core/strategy/decision.py`
   - Added temporary diagnostic logging (removed after fix confirmed)

### Calibration Process
1. Created test config with lowered thresholds
2. Ran backtest → confirmed trades appeared
3. Applied same thresholds to champion config
4. Validated on 1-month and 2.5-month periods
5. Removed diagnostic logging

## Recommendations for Future Work

1. **Threshold Optimization**
   - Current values (0.42-0.52) produce very selective system (7 trades / 2.5 months)
   - Consider testing range 0.35-0.50 for more trade opportunities
   - Use Optuna to optimize probability thresholds alongside other parameters

2. **Model Calibration**
   - Investigate why model outputs cluster in 0.42-0.64 range
   - Consider probability calibration techniques
   - Retrain with different loss function if probability range is too narrow

3. **Configuration Validation**
   - Add schema validation to ensure `thresholds.regime_proba` matches expected ranges
   - Warn if thresholds > 0.65 (likely too high for current model)
   - Add preflight check that compares top-level vs nested regime_proba values

4. **Documentation**
   - Update decision flow documentation to clarify probability threshold check
   - Add troubleshooting guide for "0 trades" scenarios
   - Document relationship between top-level and nested threshold configs

## Related Documents
- `AGENTS.md` - Section 21: Original breakthrough configuration discovery (2025-11-13)
- `docs/fibonacci/FIB_GATING_DEBUG_20251027.md` - Fibonacci gate debugging
- `docs/optuna/BREAKTHROUGH_CONFIG_20251113.md` - Signal adaptation threshold discovery

## Conclusion

The "0 trades mystery" was resolved by identifying that probability thresholds (0.70-0.80) were mismatched with model output range (0.42-0.64). Lowering `thresholds.regime_proba` to 0.42-0.52 restored trade generation while maintaining high quality (71.4% win rate, PF 8.85). The fibonacci gates were working correctly but never reached due to upstream filtering.

**Status:** ✅ RESOLVED - Champion config now generates trades with strong performance metrics.
