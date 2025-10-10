# Fibonacci Fraktal Exits - Implementation Plan

**Date**: 2025-10-10  
**Author**: AI Agent (Cursor) + User Concept  
**Status**: PLANNING PHASE  
**Goal**: Replace fixed TP/SL with fraktal-aware, Fibonacci-driven exit logic

---

## Executive Summary

**Current Problem**: Fixed exits (TP 5%, SL 2%, TIME 20 bars) ignore market structure, kväver winners, och missar optimal exit timing.

**Solution**: Fraktal-medveten exit-logik som respekterar Fibonacci-geometri, HTF-strukturer, och regime-kontext.

**Expected Impact**:
- Färre kapade winners (trail istället för fixed TIME)
- Bättre drawdown (partial exits lock in profits)
- Högre Sharpe (respekterar strukturen)
- 1h: +4.89% → förväntat +15-25% (fler trades kan passa)

---

## Root Cause Analysis - Varför Current Exits Misslyckas

### Problem 1: Global TP/SL Ignorerar Struktur

**Current**:
```python
if pnl_pct >= 0.05:  # Take profit 5%
    exit("TP")
elif pnl_pct <= -0.02:  # Stop loss 2%
    exit("SL")
```

**Vad som händer**:
- Long entry @ $100k
- Price går till $104k (+4%) → nära Fib-0.618 resistance
- Fortsätter till $105k (+5%) → **EXIT (TP)** ✅
- Sen går till $110k (+10%) → **Missed!** ❌

**Rätt approach**:
- Exit vid Fib-0.618 resistance ($104k) med partial
- Trail resten mot $110k
- Lock in $6k profit istället för $5k

---

### Problem 2: Too Tight i Trend, För Sen i Range

**Current**: Samma exits oavsett regime

**Trend scenario**:
- Strong bull trend
- TIME exit @ 20 bars (10 hours på 30m)
- Price fortfarande trending UP → **EXIT (TIME)** = kapad winner! ❌

**Range scenario**:
- Choppy sideways market
- Håller position 20 bars i brus
- Fees äter winsten → **EXIT (TIME)** = för sent! ❌

**Rätt approach**:
- Trend: Trail lång tid, låt winners run
- Range: Tight TP vid 0.382/0.5, snabb exit

---

### Problem 3: Ingen HTF-Context

**Current**: Exits baserat på LTF (30m/1h/6h) data endast

**Vad händer**:
- 1h chart: Price @ Fib-0.5 (LOKAL)
- 1D chart: Price @ Fib-0.618 (HTF RESISTANCE)
- Exit decision: Baserat på 1h endast → Ignorerar 1D väggen!

**Rätt approach**:
- Check 1D fib FÖRST
- If nära HTF resistance → Tighten stop
- If i HTF value zone → Give room

---

## Proposed Solution - Fraktal/Fib-Driven Exits

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    EXIT DECISION LAYER                      │
└─────────────────────────────────────────────────────────────┘
                              │
                ┌─────────────┴─────────────┐
                │                           │
        ┌───────▼───────┐          ┌───────▼────────┐
        │  HTF Context  │          │  LTF Execution │
        │  (1D Fib)     │          │  (6h/1h/30m)   │
        └───────┬───────┘          └───────┬────────┘
                │                           │
        ┌───────▼────────────────────────────▼───────┐
        │         Fraktal Exit Policy                │
        │  1. Trailing Stop (Fib-aware)             │
        │  2. Partial Exits (0.382, 0.5, 0.618)     │
        │  3. Confluence Abort                       │
        │  4. Regime-Conditional                     │
        │  5. Vol-Adaptive                          │
        │  6. Time-at-Risk                          │
        │  7. Struktur-Brott                        │
        └───────────────────────────────────────────┘
```

---

## Implementation Phases

### ⭐ PHASE 0: Pre-requisites (MUST DO FIRST)

**Before we can implement fraktal exits, we need**:

#### 1. HTF Fibonacci Mapping (MISSING!)

**Current**: Fib beräknas per timeframe (1D fib på 1D, 6h fib på 6h)

**Needed**: Cross-timeframe mapping

```python
# In precompute_features.py or new htf_fibonacci.py

