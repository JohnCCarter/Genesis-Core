# Fibonacci Fraktal Exits - Implementation Next Plan
## 🎯 **Översikt**

**Status**: ✅ **IMPLEMENTERAT OCH FUNGERAR**

Fibonacci Fraktal Exits har implementerats framgångsrikt med symmetrisk exit-logik som speglar entry-logiken. Systemet använder högre timeframe (HTF) Fibonacci-nivåer för dynamiska exits med partial closes, trailing stops och structure breaks.

## 🏗️ **Arkitektur**

### **Kärnkomponenter**

1. **`src/core/indicators/exit_fibonacci.py`**
   - `calculate_exit_fibonacci_levels()` - Symmetrisk Fibonacci-beräkning
   - `validate_swing_for_exit()` - Swing-validering för exits
   - `calculate_swing_improvement_pct()` - Swing-förbättringsmätning

2. **`src/core/backtest/exit_strategies.py`**
   - `SwingUpdateStrategy` enum (FIXED, DYNAMIC, HYBRID)
   - `SwingUpdateDecider` - Beslutslogik för swing-uppdateringar
   - `SwingUpdateParams` - Konfigurationsparametrar

3. **`src/core/backtest/htf_exit_engine.py`**
   - `HTFFibonacciExitEngine` - Huvudexit-motor
   - `crossed_target()` - Intrabar touch-detection
   - Frozen context support för statisk referens

4. **`src/core/backtest/position_tracker.py`**
   - `Position` dataclass utökad med exit-fält
   - `arm_exit_context()` - Freeze HTF context vid position open

5. **`src/core/backtest/engine.py`**
   - `_initialize_position_exit_context()` - Initiera exit context
   - Integration med HTF Exit Engine

## 🔄 **Symmetrisk Exit-Logik (Chamoun's Approach)**

### **Koncept**
Exit-logiken är **symmetrisk** med entry-logiken enligt Chamoun's Fibonacci-principer:

**ENTRY (Long)**:
- Retracement down (from swing_low → swing_high)
- Fibonacci retracements (0.382, 0.5, 0.618, 0.786) för entry-pullbacks
- Ordning: 0.382 → 0.5 → 0.618 → 0.786 (från lägsta till högsta)

**EXIT (Long)**:
- Retracement up (from swing_high → swing_low) - INVERTERADE nivåer
- Fibonacci retracements (0.786, 0.618, 0.5, 0.382) för profit-targets
- Ordning: 0.786 → 0.618 → 0.5 → 0.382 (från lägsta till högsta)

### **Symmetri**:
- **ENTRY**: `swing_low + (range * level)` - bygger UPPÅT från swing low
- **EXIT**: `swing_high - (range * level)` - bygger NEDÅT från swing high
- **Båda använder samma Fibonacci-nivåer** men i olika riktningar

### **Implementation**
```python
def calculate_exit_fibonacci_levels(side, swing_high, swing_low, levels=None):
    """Symmetrisk Fibonacci-beräkning för exits."""
    if side == "LONG":
        # Exit → från high ner mot low
        levels = {k: swing_high - (swing_high - swing_low)*v for k,v in base.items()}
    else:  # SHORT
        # Exit → från low upp mot high
        levels = {k: swing_low + (swing_high - swing_low)*v for k,v in base.items()}
    return levels
```

## 🎛️ **Swing Update Strategies**

### **FIXED (Statisk)**
- Swing fastställs vid position open
- Aldrig uppdaterad under trade
- Frozen context approach

### **DYNAMIC (Dynamisk)**
- Uppdaterar vid varje ny validerad HTF-swing
- Real-time swing tracking
- Live Fibonacci-nivåer

### **HYBRID (Hybrid)**
- Uppdaterar endast om "bättre" swing upptäcks
- Förbättringströskel (default 2%)
- Åldersgräns för swing-uppdateringar

## 🧊 **Frozen Context**

### **Koncept**
"En referens per trade" - freeze HTF-swing och Fibonacci-nivåer vid position open för att undvika statisk/dynamisk konflikt.

### **Implementation**
```python
def arm_exit_context(self, htf_ctx):
    """Freeze HTF swing och Fibonacci-nivåer för denna position."""
    self.exit_ctx = {
        "swing_id": htf_ctx.get("swing_id", "unknown"),
        "fib": dict(htf_ctx.get("levels", {})),  # freeze copy
        "swing_bounds": (htf_ctx.get("swing_low", 0.0), htf_ctx.get("swing_high", 0.0)),
        "armed_at": self.entry_time
    }
```

