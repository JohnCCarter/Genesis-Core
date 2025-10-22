# TODO - Genesis-Core

**Current Phase:** Phase-6c ✅ COMPLETE  
**Status:** Production-Ready System | Strategy Decision Needed  
**Last Updated:** 2025-10-10  
**Branch:** phase-5

---

## ✅ PHASE 1-6c: COMPLETE

### **Phase 1-2: Foundation** ✅
- Strategy pipeline (features, probability, confidence, regime, decision)
- Observability (metrics, dashboard, audit logging)
- SSOT Config API
- Backtest Framework
- Data Foundation

### **Phase 3-4: ML Pipeline** ✅
- Feature Engineering (precompute features)
- Label Generation (triple-barrier)
- Model Training (Logistic Regression)
- Model Evaluation & Calibration
- Champion Selection

### **Phase 5: Advanced Validation** ✅
- Centralized feature loading
- Champion Decision Matrix
- Visualization (radar charts, summary plots)
- Purged Walk-Forward CV
- Provenance tracking
- Drift monitoring (PSI/K-S)
- Model Cards & Championship Tickets

### **Phase 6a: BB Bug Fix** ✅ **CRITICAL**
- **Found:** ddof=1 vs ddof=0 (1.21% systematic error in BB)
- **Fixed:** src/core/indicators/vectorized.py
- **Validated:** Bit-exact parity (3.44e-10 max diff)
- **Impact:** ALL previous features & models were INVALID

### **Phase 6b: Systematic Indicator Validation** ✅
- Created validation framework (validate_all_indicators.py)
- Tested ALL 4 core indicators
- Result: Machine precision (no other bugs found)

### **Phase 6c: Regime-Aware Calibration** ✅
- Analyzed ML calibration per regime
- Implemented regime-specific Platt scaling
- Unified regime detection (regime_unified.py)
- Integrated into pipeline (detect → calibrate → decide)
- Result: Bear regime boost a=4.15 (+18% probability!)

**📚 Complete details:** `docs/PHASE-6_LEARNINGS.md`
di
---

## 🎯 CURRENT SYSTEM STATUS

### **✅ Technical Health: 10/10**
```
✅ 334/334 tests passing
✅ All indicators validated (machine precision)
✅ Regime-aware calibration active
✅ Data integrity confirmed (93.75%)
✅ Clean codebase (Ruff + Black + Bandit)
✅ Production-ready infrastructure
```

### **⚠️ Strategy Clarity: 5/10**
```
Model: tBTCUSD_1h_v3.json
IC: +0.0528 @ 20-bar (EXCELLENT)
Strategy: Mean reversion (buy dips, 58.6% win in Bear)
Issue: Bitcoin 1h is MEAN REVERSION market, NOT trend-following!
```

**Key Discovery:**
- ❌ ALL trend features have NEGATIVE IC (ema_slope: -0.0318)
- ✅ Volatility features have POSITIVE IC (atr_pct: +0.058, Bear: +0.25!)
- 🎯 Model learned: "Buy oversold dips in high volatility"

---

## 🚨 STRATEGIC DECISION NEEDED

### **The Technical System Works Perfectly. The Question Is:**

**Option A: Test Higher Timeframes** ⏰ **RECOMMENDED**
```
Hypothesis: Trend-following may work on 4h/1D?

Action Plan:
1. Fetch tBTCUSD 4h data (6-12 months)
   python scripts/fetch_historical.py tBTCUSD 4h --months 6

2. Precompute features (vectorized, fast!)
   python scripts/precompute_features_fast.py --symbol tBTCUSD --timeframe 4h

3. Run comprehensive feature analysis
   python scripts/comprehensive_feature_analysis.py --symbol tBTCUSD --timeframe 4h

4. DECISION based on results:
   IF trend features have POSITIVE IC on 4h:
     → Build trend-following model on 4h timeframe
   ELSE:
     → Accept that mean reversion is Bitcoin's nature

Timeline: 1-2 hours
Risk: Low (just data analysis)
Reward: Clarity on trend vs mean-reversion
```

**Option B: Optimize Mean Reversion** 🔄
```
Accept: Bitcoin 1h is mean reversion market

Action Plan:
1. Optimize entry timing (extreme oversold + high vol)
2. Implement tight stops (reversals are quick!)
3. Better exit strategy (take profit on bounce)
4. Focus on HighVol regime (IC +0.24!)

Timeline: 2-3 days
Risk: Medium (strategy might still be marginal)
Reward: Optimized system for what works
```

**Option C: Research New Approach** 🧪
```
Explore: Order flow, market microstructure, etc.

Action Plan:
1. Study what ACTUALLY works on crypto 1h
2. Research new indicator types
3. Test systematically (with our validation framework)

Timeline: 1-2 weeks
Risk: High (unknown territory)
Reward: Potentially discover better edge
```

---

## 📊 CURRENT PERFORMANCE

### **Model: tBTCUSD_1h_v3.json**

**IC Metrics:**
- 5-bar:  IC +0.0388 (p<0.001, ICIR 0.54)
- 10-bar: IC +0.0461 (p<0.001, ICIR 0.50)
- 20-bar: IC +0.0528 (p<0.001, ICIR 0.51) ✅ EXCELLENT

**Regime Performance:**
| Regime | IC | Win Rate | Calibration | Threshold |
|--------|-----|----------|-------------|-----------|
| Bear | +0.0946 | 58.6% | a=4.15 (boost) | 0.30 (low) |
| Bull | +0.0124 | 47.7% | a=1.24 (mild) | 0.90 (high) |
| Ranging | +0.0456 | 52.4% | a=1.98 (mod) | 0.50 (normal) |

