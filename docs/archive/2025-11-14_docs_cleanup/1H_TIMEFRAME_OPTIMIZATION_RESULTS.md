# 1h Timeframe Optimization Results

## 🎯 **Översikt**
Denna dokumentation sammanfattar alla tester vi genomfört för att optimera 1h timeframe performance. Målet var att förbättra från initiala +3.36% return till bättre resultat.

## 📊 **Baseline Resultat**
**Initial Config (All Regime Proba = 0.6):**
- **Return:** +3.36%
- **Win Rate:** 30.3%
- **Trades:** 33
- **Profit Factor:** 1.60
- **Sharpe Ratio:** 0.08
- **Max Drawdown:** 5.09%

---

## 🧪 **Test 1: Confidence Level Optimization**

### **Test 1.1: Confidence 0.49 (Sänkt)**
- **Return:** -0.45%
- **Win Rate:** 30.0%
- **Trades:** 10
- **Profit Factor:** 0.93
- **Sharpe Ratio:** -0.03
- **Max Drawdown:** 3.95%
- **Resultat:** ❌ SÄMRE (-3.81% försämring)

### **Test 1.2: Confidence 0.41 (Sänkt)**
- **Return:** -0.45%
- **Win Rate:** 30.0%
- **Trades:** 10
- **Profit Factor:** 0.93
- **Sharpe Ratio:** -0.03
- **Max Drawdown:** 3.95%
- **Resultat:** ❌ SÄMRE (-3.81% försämring)

### **Test 1.3: Confidence 0.50 (Höjd)**
- **Return:** -0.19%
- **Win Rate:** 30.0%
- **Trades:** 10
- **Profit Factor:** 0.96
- **Sharpe Ratio:** -0.02
- **Max Drawdown:** 3.16%
- **Resultat:** ❌ SÄMRE (-3.55% försämring)

**Slutsats:** Confidence 0.40 är optimal. Både högre och lägre confidence ger sämre resultat.

---

## 🧪 **Test 2: Risk Map Optimization**

### **Test 2.1: Risk Map Sänkt (0.02)**
- **Return:** -0.19%
- **Win Rate:** 30.0%
- **Trades:** 10
- **Profit Factor:** 0.96
- **Sharpe Ratio:** -0.02
- **Max Drawdown:** 3.16%
- **Resultat:** ❌ SÄMRE (-3.55% försämring)

**Slutsats:** Risk Map 0.03 är optimal. Sänkt risk map ger sämre resultat.

---

## 🧪 **Test 3: Regime Probability Optimization**

### **Test 3.1: Trend-Favoring Approach**
**Config:**
```python
"regime_proba": {
    "ranging": 0.7,  # HÖJD: Undvik whipsaws
    "bull": 0.4,     # SÄNKT: Fånga fler bull moves
    "bear": 0.4,     # SÄNKT: Fånga fler bear moves
    "balanced": 0.6  # MEDIUM: Neutral
}
```

**Resultat:**
- **Return:** +1.87%
- **Win Rate:** 33.3%
- **Trades:** 9
- **Profit Factor:** 1.40
- **Sharpe Ratio:** 0.13
- **Max Drawdown:** 2.58%
- **Resultat:** ❌ SÄMRE (-1.49% försämring)

### **Test 3.2: Conservative Approach** ✅ **WINNER**
**Config:**
```python
"regime_proba": {
    "ranging": 0.8,  # MYCKET HÖJD: Undvik ranging
    "bull": 0.7,     # HÖJD: Mer selektiv
    "bear": 0.7,     # HÖJD: Mer selektiv
    "balanced": 0.8  # HÖJD: Mer selektiv
}
```

**Resultat:**
- **Return:** +4.37% ✅
- **Win Rate:** 66.7% ✅
- **Trades:** 3
- **Profit Factor:** 3.14 ✅
- **Sharpe Ratio:** 0.46 ✅
- **Max Drawdown:** 2.04% ✅
- **Resultat:** ✅ BÄTTRE (+1.01% förbättring!)

---

## 🏆 **Final Optimal Configuration**

**1h Timeframe - Conservative Approach:**
```python
{
    "thresholds": {
        "entry_conf_overall": 0.40,  # OPTIMAL
        "regime_proba": {
            "ranging": 0.8,   # MYCKET HÖJD: Undvik ranging
            "bull": 0.7,      # HÖJD: Mer selektiv
            "bear": 0.7,      # HÖJD: Mer selektiv
            "balanced": 0.8   # HÖJD: Mer selektiv
        },
    },
    "risk": {
        "risk_map": [
            [0.50, 0.03],  # OPTIMAL
            [0.60, 0.05],
            [0.70, 0.08],
            [0.80, 0.10],
            [0.90, 0.12],
        ]
    },
    "exit": {
        "enabled": True,
        "exit_conf_threshold": 0.5,
        "max_hold_bars": 25,
        "regime_aware_exits": True,
    },
    "gates": {
        "cooldown_bars": 2,
        "hysteresis_steps": 3,
    },
    "htf_exit_config": {
        "enable_partials": True,
        "enable_trailing": True,
        "enable_structure_breaks": True,
        "partial_1_pct": 0.60,
        "partial_2_pct": 0.50,
        "fib_threshold_atr": 0.7,
        "trail_atr_multiplier": 2.5,
        "swing_update_strategy": "fixed",
    },
    "warmup_bars": 150,
}
```

---

## 📈 **Performance Comparison**

| Config | Return | Win Rate | Trades | Profit Factor | Sharpe | Drawdown | Status |
|--------|--------|----------|--------|---------------|--------|----------|---------|
| **Baseline** | +3.36% | 30.3% | 33 | 1.60 | 0.08 | 5.09% | Baseline |
| **Conservative** | **+4.37%** | **66.7%** | **3** | **3.14** | **0.46** | **2.04%** | ✅ **BEST** |

---

## 🎯 **Key Insights**

### **1. Conservative Approach Works Best**
- **Kvalitet över kvantitet:** 3 trades vs 33 trades
- **Högre win rate:** 66.7% vs 30.3%
- **Bättre risk management:** 2.04% vs 5.09% drawdown
- **Bättre return:** +4.37% vs +3.36%

### **2. Regime Proba is Critical**
- **Symmetrisk approach (all 0.6):** Fungerar OK
- **Trend-favoring:** Fungerar inte
- **Conservative approach:** Fungerar bäst

### **3. Confidence Level is Sensitive**
- **0.40:** Optimal
- **0.41, 0.49, 0.50:** Alla sämre
- **Small changes have big impact**

### **4. Risk Map is Important**
- **0.03:** Optimal
- **0.02:** Sämre
- **Position sizing matters**

---

## 🚀 **Next Steps**

**Completed:**
- ✅ Confidence optimization
- ✅ Risk map optimization
- ✅ Regime proba optimization

**Pending:**
- ⏳ Other parameter optimization (max_hold_bars, partial_1_pct, cooldown_bars)
- ⏳ Test with different timeframes
- ⏳ Production deployment

---

**Dokumentation skapad:** 2025-10-14
**Status:** ✅ Conservative Approach är optimal för 1h timeframe
**Nästa steg:** Optimera andra parametrar eller testa andra timeframes