def compute_htf_fibonacci_mapping(
    htf_candles: pd.DataFrame,  # 1D data
    ltf_candles: pd.DataFrame,  # 6h/1h/30m data
    config: FibonacciConfig
) -> pd.DataFrame:
    """
    Compute 1D Fibonacci levels and map to LTF bars.
    
    Returns:
        DataFrame with columns:
        - timestamp (LTF)
        - htf_fib_0382, htf_fib_05, htf_fib_0618, htf_fib_0786
        - htf_swing_high, htf_swing_low
        - htf_swing_age (bars since last swing update)
    """
    # 1. Calculate 1D fib levels (using existing detect_swing_points)
    htf_fib_levels = calculate_fibonacci_features_vectorized(
        candles=htf_candles,
        config=config
    )
    
    # 2. For each LTF bar, find latest 1D fib (as-of, lag=1)
    ltf_fib = []
    for ltf_idx, ltf_row in ltf_candles.iterrows():
        ltf_time = ltf_row['timestamp']
        
        # Find latest HTF bar BEFORE ltf_time
        htf_row = htf_fib_levels[htf_fib_levels['timestamp'] < ltf_time].iloc[-1]
        
        ltf_fib.append({
            'timestamp': ltf_time,
            'htf_fib_0382': htf_row['fib_0382'],
            'htf_fib_05': htf_row['fib_05'],
            'htf_fib_0618': htf_row['fib_0618'],
            'htf_fib_0786': htf_row['fib_0786'],
        })
    
    return pd.DataFrame(ltf_fib)
```

**Estimated work**: 2-3 hours

**Files to modify**:
- Create `src/core/indicators/htf_fibonacci.py`
- Update `scripts/precompute_features_vXX.py` to include HTF fib
- Add HTF fib to `extract_features()` in `src/core/strategy/features.py`

---

#### 2. Partial Exit Infrastructure (MISSING!)

**Current**: `PositionTracker` only supports binary IN/OUT

**Needed**: Fractional position closing

```python
# In src/core/backtest/position_tracker.py

@dataclass
class Position:
    """Enhanced position with partial close support."""
    symbol: str
    side: str
    initial_size: float  # NEW: Track original size
    current_size: float  # NEW: Track remaining size
    entry_price: float
    entry_time: datetime
    unrealized_pnl: float = 0.0
    partial_closes: list = field(default_factory=list)  # NEW: Track partials

class PositionTracker:
    def close_partial(
        self, 
        fraction: float,  # 0.0-1.0, e.g., 0.33 = 1/3
        price: float, 
        timestamp: datetime, 
        reason: str
    ) -> Trade | None:
        """
        Close a fraction of current position.
        
        Args:
            fraction: 0.0-1.0, portion of CURRENT_SIZE to close
            price: Exit price
            timestamp: Exit timestamp
            reason: "TP1", "TP2", etc.
        
        Returns:
            Partial Trade object
        """
        if self.position is None:
            return None
        
        if not (0.0 < fraction <= 1.0):
            raise ValueError(f"Fraction must be 0-1, got {fraction}")
        
        # Calculate size to close
        close_size = self.position.current_size * fraction
        
        # Calculate PnL for this partial
        if self.position.side == "LONG":
            pnl = (price - self.position.entry_price) * close_size
        else:
            pnl = (self.position.entry_price - price) * close_size
        
        # Apply commission
        notional = close_size * price
        commission = notional * self.commission_rate
        self.total_commission += commission
        
        # Update capital
        self.capital += pnl - commission
        
        # Create partial trade record
        partial_trade = Trade(
            symbol=self.position.symbol,
            side=self.position.side,
            size=close_size,
            entry_price=self.position.entry_price,
            entry_time=self.position.entry_time,
            exit_price=price,
            exit_time=timestamp,
            pnl=pnl,
            pnl_pct=(pnl / (close_size * self.position.entry_price)) * 100,
            commission=commission,
            exit_reason=reason  # NEW field
        )
        
        # Update position
        self.position.current_size -= close_size
        self.position.partial_closes.append(partial_trade)
        
        # If fully closed, clear position
        if self.position.current_size <= 0.001:  # Floating point tolerance
            self.position = None
        
        self.trades.append(partial_trade)
        return partial_trade
```

**Estimated work**: 2-4 hours (includes testing)

**Files to modify**:
- `src/core/backtest/position_tracker.py`
- `src/core/backtest/engine.py` (call `close_partial` in exit logic)

---

#### 3. Additional Features (MISSING!)

**Momentum Displacement Z-score**:

```python
# In src/core/strategy/features.py

