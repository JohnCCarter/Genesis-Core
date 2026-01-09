# Complete Decision Chain Analysis: Why Optuna Trials Generate Zero Trades

**Date**: 2025-11-11
**Analysis**: Deep trace through the entire system from data to trades

## Executive Summary

Zero-trade Optuna trials are caused by a **cascade of strict gating layers** where each gate can independently block trade generation. When multiple gates are configured conservatively (as happens in random/TPE parameter exploration), the cumulative effect is that nearly ALL signals are blocked.

## The Complete Decision Chain

### Phase 1: Data Loading & Feature Extraction
**File**: `src/core/backtest/engine.py`

```python
# 1. Load historical data
load_data() -> candles_df

# 2. Skip warmup period (typically 120 bars)
if i < self.warmup_bars:
    continue  # NO DECISION POSSIBLE

# 3. Build candles window
candles_window = _build_candles_window(i)
```

**Zero-Trade Cause #1: Insufficient Data**
- If `bars_processed < 100` after warmup, no meaningful trades possible
- Date range might not overlap with available data
- Warmup period might consume most/all of available data

---

### Phase 2: Feature Computation
**File**: `src/core/strategy/features_asof.py`, `src/core/strategy/evaluate.py`

```python
# 1. Extract features (ATR, EMAs, RSI, etc.)
feats, feats_meta = extract_features(candles, config, timeframe, symbol)

# 2. Detect regime (trend/balanced/ranging)
regime = detect_regime_unified(candles, ema_period=50)

# 3. Compute HTF/LTF Fibonacci levels
state = {
    "htf_fib": feats_meta.get("htf_fibonacci"),
    "ltf_fib": feats_meta.get("ltf_fibonacci"),
    "current_atr": feats.get("atr_14"),
    "atr_percentiles": feats_meta.get("atr_percentiles"),
}
```

**Zero-Trade Cause #2: Missing Fibonacci Context**
- If HTF or LTF fibonacci data is unavailable/invalid
- AND `missing_policy = "block"` (default)
- Result: All entries blocked

---

### Phase 3: Model Prediction
**File**: `src/core/strategy/prob_model.py`, `src/core/strategy/evaluate.py`

```python
# 1. Predict buy/sell probabilities
probas, pmeta = predict_proba_for(symbol, timeframe, feats, regime=regime)
# Returns: {"buy": 0.XX, "sell": 0.XX}

# 2. Compute confidence scores
conf, conf_meta = compute_confidence(probas, config=configs.get("quality"))
# Returns: {"buy": 0.XX, "sell": 0.XX}
```

**Zero-Trade Cause #3: Low Probability Scores**
- Model might predict low probabilities (< 0.5 for both directions)
- Often happens in ranging/uncertain market conditions
- Will fail subsequent threshold checks

---

### Phase 4: Decision Gates (THE CRITICAL SECTION)
**File**: `src/core/strategy/decision.py` - `decide()` function

This is where **99% of zero-trade issues occur**. The decision function has **10 sequential gates**, and a signal must pass ALL of them to generate a trade.

#### Gate 1: Fail-Safe & EV Filter (Lines 100-124)
```python
# Must have valid probabilities
if not probas or not isinstance(probas, dict):
    return "NONE", {"reasons": ["FAIL_SAFE_NULL"]}

# Must have positive Expected Value for at least one direction
ev_long = p_buy * R - p_sell
ev_short = p_sell * R - p_buy
if max(ev_long, ev_short) <= 0.0:
    return "NONE", {"reasons": ["EV_NEG"]}
```

**Zero-Trade Cause #4: Negative EV**
- If both directions have negative EV, no trades
- Happens when probabilities are too balanced (p_buy ≈ p_sell ≈ 0.5)
- Common in choppy/ranging markets

#### Gate 2: Event Block (Lines 126-133)
```python
if (risk_ctx or {}).get("event_block"):
    return "NONE", {"reasons": ["R_EVENT_BLOCK"]}
```

**Zero-Trade Cause #5: Event Block**
- External risk management can block all trading
- Rare in backtests, common in live trading

#### Gate 3: Risk Cap (Lines 135-142)
```python
if (risk_ctx or {}).get("risk_cap_breached"):
    return "NONE", {"reasons": ["RISK_CAP"]}
```

**Zero-Trade Cause #6: Risk Cap Breach**
- Position limits exceeded
- Unlikely in backtest (no previous positions)