**Features (v15 - Mean Reversion Optimized):**
1. rsi_inv_lag1 (lagged inverted RSI)
2. volatility_shift_ma3 (smoothed volatility)
3. bb_position_inv_ma3 (inverted BB position)
4. rsi_vol_interaction (cross-product)
5. vol_regime (categorical volatility)

---

## 📁 KEY FILES

### **Active Models:**
- `config/models/tBTCUSD_1h.json` - Current model with regime calibration
- `results/models/tBTCUSD_1h_v3*.json` - Model + provenance + metrics

### **Validation Results:**
- `results/validation/CALIBRATION_ANALYSIS.md` - Regime calibration analysis
- `results/validation/candle_integrity.json` - Data quality (93.75%)
- `results/validation/indicator_validation.json` - All indicators validated
- `results/feature_analysis/comprehensive_ic_analysis.json` - 25 features tested

### **Documentation:**
- `README.agents.md` - Agent workflow & Phase status
- `docs/PHASE-6_LEARNINGS.md` - Complete Phase-6 discoveries
- `docs/ADVANCED_VALIDATION_PRODUCTION.md` - Production ML guide
- `docs/INDICATORS_REFERENCE.md` - Indicator cheat sheet
- `docs/FEATURE_COMPUTATION_MODES.md` - AS-OF semantics (CRITICAL!)

### **Key Scripts:**
- `scripts/comprehensive_feature_analysis.py` - Test 25 features across regimes
- `scripts/validate_all_indicators.py` - Systematic indicator validation
- `scripts/calibrate_by_regime.py` - Regime-aware calibration
- `scripts/precompute_features_fast.py` - Vectorized feature computation
- `scripts/validate_candle_integrity.py` - Data quality checks

---

## 🔄 NEXT ACTIONS (Choose Path)

### **IF CHOOSING OPTION A (Recommended):**

```bash
# 1. Fetch 4h data
python scripts/fetch_historical.py tBTCUSD 4h --months 6

# 2. Precompute features (fast!)
python scripts/precompute_features_fast.py --symbol tBTCUSD --timeframe 4h

# 3. Analyze features
python scripts/comprehensive_feature_analysis.py --symbol tBTCUSD --timeframe 4h

# 4. Review results in:
results/feature_analysis/comprehensive_ic_analysis_4h.json

# 5. DECISION:
# - If trend features have POSITIVE IC → Build 4h model
# - If trend features have NEGATIVE IC → Accept mean reversion
```

### **IF CHOOSING OPTION B:**

```bash
# 1. Optimize entry conditions (extreme oversold)
# Edit: src/core/strategy/features.py
# - Tighten volatility thresholds
# - Add extreme RSI conditions

# 2. Implement tight stops
# Edit: config/runtime.json
# - Reduce stop loss from -0.3% to -0.15%

# 3. Better exit strategy
# Edit: src/core/strategy/decision.py
# - Add take-profit logic on bounce

# 4. Test with backtest
python scripts/run_backtest.py --model tBTCUSD_1h_v3 --timeframe 1h
```

### **IF CHOOSING OPTION C:**

```bash
# 1. Research phase (external)
# - Study successful crypto 1h strategies
# - Identify new indicator types
# - Document findings

# 2. Prototype new indicators
# Create: src/core/indicators/<new_indicator>.py

# 3. Test systematically
python scripts/comprehensive_feature_analysis.py --symbol tBTCUSD --timeframe 1h

# 4. Validate with our framework
python scripts/validate_all_indicators.py
```

---

## 📚 REFERENCE

### **Archived Documentation:**
- `docs/archive/TODO_PHASE3.5_superseded.md` - Old Phase 3.5 plan (BB bug era)
- `docs/archive/TODO_PROJECT_superseded.md` - Old project TODO (BB bug era)
- `docs/archive/CHANGELOG_pre-phase6.md` - Old changelog (pre-Phase 6)
- `results/archive_2025-10-08/` - Old experiment results
- `results/archive_2025-10-09/` - Phase-6 experiments before BB fix

### **Why Archived?**
ALL models and features from before 2025-10-10 were trained/computed with INCORRECT Bollinger Bands (ddof=1 bug). They are INVALID and must NOT be used!

---

## 🎯 RECOMMENDATION

**Start with Option A (Test 4h Timeframe):**

**Why:**
- ✅ Quick (1-2 hours)
- ✅ Low risk (just analysis)
- ✅ Gives clarity (trend works or not?)
- ✅ Data-driven decision
- ✅ Uses our validated framework

**If 4h shows POSITIVE IC for trend features:**
- Build trend-following model on 4h
- Keep mean-reversion model on 1h
- Use both (multi-timeframe strategy!)

**If 4h ALSO shows NEGATIVE IC for trend:**
- Accept mean reversion is reality
- Optimize mean-reversion strategy
- Focus on HighVol regime edge

**Either way, we get CLARITY!** 🎯

---

## 📝 STABILIZATION PHASE POLICY

**Code Stability > New Features**

Every code change must either:
- ✅ Solve a concrete problem, OR
- ✅ Increase reliability, performance, or readability

**Green-Light Checklist:**
1. ✅ Solves a defined need/problem
2. ✅ Does not unexpectedly affect other parts
3. ✅ Has unit tests or validated measurement
4. ✅ Is documented (docstring with purpose & usage)
5. ✅ Passes Ruff + pytest without warnings

---

**Status:** ✅ **SYSTEM READY. AWAITING STRATEGIC DIRECTION.** 🚀

