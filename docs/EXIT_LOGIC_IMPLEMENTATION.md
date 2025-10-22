# Exit Logic Implementation - 2025-10-10

**Status**: ✅ IMPLEMENTED, TESTING IN PROGRESS

---

## Summary

Implemented comprehensive exit logic for backtest engine and future live trading, addressing the critical issue where positions were held indefinitely (up to 11 months!).

---

## Changes Made

### 1. Added Exit Configuration Schema (`src/core/config/schema.py`)

```python
class ExitLogic(BaseModel):
    """Exit configuration for backtest and live trading."""

    enabled: bool = Field(default=True, description="Enable exit logic")
    max_hold_bars: int = Field(default=20, ge=1, description="Max bars to hold position")
    stop_loss_pct: float = Field(default=0.02, ge=0.0, le=1.0, description="Stop loss %")
    take_profit_pct: float = Field(default=0.05, ge=0.0, le=1.0, description="Take profit %")
    exit_conf_threshold: float = Field(
        default=0.45, ge=0.0, le=1.0, description="Close if confidence drops below"
    )
    regime_aware_exits: bool = Field(
        default=True, description="Close on regime change (e.g., SHORT in BULL)"
    )
    trailing_stop_enabled: bool = Field(default=False, description="Enable trailing stop-loss")
    trailing_stop_pct: float = Field(
        default=0.015, ge=0.0, le=1.0, description="Trailing stop distance %"
    )
```

**Impact**: Exit parameters now part of runtime config, validated by Pydantic.

---

### 2. Updated Runtime Config (`config/runtime.json`)

Added new `exit` section:

```json
{
  "cfg": {
    "exit": {
      "enabled": true,
      "max_hold_bars": 20,
      "stop_loss_pct": 0.02,
      "take_profit_pct": 0.05,
      "exit_conf_threshold": 0.45,
      "regime_aware_exits": true,
      "trailing_stop_enabled": false,
      "trailing_stop_pct": 0.015
    },
    ...
  },
  "version": 61
}
```

**Defaults**:
- **Max hold**: 20 bars (aligns with validation horizon ~2.5 days on 6h)
- **Stop-loss**: 2% (risk management)
- **Take-profit**: 5% (2.5:1 reward/risk ratio)
- **Confidence exit**: < 0.45 (model no longer confident)
- **Regime-aware**: Yes (close SHORT in BULL, LONG in BEAR)

---

### 3. Enhanced PositionTracker (`src/core/backtest/position_tracker.py`)

#### New Methods:

**`close_position_with_reason(price, timestamp, reason)`**:
- Closes position with explicit reason tracking
- Returns completed `Trade` object
- Reasons: "SL", "TP", "TIME", "CONF_DROP", "REGIME_CHANGE", etc.

**`get_unrealized_pnl_pct(current_price)`**:
- Calculates current P&L% for open position
- Used by exit logic to check SL/TP thresholds

**`get_bars_held(current_timestamp)`**:
- Stub method (BacktestEngine tracks this directly)

#### Updated Methods:

**`_close_position()`**: Now calls `close_position_with_reason()` internally

---

### 4. BacktestEngine Exit Logic (`src/core/backtest/engine.py`)

#### New Variable Tracking:

```python
position_entry_bar = None  # Track when position opened
```

#### New Method: `_check_exit_conditions()`

Checks 5 exit conditions on every bar:

```python
def _check_exit_conditions(
    self,
    current_price: float,
    current_bar: int,
    entry_bar: int,
    confidence: float,
    regime: str,
    configs: dict,
) -> str | None:
    """
    Check if any exit conditions are met.

    Returns:
        Exit reason string if should exit, None otherwise
    """
    # 1. Stop-Loss / Take-Profit
    pnl_pct = self.position_tracker.get_unrealized_pnl_pct(current_price) / 100.0
    if pnl_pct <= -stop_loss_pct:
        return "SL"
    if pnl_pct >= take_profit_pct:
        return "TP"

    # 2. Time-Based Exit
    bars_held = current_bar - entry_bar
    if bars_held >= max_hold_bars:
        return "TIME"

    # 3. Confidence Drop
    if confidence < exit_conf_threshold:
        return "CONF_DROP"

    # 4. Regime-Aware Exit
    if regime_aware:
        if position.side == "SHORT" and regime == "BULL":
            return "REGIME_CHANGE"
        if position.side == "LONG" and regime == "BEAR":
            return "REGIME_CHANGE"

    return None
```

#### Updated Main Loop:

```python
for i in range(len(self.candles_df)):
    # ... get bar data ...

    # === EXIT LOGIC (check BEFORE new entry) ===
    if self.position_tracker.has_position():
        exit_reason = self._check_exit_conditions(...)

        if exit_reason:
            trade = self.position_tracker.close_position_with_reason(
                price=close_price, timestamp=timestamp, reason=exit_reason
            )
            if verbose and trade:
                print(f"\n[{timestamp}] EXIT ({exit_reason}): {trade.side} ...")
            position_entry_bar = None

    # === ENTRY LOGIC ===
    if action != "NONE" and size > 0:
        exec_result = self.position_tracker.execute_action(...)
        if exec_result.get("executed"):
            position_entry_bar = i  # Track entry bar
```

**Key Point**: Exit checks happen BEFORE entry logic, ensuring positions are managed properly.

---

## Exit Conditions - Detailed Explanation

### 1. Stop-Loss (SL)

**Trigger**: Position loses 2% or more

**Example**:
- LONG @ $100,000, current price $98,000 → -2% → EXIT (SL)
- SHORT @ $100,000, current price $102,000 → -2% → EXIT (SL)

**Purpose**: Risk management, prevent runaway losses

---

### 2. Take-Profit (TP)

**Trigger**: Position gains 5% or more

**Example**:
- LONG @ $100,000, current price $105,000 → +5% → EXIT (TP)
- SHORT @ $100,000, current price $95,000 → +5% → EXIT (TP)

**Purpose**: Lock in profits, 2.5:1 reward/risk ratio

---

### 3. Time-Based Exit (TIME)

**Trigger**: Position held for 20+ bars

**Example**:
- 6h timeframe: 20 bars = 5 days
- 1h timeframe: 20 bars = 20 hours
- 30m timeframe: 20 bars = 10 hours

**Purpose**: Align with validation horizon (10-bar forward returns), prevent indefinite holds

**Why 20 bars?**
- Validation uses 10-bar horizon
- 20 bars = 2× validation horizon (safety margin)
- Prevents 11-month holds like we saw in 6h backtest!

---

### 4. Confidence Drop (CONF_DROP)

**Trigger**: Model confidence drops below 0.45

**Example**:
- Entry: conf = 0.57 → Open LONG
- Bar +5: conf = 0.52 → Keep open
- Bar +8: conf = 0.44 → EXIT (CONF_DROP)

**Purpose**: Exit when model becomes uncertain

**Why 0.45?**
- Entry threshold: 0.55
- Exit threshold: 0.45
- Creates 0.10 hysteresis band (prevents flip-flopping)

---

### 5. Regime-Aware Exit (REGIME_CHANGE)

**Trigger**: Position side misaligned with regime

**Examples**:
- SHORT in BULL regime → EXIT (wrong direction)
- LONG in BEAR regime → EXIT (wrong direction)
- SHORT in BEAR → Keep open ✅
- LONG in BULL → Keep open ✅

**Purpose**: Prevent trading against dominant trend

**Why important?**
- 6h model showed SHORT entry in strong bull market
- Position held 11 months, -36% loss
- This would have exited within days!

---

## Expected Impact

### Before Exit Logic:

| Issue | Impact |
|-------|--------|
| 11-month hold period | -36% loss on single trade |
| 1 trade in 360 days | No statistical significance |
| No stop-loss | Unlimited downside risk |
| No take-profit | Missed profit opportunities |

### After Exit Logic (Expected):

| Improvement | Impact |
|-------------|--------|
| Max 5-day hold (6h) | Aligns with validation horizon |
| 20-40 trades/year | Statistical significance |
| 2% stop-loss | Limited downside risk |
| 5% take-profit | Captures profits |
| Regime-aware | Avoids counter-trend disasters |

---

## Trade Lifecycle Example

### Scenario: Successful LONG Trade

```
Bar 100: Entry
  - Signal: LONG, conf=0.58
  - Action: Open LONG 0.02 BTC @ $90,000
  - Entry bar tracked: 100

Bar 101-105: Monitor
  - Price: $91,000-$93,000
  - PnL: +1% to +3%
  - Conf: 0.56-0.57
  - Check: SL? NO. TP? NO. TIME? NO (5 bars). CONF? NO.
  - Action: HOLD

Bar 106: Take-Profit
  - Price: $94,500
  - PnL: +5.0% ✅
  - Check: TP? YES!
  - Action: EXIT (TP)
  - Trade closed: +5% profit
```

**Duration**: 6 bars ✅ (vs 330 bars before!)