#### Gate 4: Regime Direction Filter (Lines 144-153)
```python
if regime_str == "trend":
    if policy.get("trend_long_only"):
        short_allowed = False
    if policy.get("trend_short_only"):
        long_allowed = False
```

**Zero-Trade Cause #7: Regime Mismatch**
- If in trend regime and signal opposes trend direction
- Policy might restrict trading in certain regimes

#### Gate 5: Probability Threshold (Lines 156-218)
```python
# Get threshold (regime-specific or ATR-adapted)
thr = float(thresholds.get(regime_str, default_thr))

buy_pass = p_buy >= thr and long_allowed
sell_pass = p_sell >= thr and short_allowed

if not buy_pass and not sell_pass:
    return "NONE"
```

**Zero-Trade Cause #8: Probability Below Threshold** ⚠️ **MOST COMMON**
- `entry_conf_overall` is THE primary threshold
- If set > 0.50, MOST signals blocked
- Optuna often explores values 0.35-0.70 range
- At 0.70 threshold, ~90% of signals blocked

**Example Impact**:
- entry_conf_overall = 0.30 → ~50% of signals pass
- entry_conf_overall = 0.50 → ~20% of signals pass
- entry_conf_overall = 0.70 → ~5% of signals pass

#### Gate 6: HTF Fibonacci Entry Gate (Lines 419-596)
```python
htf_entry_cfg = (cfg.get("htf_fib") or {}).get("entry") or {}
if use_htf_block and htf_entry_cfg.get("enabled"):
    # Check if price is near target Fibonacci levels
    # with tolerance based on ATR

    # For LONG: must be near support levels
    if candidate == "LONG":
        if not near_target_level:
            if not _try_override_htf_block(payload):
                return "NONE", {"reasons": ["HTF_FIB_LONG_BLOCK"]}

    # For SHORT: must be near resistance levels
    elif candidate == "SHORT":
        if not near_target_level:
            if not _try_override_htf_block(payload):
                return "NONE", {"reasons": ["HTF_FIB_SHORT_BLOCK"]}
```

**Zero-Trade Cause #9: HTF Fibonacci Blocking** ⚠️ **VERY COMMON**
- Requires price to be within `tolerance_atr * ATR` of target Fibonacci levels
- If `tolerance_atr = 0.3` and `ATR = 100`, tolerance is only $30
- For a $40,000 BTC, that's 0.075% - EXTREMELY TIGHT
- Most entries occur far from Fibonacci levels

**Example Impact**:
- tolerance_atr = 0.3 → ~90-95% blocked
- tolerance_atr = 0.5 → ~70-80% blocked
- tolerance_atr = 0.8 → ~40-50% blocked

**Missing Data Issue**:
- If HTF Fibonacci data unavailable: `missing_policy = "block"` (default)
- Result: ALL entries blocked
- Should use `missing_policy = "pass"` for robustness

#### Gate 7: LTF Fibonacci Entry Gate (Lines 607-696)
```python
if ltf_entry_cfg.get("enabled"):
    # Similar to HTF but for same-timeframe Fib levels
    # LONG: must be below max_level + tolerance
    # SHORT: must be above min_level - tolerance

    if condition_fails:
        return "NONE", {"reasons": ["LTF_FIB_BLOCK"]}
```

**Zero-Trade Cause #10: LTF Fibonacci Blocking**
- Similar mechanism to HTF
- Can block independently even if HTF passes
- Compounds with HTF gate: `P(pass_both) = P(htf) * P(ltf)`

#### Gate 8: Confidence Gate (Lines 704-729)
```python
# Must meet confidence threshold for chosen direction
if candidate == "LONG" and c_buy < conf_thr:
    return "NONE", {"reasons": ["CONF_TOO_LOW"]}
if candidate == "SHORT" and c_sell < conf_thr:
    return "NONE", {"reasons": ["CONF_TOO_LOW"]}
```

**Zero-Trade Cause #11: Low Confidence**
- Separate from probability threshold
- Both must pass: probability AND confidence
- Cumulative effect: `P(trade) = P(proba_pass) * P(conf_pass)`

#### Gate 9: Edge Requirement (Lines 733-752)
```python
min_edge = float((cfg.get("thresholds") or {}).get("min_edge", 0.0))
if min_edge > 0:
    edge = p_buy - p_sell  # or p_sell - p_buy for SHORT
    if edge < min_edge:
        return "NONE", {"reasons": ["EDGE_TOO_SMALL"]}
```