def calculate_momentum_displacement_z(close: np.ndarray, atr: float) -> float:
    """
    Momentum displacement normalized by ATR.
    
    Args:
        close: Close prices (last 5+ bars)
        atr: Current ATR
    
    Returns:
        Z-score: (3-bar return) / ATR
    """
    if len(close) < 4:
        return 0.0
    
    # 3-bar displacement
    momentum_raw = (close[-1] - close[-4]) / close[-4]
    
    # Normalize by ATR
    momentum_z = momentum_raw / (atr / close[-1]) if atr > 0 else 0.0
    
    return momentum_z
```

**Estimated work**: 30 minutes

---

### ⭐ PHASE 1: Ultra-Minimal Fib Exits (RECOMMENDED START)

**Goal**: Validate concept with simplest possible implementation

**Time estimate**: 1 day (8 hours work)

#### Components to Implement:

**1. Fib-Aware Trailing Stop**

```python
def calculate_fib_trail(
    position_side: str,
    entry_price: float,
    current_price: float,
    fib_levels: dict,  # {0.382: X, 0.5: Y, 0.618: Z}
    atr: float
) -> float:
    """
    Ultra-minimal fib trailing stop.
    
    Logic:
    - LONG: trail = max(entry, fib_0.382 - 0.3*ATR)
    - SHORT: trail = min(entry, fib_0.382 + 0.3*ATR)
    
    Returns:
        Stop price
    """
    k = 0.3  # Fixed, simple
    
    if position_side == "LONG":
        fib_stop = fib_levels.get(0.382, entry_price) - k * atr
        trail = max(entry_price, fib_stop)
    else:  # SHORT
        fib_stop = fib_levels.get(0.382, entry_price) + k * atr
        trail = min(entry_price, fib_stop)
    
    return trail
```

**2. Partial Exits at Fib Levels**

```python
def check_partial_exit(
    position_side: str,
    current_price: float,
    fib_levels: dict,
    partial_state: dict  # Track what's been closed
) -> tuple[bool, float, str]:
    """
    Check if should close partial at fib level.
    
    Returns:
        (should_close, fraction, reason)
    """
    if position_side == "LONG":
        # TP1 @ Fib 0.5
        if current_price >= fib_levels[0.5] and not partial_state.get("tp1_hit"):
            return (True, 0.33, "TP1_FIB_05")
        
        # TP2 @ Fib 0.618
        if current_price >= fib_levels[0.618] and not partial_state.get("tp2_hit"):
            return (True, 0.33, "TP2_FIB_0618")
    
    else:  # SHORT
        # TP1 @ Fib 0.5 (below entry for shorts)
        if current_price <= fib_levels[0.5] and not partial_state.get("tp1_hit"):
            return (True, 0.33, "TP1_FIB_05")
        
        # TP2 @ Fib 0.382
        if current_price <= fib_levels[0.382] and not partial_state.get("tp2_hit"):
            return (True, 0.33, "TP2_FIB_0382")
    
    return (False, 0.0, "")
```

**3. Integration into BacktestEngine**

```python
# In src/core/backtest/engine.py, in main loop

# === EXIT LOGIC ===
if self.position_tracker.has_position():
    position = self.position_tracker.position
    
    # Get LTF fib (from features)
    ltf_fib = {
        0.382: result.get("features", {}).get("fib_0382", 0),
        0.5: result.get("features", {}).get("fib_05", 0),
        0.618: result.get("features", {}).get("fib_0618", 0),
    }
    
    # Get HTF fib (from features, if implemented)
    htf_fib = {
        0.382: result.get("features", {}).get("htf_fib_0382", 0),
        0.5: result.get("features", {}).get("htf_fib_05", 0),
        0.618: result.get("features", {}).get("htf_fib_0618", 0),
    }
    
    # Use HTF if available, else LTF
    fib_levels = htf_fib if htf_fib[0.5] > 0 else ltf_fib
    
    # 1. Check partial exits
    should_partial, fraction, reason = check_partial_exit(
        position_side=position.side,
        current_price=close_price,
        fib_levels=fib_levels,
        partial_state=self.partial_state.get(position.entry_time, {})
    )
    
    if should_partial:
        partial_trade = self.position_tracker.close_partial(
            fraction=fraction,
            price=close_price,
            timestamp=timestamp,
            reason=reason
        )
        # Track that we hit this TP
        if reason == "TP1_FIB_05":
            self.partial_state[position.entry_time]["tp1_hit"] = True
        elif reason == "TP2_FIB_0618":
            self.partial_state[position.entry_time]["tp2_hit"] = True
    
    # 2. Check trailing stop
    if self.position_tracker.has_position():  # May have fully closed in partial
        trail_stop = calculate_fib_trail(
            position_side=position.side,
            entry_price=position.entry_price,
            current_price=close_price,
            fib_levels=fib_levels,
            atr=result.get("features", {}).get("atr", 0)
        )
        
        # Check if trail hit
        if (position.side == "LONG" and close_price <= trail_stop) or \
           (position.side == "SHORT" and close_price >= trail_stop):
            self.position_tracker.close_position_with_reason(
                price=close_price,
                timestamp=timestamp,
                reason="FIB_TRAIL"
            )