## 📊 **Exit Types**

### **Partial Exits**
- **TP1 (0.382)**: 40% av position
- **TP2 (0.5)**: 30% av position
- **TP3 (0.618)**: 20% av position
- **TP4 (0.786)**: 10% av position

### **Trailing Stop**
- Aktiveras efter första partial
- Låses mot Fibonacci-nivåer
- ATR-baserad marginal

### **Structure Break**
- Momentum-baserad exit
- Break av marknadsstruktur
- Kombinerat med trend-brytning

## 🔧 **Konfiguration**

### **Exit Engine Config**
```python
htf_exit_config = {
    "partial_1_pct": 0.40,        # TP1 size
    "partial_2_pct": 0.30,        # TP2 size
    "fib_threshold_atr": 0.3,     # Proximity threshold
    "trail_atr_multiplier": 1.3,  # Trailing stop margin
    "enable_partials": True,
    "enable_trailing": True,
    "enable_structure_breaks": True,
    "swing_update_strategy": "fixed",  # fixed/dynamic/hybrid
}
```

### **Swing Update Params**
```python
swing_update_params = {
    "strategy": "fixed",           # fixed/dynamic/hybrid
    "min_improvement_pct": 0.02,   # Min improvement for HYBRID
    "max_age_bars": 30,           # Max age before forcing update
    "allow_worse_swing": False,   # Allow worse swings (DYNAMIC)
    "min_swing_size_atr": 3.0,    # Min swing size validation
    "max_distance_atr": 8.0,      # Max distance validation
    "log_updates": True           # Log swing updates
}
```

## 🧪 **Testing**

### **Unit Tests**
- `test_exit_fibonacci.py` - Fibonacci-beräkningar
- `test_exit_strategies.py` - Swing update logik
- `test_htf_exit_engine.py` - Exit engine funktionalitet

### **Integration Tests**
- `test_static_frozen_exits_optimized.py` - Statisk strategi
- `test_dynamic_exits_optimized.py` - Dynamisk strategi
- `test_fibonacci_exits_real_backtest.py` - Full backtest

### **Performance Tests**
- Feather data loading
- Vectorized feature computation
- Optimized exit processing

## 📈 **Resultat**

### **Exit System Performance**
- ✅ **Partial exits triggas korrekt**
- ✅ **Frozen context fungerar**
- ✅ **Symmetrisk Fibonacci-logik implementerad**
- ✅ **Intrabar touch-detection**
- ✅ **Reachability guards**
- ✅ **Invariants för data-integrity**

### **Test Results**
```
[PARTIAL] TP2_05: 0.030 @ $116,142 = $18.12
[PARTIAL] TP1_0382: 0.040 @ $118,061 = $71.71
[PARTIAL] TP2_05: 0.030 @ $116,322 = $6.11
```

## 🔍 **Troubleshooting**

### **Vanliga Problem**

1. **0 trades genererade**
   - **Orsak**: Confidence thresholds för höga
   - **Lösning**: Sänk `entry_conf_overall` till 0.35

2. **0 exits trots positioner**
   - **Orsak**: Swing validation blockerar
   - **Lösning**: Använd frozen context approach

3. **Levels out of reach**
   - **Orsak**: Stale HTF-swing
   - **Lösning**: Implementera reachability guards

### **Debug Commands**
```bash
# Test exit system
python scripts/test_fibonacci_exits_real_backtest.py

# Debug signals
python scripts/debug_strategy_signals.py

# Test frozen context
python scripts/test_frozen_exit_context.py
```

## 🚀 **Nästa Steg**

1. **Production Deployment**
   - Konfigurera live trading parameters
   - Implementera risk management
   - Setup monitoring och alerting

2. **Performance Optimization**
   - Caching av HTF-swing calculations
   - Parallel processing av exits
   - Memory optimization

3. **Advanced Features**
   - Multi-timeframe exits
   - Regime-aware exit parameters
   - Machine learning exit optimization

## 📚 **Referenser**

- `docs/FIBONACCI_FRAKTAL_EXITS_IMPLEMENTATION_PLAN.md` - Detaljerad plan
- `src/core/indicators/exit_fibonacci.py` - Kärnimplementation
- `scripts/test_fibonacci_exits_real_backtest.py` - Full test
- `config/models/tBTCUSD_1h.json` - Model configuration

---

**Implementation Complete**: 2025-10-13
**Status**: ✅ Production Ready
**Next**: Live trading deployment