**Zero-Trade Cause #12: Insufficient Edge**
- Requires clear directional bias (e.g., 0.10 difference)
- Blocks marginal signals where buy ≈ sell probabilities
- If min_edge = 0.10, requires p_buy >= 0.60 when p_sell = 0.50

#### Gate 10: Hysteresis (Lines 755-771)
```python
# Must confirm direction change for N steps
if last_action != candidate:
    d_steps += 1
    if d_steps < hysteresis_steps:
        return "NONE", {"reasons": ["HYST_WAIT"]}
```

**Zero-Trade Cause #13: Hysteresis Delay**
- Prevents rapid direction changes
- Requires N consecutive confirmations (typically 2)
- First signal always blocked if switching direction

#### Gate 11: Cooldown (Lines 774-782)
```python
cooldown_left = int(state_in.get("cooldown_remaining", 0))
if cooldown_left > 0:
    return "NONE", {"reasons": ["COOLDOWN_ACTIVE"]}
    state_out["cooldown_remaining"] = max(0, cooldown_left - 1)
```

**Zero-Trade Cause #14: Cooldown Period**
- After any decision, system enters cooldown
- Must wait N bars before next signal
- Reduces trade frequency significantly

---

### Phase 5: Sizing & Execution
**File**: `src/core/backtest/engine.py`

```python
# Only executed if action != "NONE"
if action != "NONE" and size > 0:
    exec_result = self.position_tracker.execute_action(
        action=action,
        size=size,
        price=close_price,
        timestamp=timestamp,
    )
```

**Zero-Trade Cause #15: Zero Size**
- Even if action passes all gates, size might be 0.0
- Happens if confidence below all risk_map thresholds

---

## Cumulative Effect: The Multiplication Problem

If each gate has an independent pass rate:
- Gate 5 (Probability): 20% pass (entry_conf = 0.50)
- Gate 6 (HTF Fib): 10% pass (tolerance = 0.3)
- Gate 7 (LTF Fib): 10% pass (tolerance = 0.3)
- Gate 8 (Confidence): 30% pass
- Gate 9 (Edge): 40% pass
- Gate 10 (Hysteresis): 50% pass (every other signal)

**Combined pass rate**: 0.20 × 0.10 × 0.10 × 0.30 × 0.40 × 0.50 = **0.0012** = **0.12%**

Out of 1000 bars processed, only **1-2 trades** would occur!

With more conservative settings:
- entry_conf = 0.70 (5% pass)
- htf_tolerance = 0.2 (5% pass)
- ltf_tolerance = 0.2 (5% pass)

**Combined**: 0.05 × 0.05 × 0.05 × 0.30 × 0.40 × 0.50 = **0.000075** = **0.0075%**

Out of 10,000 bars, ~0.75 trades = **ZERO TRADES!**

---

## Why Optuna Makes This Worse

### 1. Random/TPE Exploration
Optuna explores parameter space randomly or via TPE. It will frequently sample:
- High entry thresholds (0.60-0.70)
- Tight Fibonacci tolerances (0.2-0.4)
- Strict edge requirements (0.10-0.15)

These combinations almost guarantee zero trades.

### 2. No Pre-Validation
Optuna doesn't know which parameter combinations are viable. It treats:
- `entry_conf = 0.30` (generates trades)
- `entry_conf = 0.70` (generates no trades)

as equally worth exploring.

### 3. Penalty Doesn't Help Early
When Optuna gets -100 score (zero trades), it learns "these parameters are bad" but:
- It may have already wasted 50+ trials exploring that region
- TPE needs several trials to learn the boundary
- Random sampler never learns

---

## Concrete Problems Identified

### Problem 1: Default Thresholds Too Conservative
**Location**: Various config files, champion configs

**Current Defaults**:
```yaml
thresholds:
  entry_conf_overall: 0.70  # TOO HIGH - blocks 95% of signals
```

**Fix**:
```yaml
thresholds:
  entry_conf_overall: 0.30-0.40  # More reasonable range
```

### Problem 2: Fibonacci Tolerances Too Tight
**Location**: `htf_fib.entry.tolerance_atr`, `ltf_fib.entry.tolerance_atr`

**Current Defaults**:
```yaml
htf_fib:
  entry:
    tolerance_atr: 0.3  # TOO TIGHT
    missing_policy: "block"  # TOO STRICT
```