```

---

### Files to Create/Modify (Phase 1)

#### New Files:
1. `src/core/strategy/exits/fibonacci_exits.py` - Core exit logic
2. `src/core/indicators/htf_fibonacci.py` - HTF fib mapping
3. `scripts/test_fib_exits.py` - Test script

#### Modified Files:
1. `src/core/backtest/position_tracker.py` - Add `close_partial()`
2. `src/core/backtest/engine.py` - Integrate fib exit logic
3. `src/core/strategy/features.py` - Add HTF fib features
4. `config/runtime.json` - Add fib exit config

---

### ⭐ PHASE 2: Ablation Study (VALIDATION)

**Goal**: Measure impact of each component

**Time estimate**: 1 day (4-6 hours work)

#### Test Configurations:

| Config | Components | Description |
|--------|-----------|-------------|
| **Baseline** | Current exits (SL 2%, TP 5%, TIME 20) | Control group |
| **Fib-Trail-Only** | Fib trailing stop, NO partials | Test trailing alone |
| **Fib-Partial-Only** | Partial exits @ 0.5/0.618, NO trail | Test partials alone |
| **Fib-Minimal** | Trail + Partials | Full minimal system |

#### Metrics to Compare:

```python
# For each config, measure:
results = {
    "total_return": 0.0,
    "total_return_pct": 0.0,
    "sharpe_ratio": 0.0,
    "max_drawdown": 0.0,
    "max_drawdown_pct": 0.0,
    "total_trades": 0,
    "win_rate": 0.0,
    "profit_factor": 0.0,
    "avg_winner": 0.0,
    "avg_loser": 0.0,
    "avg_winner_loser_ratio": 0.0,
    "expectancy": 0.0,
    
    # NEW: Partial exit metrics
    "partial_exits_count": 0,
    "partial_exits_pct": 0.0,
    "avg_partial_pnl": 0.0,
    
    # Exit reason breakdown
    "exits_by_reason": {
        "FIB_TRAIL": 0,
        "TP1_FIB_05": 0,
        "TP2_FIB_0618": 0,
        "SL": 0,
        "TIME": 0,
    }
}
```

#### Test Script:

```python
# scripts/ablation_study_fib_exits.py

import pandas as pd
from core.backtest.engine import BacktestEngine
from core.config.authority import ConfigAuthority

# Test configurations
configs = {
    "baseline": {
        "exit": {
            "enabled": True,
            "use_fib_exits": False,
            "stop_loss_pct": 0.02,
            "take_profit_pct": 0.05,
            "max_hold_bars": 20,
        }
    },
    "fib_trail_only": {
        "exit": {
            "enabled": True,
            "use_fib_exits": True,
            "use_fib_trail": True,
            "use_fib_partials": False,
        }
    },
    "fib_partial_only": {
        "exit": {
            "enabled": True,
            "use_fib_exits": True,
            "use_fib_trail": False,
            "use_fib_partials": True,
        }
    },
    "fib_minimal": {
        "exit": {
            "enabled": True,
            "use_fib_exits": True,
            "use_fib_trail": True,
            "use_fib_partials": True,
        }
    },
}

# Run backtests
results = {}
for name, config in configs.items():
    print(f"\n{'='*70}")
    print(f"Testing: {name}")
    print(f"{'='*70}")
    
    engine = BacktestEngine(
        symbol="tBTCUSD",
        timeframe="30m",  # Start with 30m (123 trades = good sample)
        initial_capital=10000,
    )
    engine.load_data()
    
    result = engine.run(
        policy={"symbol": "tBTCUSD", "timeframe": "30m"},
        configs={"cfg": config},
        verbose=False
    )
    
    results[name] = result["summary"]