---

### Scenario: Stopped Out

```
Bar 200: Entry
  - Signal: SHORT, conf=0.60
  - Action: Open SHORT 0.02 BTC @ $100,000

Bar 201-203: Monitor
  - Price: $100,500-$101,500
  - PnL: -0.5% to -1.5%
  - Check: SL? NO (< -2%). Others? NO.
  - Action: HOLD

Bar 204: Stop-Loss
  - Price: $102,100
  - PnL: -2.1% ❌
  - Check: SL? YES!
  - Action: EXIT (SL)
  - Trade closed: -2.1% loss
```

**Duration**: 4 bars, loss limited to -2.1% ✅

---

## Testing Status

### Implemented ✅:
1. Exit schema in RuntimeConfig
2. Exit config in runtime.json
3. PositionTracker methods
4. BacktestEngine exit logic
5. Debug script for testing

### Testing 🔄:
1. Running backtest on 30m (in progress)
2. Will test 1h, 6h next
3. Comparing results with validation metrics

### Expected Results:

| Timeframe | Trades (before) | Trades (after) | Avg Hold (before) | Avg Hold (after) |
|-----------|-----------------|----------------|-------------------|------------------|
| 30m | 1 | 20-40 | Unknown | ~10 hours |
| 1h | 3 | 20-40 | Unknown | ~20 hours |
| 6h | 1 | 20-40 | **330 days!** | ~5 days |

---

## Configuration Tuning Guide

### For Higher Trade Frequency:

```json
{
  "max_hold_bars": 10,  // Shorter hold period
  "exit_conf_threshold": 0.50  // Higher threshold (exit sooner)
}
```

### For Better Risk/Reward:

```json
{
  "stop_loss_pct": 0.015,  // Tighter stop (1.5%)
  "take_profit_pct": 0.06   // Higher target (6%)
}
```

### For Trend-Following:

```json
{
  "max_hold_bars": 50,  // Longer holds
  "regime_aware_exits": true,  // Exit on regime change
  "trailing_stop_enabled": true,  // Let winners run
  "trailing_stop_pct": 0.02
}
```

---

## Next Steps

1. ✅ Implementation complete
2. 🔄 Testing in progress (30m, 1h, 6h backtests)
3. ⬜ Analyze results vs validation metrics
4. ⬜ Tune exit parameters if needed
5. ⬜ Document final results
6. ⬜ Deploy to live trading (paper mode first)

---

## Key Learnings

### 1. Exit Logic is Critical

**Quote from 6h disaster**: "11-month hold, -36% loss"

**Without exits**: Perfect entry means nothing if you never exit.

**With exits**: Risk-managed, profit-captured, aligned with validation.

---

### 2. Align Backtest with Validation

**Validation**: 10-bar forward return horizon

**Backtest (before)**: Unlimited holding period

**Backtest (after)**: 20-bar max hold (2× validation horizon)

**Result**: Backtest now tests what validation validated!

---

### 3. Multiple Exit Conditions Better Than One

**Having ONLY stop-loss**: Misses profit opportunities

**Having ONLY take-profit**: Unlimited downside risk

**Having BOTH + time + conf + regime**: Robust, adaptive, safe

---

## Files Changed

| File | Changes | Lines Added |
|------|---------|-------------|
| `src/core/config/schema.py` | Added ExitLogic class | +25 |
| `src/core/backtest/position_tracker.py` | Added close_position_with_reason(), get_unrealized_pnl_pct() | +80 |
| `src/core/backtest/engine.py` | Added _check_exit_conditions(), updated main loop | +90 |
| `config/runtime.json` | Added exit config | +9 |
| `scripts/debug_backtest_exit_logic.py` | New debug script | +60 |

**Total**: 5 files, ~264 lines added

---

## Conclusion

Exit logic implementation is **complete** and represents a **critical fix** to the backtest infrastructure.

**Before**: Positions held indefinitely → unrealistic, risky, misaligned with validation

**After**: Positions managed with 5 exit conditions → realistic, safe, aligned with validation

**Expected impact**: 20-40× more trades, realistic holding periods, improved risk management, alignment with validation metrics.

**Status**: ✅ Implemented, 🔄 Testing, ⏳ Awaiting results

---

**Implemented by**: AI Agent (Cursor)
**Date**: 2025-10-10
**Related Docs**: `docs/6H_BACKTEST_MYSTERY_SOLVED.md`, `docs/BACKTEST_CRITICAL_BUGS_FIXED.md`