**Fix**:
```yaml
htf_fib:
  entry:
    tolerance_atr: 0.5-0.8  # Wider tolerance
    missing_policy: "pass"  # Allow trading when data missing
```

### Problem 3: No LTF Override by Default
**Location**: `multi_timeframe` config

**Current**:
```yaml
multi_timeframe:
  use_htf_block: true
  allow_ltf_override: false  # HTF can block everything
```

**Fix**:
```yaml
multi_timeframe:
  use_htf_block: true
  allow_ltf_override: true  # Allow high-confidence LTF to override
  ltf_override_threshold: 0.75
```

### Problem 4: Search Space Includes Unviable Regions
**Location**: Optuna YAML configs

**Current**:
```yaml
parameters:
  thresholds:
    entry_conf_overall:
      type: float
      low: 0.30
      high: 0.70  # Includes unviable 0.60-0.70 range
```

**Fix**:
```yaml
parameters:
  thresholds:
    entry_conf_overall:
      type: float
      low: 0.25
      high: 0.45  # Exclude unviable range
```

### Problem 5: No Validation Before Long Runs
**Location**: Optimizer workflow

**Current**: Start 100-trial Optuna run without testing

**Fix**:
1. Run smoke test (2-5 trials) with champion parameters
2. Verify >0 trades before full run
3. Adjust search space if smoke test fails

---

## Recommended Fixes

### Immediate (Code Changes)

1. **Add pre-run validation** in `src/core/optimizer/runner.py`:
   ```python
   # Before starting Optuna, test champion parameters
   smoke_trial = run_trial(champion_params, ...)
   if smoke_trial["score"]["metrics"]["num_trades"] == 0:
       print("WARNING: Champion parameters produce 0 trades!")
       print("Search space may be too restrictive.")
   ```

2. **Improve search space validation** (already done):
   ```python
   space_diagnostics = _estimate_optuna_search_space(parameters_spec)
   # Warn if all parameter combinations likely unviable
   ```

3. **Add gate telemetry** in `src/core/strategy/decision.py`:
   ```python
   # Track which gates block most often
   state_out["gate_stats"] = {
       "blocked_by": "HTF_FIB_LONG_BLOCK",
       "gate_sequence": reasons,
   }
   ```

### Configuration (User-Facing)

1. **Update champion configs** to use more permissive defaults:
   - entry_conf_overall: 0.30-0.40 (not 0.70)
   - htf_fib tolerance: 0.5-0.8 (not 0.3)
   - missing_policy: "pass" (not "block")

2. **Update Optuna search spaces** to exclude unviable regions:
   - entry_conf_overall: [0.25, 0.45] (not [0.30, 0.70])
   - tolerance_atr: [0.4, 0.8] (not [0.2, 0.6])

3. **Enable LTF override** by default:
   - allow_ltf_override: true
   - ltf_override_threshold: 0.70-0.85

### Documentation

1. **Create decision chain diagram** showing all 14 blocking points
2. **Add "Why am I getting zero trades?" troubleshooting guide**
3. **Document typical pass rates** for each threshold setting
4. **Provide calculator** for combined pass probability

---

## Testing Validation

To verify these fixes work, test with:

```yaml
# Smoke test config - should generate trades
thresholds:
  entry_conf_overall: 0.30
htf_fib:
  entry:
    enabled: true
    tolerance_atr: 0.6
    missing_policy: "pass"
ltf_fib:
  entry:
    enabled: true
    tolerance_atr: 0.6
    missing_policy: "pass"
multi_timeframe:
  use_htf_block: true
  allow_ltf_override: true
  ltf_override_threshold: 0.75
```

Expected: 10-50 trades over a 3-month backtest period.

---

## Conclusion

Zero trades in Optuna trials are caused by a **multiplicative cascade** of strict decision gates. The core issues are:

1. **Overly conservative default thresholds**
2. **Tight Fibonacci tolerances** that block most entries
3. **No escape valve** (LTF override disabled)
4. **Search spaces include unviable parameter regions**
5. **No validation before expensive runs**

The fixes are straightforward but require:
- Configuration updates (immediate)
- Search space adjustments (immediate)
- Code enhancements for better diagnostics (medium-term)
- User education and documentation (ongoing)

With these changes, Optuna trials should generate 10-100+ trades per run, providing meaningful optimization feedback.