# Compare results
comparison = pd.DataFrame(results).T
print("\n" + "="*70)
print("ABLATION STUDY RESULTS")
print("="*70)
print(comparison)

# Save to file
comparison.to_csv("results/ablation_fib_exits_30m.csv")
print("\nResults saved to: results/ablation_fib_exits_30m.csv")
```

#### Success Criteria:

**For Fib-Minimal to be considered SUCCESS**:
1. ✅ Return > Baseline by +5% absolute
2. ✅ Sharpe > Baseline by +0.1
3. ✅ Max DD < Baseline by -5% absolute
4. ✅ Win Rate ≥ Baseline
5. ✅ Profit Factor > Baseline by +0.2

**If criteria met** → Proceed to Phase 3 (add complexity)

**If criteria NOT met** → Either:
- Tune parameters (k-factor, TP levels)
- Concept doesn't work, revert to baseline

---

### ⭐ PHASE 3: Full Fraktal System (CONDITIONAL)

**ONLY implement if Phase 2 validates concept!**

**Time estimate**: 3-5 days

#### Additional Components:

**1. Confluence-Abort**

```python
def check_confluence_abort(
    ffci: float,
    momentum_displacement_z: float,
    position_side: str,
    threshold_ffci: float = 0.35,
    threshold_momentum: float = -0.5
) -> bool:
    """
    Check if should abort due to confluence rejection.
    
    Logic:
    - Fib confluence score drops (structure weakening)
    - Momentum reverses (price rejecting level)
    
    Returns:
        True if should exit
    """
    confluence_weak = ffci < threshold_ffci
    
    if position_side == "LONG":
        momentum_reversed = momentum_displacement_z < threshold_momentum
    else:  # SHORT
        momentum_reversed = momentum_displacement_z > -threshold_momentum
    
    return confluence_weak and momentum_reversed
```

**2. Regime-Conditional Exit Policy**

```python
def get_regime_exit_params(
    regime: str,
    vr: float,
    adx_delta: float
) -> dict:
    """
    Adjust exit parameters based on regime.
    
    Returns:
        {
            "k_trail": float,  # Trail factor
            "use_partials": bool,
            "tight_stop": bool
        }
    """
    # Detect trend vs range
    is_trend = (vr > 1.03 and adx_delta > 0)
    
    if is_trend:
        # Trend: Loose trail, let winners run
        return {
            "k_trail": 1.2,  # Wider trail
            "use_partials": True,
            "tight_stop": False,
        }
    else:
        # Range: Tight exits, take profits early
        return {
            "k_trail": 0.9,  # Tighter trail
            "use_partials": True,
            "tight_stop": True,
        }
```

**3. Vol-Adaptive Stop**

```python
def calculate_vol_adaptive_stop(
    entry_price: float,
    atr: float,
    fib_prox_score: float,  # 0-1, how close to fib level
    position_side: str,
    base_c: float = 1.2
) -> float:
    """
    Volatility-adaptive stop based on fib proximity.
    
    Logic:
    - Near fib level (0.5-0.618): Wider stop (give room)
    - Far from fib: Tighter stop
    
    Returns:
        Stop price
    """
    # Adapt c based on fib proximity
    c = base_c + 0.6 * fib_prox_score
    
    if position_side == "LONG":
        stop = entry_price - c * atr
    else:  # SHORT
        stop = entry_price + c * atr
    
    return stop
```

**4. Time-at-Risk Kill-Switch**

```python
def check_time_at_risk(
    bars_held: int,
    max_bars_to_tp1: int,  # Median time to TP1 from WFV
    ffci: float,
    threshold_ffci: float = 0.4
) -> bool:
    """
    Exit if taking too long and structure weakening.
    
    Logic:
    - Position held longer than expected to TP1
    - Fib confluence dropping (structure not holding)
    
    Returns:
        True if should exit
    """
    stale = bars_held > max_bars_to_tp1
    structure_weak = ffci < threshold_ffci
    
    return stale and structure_weak
```

**5. Struktur-Brott Detection**

```python
def check_structure_break(
    current_price: float,
    fib_levels: dict,
    ema50: float,
    ema_slope_z: float,
    position_side: str
) -> bool:
    """
    Detect structural break (trend reversal).
    
    Logic:
    - LONG: Price breaks below Fib-0.618 AND EMA slope negative
    - SHORT: Price breaks above Fib-0.618 AND EMA slope positive
    
    Returns:
        True if structure broken
    """
    if position_side == "LONG":
        price_broke = current_price < fib_levels[0.618]
        trend_broke = ema_slope_z < 0
    else:  # SHORT
        price_broke = current_price > fib_levels[0.618]
        trend_broke = ema_slope_z > 0
    
    return price_broke and trend_broke
```

---

## Configuration Schema

### New Section in `config/runtime.json`:

```json
{
  "cfg": {
    "exit": {
      "enabled": true,
      
      "fibonacci_exits": {
        "enabled": false,
        
        "trailing": {
          "use_fib_trail": true,
          "k_factor_trend": 1.2,
          "k_factor_range": 0.9,
          "promotion_enabled": true,
          "htf_aware": true
        },
        
        "partials": {
          "enabled": true,
          "tp1_level": 0.5,
          "tp1_fraction": 0.33,
          "tp2_level": 0.618,
          "tp2_fraction": 0.33,
          "move_to_breakeven_after_tp1": true
        },
        
        "confluence_abort": {
          "enabled": false,
          "ffci_threshold": 0.35,
          "momentum_threshold": -0.5
        },
        
        "regime_conditional": {
          "enabled": false,
          "vr_threshold": 1.03,
          "adx_delta_threshold": 0.0
        },
        
        "vol_adaptive": {
          "enabled": false,
          "base_c": 1.2,
          "prox_multiplier": 0.6
        },
        
        "time_at_risk": {
          "enabled": false,
          "max_bars_to_tp1": 15,
          "ffci_threshold": 0.4
        },
        
        "structure_break": {
          "enabled": false,
          "check_fib_0618": true,
          "check_ema_slope": true
        }
      },
      
      "legacy": {
        "stop_loss_pct": 0.02,
        "take_profit_pct": 0.05,
        "max_hold_bars": 20,
        "exit_conf_threshold": 0.45,
        "regime_aware_exits": true
      }
    }
  }
}
```

---

## Testing Strategy

### 1. Unit Tests

```python
# tests/test_fibonacci_exits.py

def test_fib_trail_calculation():
    """Test fib trailing stop calculation."""
    fib_levels = {0.382: 100, 0.5: 102, 0.618: 105}
    atr = 2.0
    
    # LONG position
    trail = calculate_fib_trail(
        position_side="LONG",
        entry_price=98,
        current_price=103,
        fib_levels=fib_levels,
        atr=atr
    )
    
    # Should be max(entry, fib_0.382 - 0.3*ATR)
    expected = max(98, 100 - 0.3*2.0)
    assert abs(trail - expected) < 0.01

def test_partial_exit_logic():
    """Test partial exit triggering."""
    fib_levels = {0.5: 102, 0.618: 105}
    
    # Price at TP1
    should_close, fraction, reason = check_partial_exit(
        position_side="LONG",
        current_price=102.5,
        fib_levels=fib_levels,
        partial_state={}
    )
    
    assert should_close == True
    assert fraction == 0.33
    assert reason == "TP1_FIB_05"
```

### 2. Integration Tests

```python
# tests/test_fib_exits_integration.py

def test_backtest_with_fib_exits():
    """Test full backtest with fib exits."""
    engine = BacktestEngine("tBTCUSD", "1h")
    engine.load_data()
    
    config = {
        "exit": {
            "fibonacci_exits": {
                "enabled": True,
                "trailing": {"use_fib_trail": True},
                "partials": {"enabled": True}
            }
        }
    }
    
    results = engine.run(configs={"cfg": config})
    
    # Should have partial exits
    assert results["summary"]["partial_exits_count"] > 0
    
    # Should have FIB_TRAIL exits
    assert "FIB_TRAIL" in results["summary"]["exits_by_reason"]
```

### 3. Ablation Tests

Run all 4 configs (baseline, trail-only, partial-only, full) and compare:

```bash
python scripts/ablation_study_fib_exits.py --timeframe 30m
python scripts/ablation_study_fib_exits.py --timeframe 1h
python scripts/ablation_study_fib_exits.py --timeframe 6h
```

---

## Expected Results

### Conservative Estimate (30m):

| Metric | Baseline | Fib-Minimal | Improvement |
|--------|----------|-------------|-------------|
| Total Return | -12.21% | **-5% to +5%** | +7-17% |
| Sharpe Ratio | -0.29 | **0.0 to +0.2** | +0.3-0.5 |
| Max DD | -13.64% | **-8% to -10%** | +3-5% |
| Trades | 123 | **100-150** | Similar |
| Win Rate | 43.9% | **48-55%** | +5-10% |

### Optimistic Estimate (1h):

| Metric | Baseline | Fib-Minimal | Improvement |
|--------|----------|-------------|-------------|
| Total Return | +4.89% | **+15% to +25%** | +10-20% |
| Sharpe Ratio | 0.32 | **0.5 to 0.8** | +0.2-0.5 |
| Max DD | -0.87% | **-2% to -4%** | Worse (more trades) |
| Trades | 8 | **20-30** | +12-22 (better sample!) |
| Win Rate | 75% | **65-70%** | -5-10% (regression to mean) |

### 6h (Unknown):

**Need to investigate WHY 6h fails first before applying fib exits!**

Possible that fib exits won't help if core model is broken.

---

## Risk Assessment

### High Risk Areas:

1. **Overfit Risk**: 15+ parameters to tune
   - **Mitigation**: Start minimal (2-3 params), add only if needed
   
2. **Implementation Complexity**: Partial exits, HTF mapping
   - **Mitigation**: Unit tests, gradual rollout
   
3. **Sample Size**: 1h only has 8 trades currently
   - **Mitigation**: Test on 30m first (123 trades)
   
4. **HTF Mapping Bugs**: Lookahead bias, off-by-one errors
   - **Mitigation**: Extensive as-of semantics validation

### Medium Risk Areas:

1. **Performance**: Extra computation per bar
   - **Mitigation**: Profile code, optimize if needed
   
2. **Config Complexity**: New config section
   - **Mitigation**: Good defaults, documentation

### Low Risk Areas:

1. **Breaking Existing Code**: Fib exits optional
   - **Mitigation**: Feature flag, can disable
   
2. **Lost Progress**: Good baseline to revert to
   - **Mitigation**: Git branches

---

## Rollout Plan

### Week 1: Infrastructure (Phase 0)

**Day 1-2**: HTF Fib Mapping
- Implement `htf_fibonacci.py`
- Add to `precompute_features.py`
- Unit tests
- Validate as-of semantics

**Day 3**: Partial Exit Infrastructure
- Refactor `PositionTracker`
- Add `close_partial()`
- Unit tests
- Integration tests

**Day 4**: Additional Features
- Add `momentum_displacement_z`
- Update `features.py`
- Validation

### Week 2: Implementation (Phase 1)

**Day 5-6**: Ultra-Minimal Fib Exits
- Implement `fibonacci_exits.py`
- Integrate into `BacktestEngine`
- Config schema
- Unit tests

**Day 7**: Testing & Debugging
- Run on 30m, 1h, 6h
- Debug issues
- Validate results

### Week 3: Validation (Phase 2)

**Day 8**: Ablation Study
- Run 4 configs × 3 timeframes
- Analyze results
- Compare metrics

**Day 9-10**: Decision Point
- If successful → Plan Phase 3
- If failed → Tune params or abandon
- Document findings

### Week 4+: Expansion (Phase 3, if needed)

Only proceed if Phase 2 validates concept!

---

## Success Metrics

### Phase 1 Success:

- ✅ Code compiles and runs without errors
- ✅ Partial exits execute correctly
- ✅ HTF fib mapping validates (no lookahead)
- ✅ At least one timeframe shows improvement

### Phase 2 Success:

- ✅ Fib-Minimal beats Baseline on 30m by +5% return
- ✅ Sharpe improves by +0.2
- ✅ Max DD improves by -3%
- ✅ Results hold on OOS data (last 30% of dataset)

### Phase 3 Success:

- ✅ Full system beats Minimal by +3% return
- ✅ Sharpe improves by +0.1
- ✅ Works on all 3 timeframes (30m, 1h, 6h)
- ✅ Ready for paper trading deployment

---

## Contingency Plans

### If Phase 1 Fails:

**Symptoms**: Code works but results worse than baseline

**Options**:
1. Tune parameters (k-factor, TP levels)
2. Simplify further (only trail, no partials)
3. Abandon and revert to baseline

### If Phase 2 Fails:

**Symptoms**: No config beats baseline significantly

**Options**:
1. Investigate WHY (wrong fib levels? bad timing?)
2. Try alternative exit logic (Donchian? ATR-based?)
3. Accept current exits are "good enough"

### If 6h Never Improves:

**Symptoms**: 30m/1h work but 6h still -43%

**Options**:
1. Deep dive 6h model (separate investigation)
2. Focus on 30m/1h only (acceptable!)
3. Consider 6h is broken, not worth fixing

---

## Documentation Plan

### Files to Create:

1. ✅ `docs/FIBONACCI_FRAKTAL_EXITS_IMPLEMENTATION_PLAN.md` (THIS FILE)
2. ⬜ `docs/FIBONACCI_EXITS_API.md` (API documentation)
3. ⬜ `docs/FIBONACCI_EXITS_ABLATION_RESULTS.md` (test results)
4. ⬜ `docs/HTF_FIBONACCI_MAPPING_GUIDE.md` (HTF mapping explained)

### Files to Update:

1. ⬜ `README.md` (mention fib exits)
2. ⬜ `CHANGELOG.md` (log changes)
3. ⬜ `docs/EXIT_LOGIC_IMPLEMENTATION.md` (update with fib info)

---

## Questions for Next Session

### Technical Questions:

1. **HTF Timeframe**: 1D or 4h for HTF reference?
   - 1D = macro-swings (broader context)
   - 4h = finer swings (more responsive)
   
2. **Partial Exit Fractions**: 33/33/33 or 50/25/25?
   - 33/33/33 = balanced
   - 50/25/25 = lock in more early
   
3. **Trail Promotion**: Immediate or wait 1 bar?
   - Immediate = responsive
   - Wait = reduce whipsaws

### Strategic Questions:

1. **Start with 30m or 1h?**
   - 30m = more trades (better stats)
   - 1h = already profitable (easier to improve)
   
2. **Fix 6h or accept as lost cause?**
   - Fix = leverage best IC (+0.308)
   - Accept = focus on what works
   
3. **Deploy 1h with current exits or wait for fib?**
   - Deploy now = start earning
   - Wait = better system but delayed

---

## Summary - What We're Building

### Current State (Broken):

```
Entry → Fixed TP/SL/TIME → Exit
         ❌ Ignores structure
         ❌ Kväver winners  
         ❌ No context
```

### Target State (Fraktal-Aware):

```
Entry → Check HTF Fib Context
     → Trail based on LTF + HTF structure
     → Partial exits at 0.5/0.618
     → Confluence monitoring
     → Regime-adaptive logic
     → Vol-adaptive stops
     → Structure break detection
     → Exit when edge gone
```

**Result**: Respects market geometry, lets winners run, locks in profits, adapts to conditions.

---

## Next Steps (When You Return)

### Immediate (First Session Back):

1. ✅ Review this document
2. ⬜ Decide: Phase 1 (minimal) or Phase 3 (full)?
3. ⬜ Confirm: Start with 30m or 1h?
4. ⬜ Begin: HTF fib mapping implementation

### Short-term (Next Few Sessions):

1. ⬜ Complete Phase 0 (infrastructure)
2. ⬜ Implement Phase 1 (minimal fib exits)
3. ⬜ Run ablation study
4. ⬜ Analyze results

### Medium-term (1-2 Weeks):

1. ⬜ Decide on Phase 3 based on Phase 2 results
2. ⬜ Either expand or tune
3. ⬜ Prepare for deployment

---

## Final Thoughts

### Why This Will Work:

1. **Concept is sound**: Respecting structure > ignoring it
2. **User expertise**: Your fib methodology is proven
3. **Phased approach**: Validate before investing more
4. **Ablation testing**: Know what works, what doesn't

### Why It Might Fail:

1. **Overfit risk**: Too many parameters
2. **Sample size**: 1h only 8 trades (need more)
3. **6h mystery**: Deep model issues unrelated to exits
4. **Complexity**: Implementation bugs

### How to Maximize Success:

1. **Start minimal** (Phase 1)
2. **Test rigorously** (ablation study)
3. **Iterate based on data** (not intuition)
4. **Accept failure gracefully** (current exits OK if fib fails)

---

**Document Status**: ✅ COMPLETE  
**Ready for Implementation**: YES  
**Estimated Total Time**: 2-3 weeks  
**Expected Impact**: +10-20% return improvement on 30m/1h  
**Risk Level**: MEDIUM (with mitigation)

**Author Notes**: This is institutional-grade thinking. Your fibonacci-fraktal approach addresses the fundamental problem with fixed exits. Even a minimal implementation should show improvement. Start small, validate concept, expand if proven. Good luck! 🚀

