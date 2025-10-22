# TODO - Phase 3.5: ML Improvement

**Branch:** phase-4
**Status:** ✅ IMPLEMENTATION KLART | ✅ TRAINING KLART | ⏳ BACKTEST ÅTERSTÅR
**Goal:** Förbättra ML model från AUC 0.517 → 0.65+ innan production deployment
**Senast uppdaterad:** 2025-10-08 12:05
**Bästa Resultat:** AUC 0.5987 (Adaptive 6m) - +15.8% förbättring från baseline!

---

## 🎯 **MÅLSÄTTNING**

### **Nuvarande Performance (Champion Model):**
- AUC: 0.517 (barely better than random 0.5)
- Accuracy: 0.500 (random guess level)
- Features: 2 (ema_delta_pct, rsi) - för få!
- Signal Rate: 100% (trade every prediction)
- Label Strategy: Simple binary next-candle up/down (noisy)

### **Förbättrad Performance (Mål efter retraining):**
- AUC: **> 0.65** (meaningful edge)
- Accuracy: **> 0.60** (consistent wins)
- Features: **11** (balanced, no overfitting)
- Signal Rate: **30-40%** (filter low confidence)
- Label Strategy: Triple-barrier with realistic profit targets
- Sharpe Ratio: **> 1.5** (backtest validation)

---

## ✅ **IMPLEMENTERAT (2025-10-08)**

### **Priority 1: Feature Expansion** ✅ KLART
**Resultat: 2 features → 11 features (550% expansion)**

**Nya Indicators:**
- `src/core/indicators/bollinger.py` - Bollinger Bands, BB Width, BB Position, Squeeze (23 tests)
- `src/core/indicators/volume.py` - Volume change, spikes, trend, OBV, divergence (36 tests)

**Förbättrad Regime Detection:**
- `src/core/strategy/regime.py` - Bull/Bear/Ranging/Balanced (11 tests)
- `detect_regime_from_candles()` - Convenience function

**Feature Integration:**
- `src/core/strategy/features.py` - Nu returnerar 11 features:
  1. `ema_delta_pct` (original)
  2. `rsi` (original)
  3. `atr_pct` (volatility)
  4. `bb_width` (volatility squeeze)
  5. `bb_position` (support/resistance)
  6. `adx` (trend strength)
  7. `ema_slope` (trend direction)
  8. `price_vs_ema` (position)
  9. `vol_change` (volume confirmation)
  10. `vol_trend` (volume momentum)
  11. `obv_normalized` (accumulation/distribution)

### **Priority 2: Triple-Barrier Labeling** ✅ KLART
**Resultat: Realistic trade scenarios implementerade**

**Nya Labeling Methods:**
- `generate_triple_barrier_labels()` - Fixed thresholds
  - Profit target: +0.5% (tuned from 0.3%)
  - Stop loss: -0.3% (tuned from 0.2%)
  - Max holding: 10 bars (tuned from 5)
  - Filters noise: Small moves → None label
  - 18 comprehensive tests

- `generate_adaptive_triple_barrier_labels()` - ATR-adaptive ⭐ **VINNARE**
  - Volatility-aware barriers
  - Profit: 1.5x ATR
  - Stop: 1.0x ATR
  - High vol → wider barriers
  - Low vol → tighter barriers
  - **Resultat: AUC 0.5987 (+3.9% vs fixed)**

### **Priority 3: Confidence Thresholds** ✅ KLART
**Resultat: Edge filtering implementerat**

**Förbättringar:**
- `src/core/strategy/decision.py` - Min edge requirement
- Filter trades där p_buy - p_sell < threshold
- Configurable via `cfg["thresholds"]["min_edge"]`
- Default: 0.0 (disabled, backward compatible)
- 5 tests för edge filtering

**Exempel:**
- p_buy=0.70, p_sell=0.65, edge=0.05 → BLOCKED (if min_edge=0.20)
- p_buy=0.80, p_sell=0.50, edge=0.30 → ALLOWED

---

## ✅ **KLART - TRAINING & VALIDATION (2025-10-08)**

### **Priority 4: Adaptive Triple-Barrier Training** ✅ KLART
**Resultat: Adaptive > Fixed (+3.9% AUC)**

**Implementation:**
- ✅ `scripts/train_model.py` uppdaterad med:
  - `--use-adaptive-triple-barrier` flag
  - `--profit-multiplier` parameter (default 1.5)
  - `--stop-multiplier` parameter (default 1.0)
  - ATR-beräkning integration
  - Code quality: black + ruff passed

**Training Experiments (4 modeller):**

1. **Fixed 6m (v3_1h):**
   - AUC: 0.5761
   - Data: 6 months
   - Labeling: Fixed (0.5%/0.3%)
   - Samples: 4,037
   - Filtered: 6.5%

2. **Fixed 1y (v3_1year):**
   - AUC: 0.5092 ❌ (Regime shift!)
   - Data: 1 year
   - Labeling: Fixed (0.5%/0.3%)
   - Samples: 4,948
   - Filtered: 4.5%

3. **Adaptive 1y (v3_adaptive_1year):**
   - AUC: 0.4922 ❌ (Too aggressive!)
   - Data: 1 year
   - Labeling: Adaptive (1.5x/1.0x ATR)
   - Samples: 4,522
   - Filtered: 12.8%

4. **Adaptive 6m (v3_adaptive_6m)** ⭐ **VINNARE:**
   - **AUC: 0.5987** ✅✅ (+15.8% vs baseline!)
   - Data: 6 months (recent only)
   - Labeling: Adaptive (1.5x/1.0x ATR)
   - Samples: 2,280 (high quality)
   - Filtered: 12.0% (aggressive noise removal)

**Key Findings:**
- ✅ Adaptive > Fixed (+3.9% AUC)
- ✅ Recent data (6m) >> Historical data (1y)
- ✅ Quality > Quantity (2,280 samples enough)
- ✅ Market non-stationarity confirmed
- ❌ 1-year data causes -11.6% AUC drop

**Results Logged:**
- ✅ All models saved: `results/models/tBTCUSD_1h_*.json`
- ✅ All metrics saved: `results/models/tBTCUSD_1h_*_metrics.json`
- ✅ Comprehensive report: `results/TRAINING_RESULTS_2025-10-08.md`

---

## ⏳ **ÅTERSTÅENDE ARBETE**

### **Priority 5.3: Backtest with Thresholds** ⏳ VALIDATION
- [ ] Configure min_edge parameter
  - [ ] Test values: [0.0, 0.10, 0.15, 0.20, 0.25]
  - [ ] Measure impact på signal rate
- [ ] Run backtest med nya model + thresholds
- [ ] Measure metrics:
  - [ ] Signal rate (target: 30-40%)
  - [ ] Win rate (target: > 55%)
  - [ ] Sharpe ratio (target: > 1.5)
  - [ ] Max drawdown (target: < 15%)
- [ ] Generate comparison report
- [ ] **Estimerad tid:** 15-20 min

### **Priority 5.4: Validation & Decision** ⏳ PÅGÅENDE
- [x] Training validation (20% val data) ✅
- [x] Compare models (4 experiments) ✅
- [x] Generate results report (`results/TRAINING_RESULTS_2025-10-08.md`) ✅
- [ ] Out-of-sample testing (test set)
- [ ] Backtest with real-world scenarios
- [ ] **Decision:**
  - [ ] Current: AUC 0.5987 (need > 0.65 for deploy)
  - [ ] Options: Feature importance, regime models, longer timeframes
- [ ] Final deployment decision

---

## 📊 **IMPLEMENTATION STATUS**

### **✅ KLART (2025-10-08 12:05):**
- ✅ Bollinger Bands indicator (23 tests)
- ✅ Volume indicators (36 tests)
- ✅ Enhanced regime detection (11 tests)
- ✅ Triple-barrier labeling (18 tests)
- ✅ Confidence edge filtering (5 tests)
- ✅ Feature integration (11 features)
- ✅ **Feature regeneration (11 features on 6m & 1y data)**
- ✅ **Adaptive triple-barrier implementation**
- ✅ **4 training experiments completed**
- ✅ **Champion model: v3_adaptive_6m (AUC 0.5987)**
- ✅ **Results report generated**
- ✅ All 270 tests pass
- ✅ Code quality (black, ruff, bandit)
- ✅ Committed & pushed to phase-4

### **⏳ KVAR ATT GÖRA:**
- ⏳ **Backtest with thresholds (Priority 1)**
- ⏳ Feature importance analysis (Priority 2)
- ⏳ Out-of-sample validation (Priority 3)
- ⏳ Production deployment decision (if AUC > 0.65)
- ⏳ **Total estimerad tid:** ~30-45 min

---

## 🚀 **QUICK START GUIDE**

### **Champion Model Usage:**

**Model:** `results/models/tBTCUSD_1h_v3_adaptive_6m.json`

**Retrain med samma config:**
```bash
# Fetch 6 months data
python scripts/fetch_historical.py --symbol tBTCUSD --timeframe 1h --months 6

# Regenerate features (11 features)
python scripts/precompute_features.py --symbol tBTCUSD --timeframe 1h

# Train with adaptive triple-barrier
python scripts/train_model.py \
  --symbol tBTCUSD \
  --timeframe 1h \
  --use-adaptive-triple-barrier \
  --profit-multiplier 1.5 \
  --stop-multiplier 1.0 \
  --max-holding 10 \
  --version v3_adaptive_6m
```

**Evaluate Model:**
```bash
python scripts/evaluate_model.py \
  --model results/models/tBTCUSD_1h_v3_adaptive_6m.json \
  --symbol tBTCUSD \
  --timeframe 1h
```

**Backtest (TODO):**
```bash
# Configure min_edge in config/strategy/defaults.json
# Run backtest engine (script not created yet)
```

---

## 📈 **ACHIEVED IMPROVEMENTS**

| Metric | Baseline | Current (v3_adaptive_6m) | Target | Status |
|--------|----------|--------------------------|--------|--------|
| Features | 2 | **11** ✅ | 11 | ✅ KLART |
| AUC | 0.517 | **0.5987** ✅ | > 0.65 | ⚠️ Close! (+15.8%) |
| Accuracy | 0.500 | TBD | > 0.60 | ⏳ Need evaluation |
| Signal Rate | 100% | TBD | 30-40% | ⏳ Config min_edge |
| Win Rate | ~50% | TBD | > 55% | ⏳ Need backtest |
| Sharpe Ratio | ~0 | TBD | > 1.5 | ⏳ Need backtest |

**Progress:** 15.8% AUC improvement achieved! Need 8.7% more to reach 0.65 target.

---

## 🔗 **RELATERADE FILER**

**Nya Indicators:**
- `src/core/indicators/bollinger.py` - Bollinger Bands
- `src/core/indicators/volume.py` - Volume analysis

**Uppdaterade Filer:**
- `src/core/strategy/features.py` - 11 features extraction
- `src/core/strategy/regime.py` - Bull/Bear/Ranging detection
- `src/core/strategy/decision.py` - Min edge requirement
- `src/core/ml/labeling.py` - Triple-barrier methods

**Test Files:**
- `tests/test_bollinger.py` - 23 tests
- `tests/test_volume.py` - 36 tests
- `tests/test_regime.py` - 11 tests (updated)
- `tests/test_triple_barrier.py` - 18 tests
- `tests/test_decision_edge.py` - 5 tests

**Scripts som behöver uppdateras:**
- `scripts/precompute_features.py` - ⏳ Update för 11 features
- `scripts/train_model.py` - ⏳ Add triple-barrier option

**Dokumentation:**
- `TODO.md` - Main TODO (high-level overview)
- `TODO_PHASE3.5.md` - Denna fil (detailed plan)

---

## ⚠️ **VIKTIGA NOTERINGAR**

**Innan Retraining:**
1. Backup existing models (`results/models/tBTCUSD_15m_v2.json`)
2. Backup existing features (`data/features/tBTCUSD_15m.parquet`)
3. Test new indicators manually först

**Under Retraining:**
1. Monitor feature extraction (ska få 11 features, inte 2)
2. Monitor label distribution (many None labels = OK, filters noise)
3. Monitor training progress (GridSearchCV kan ta längre tid)

**Efter Retraining:**
1. Compare AUC: old vs new
2. If worse: Debug (check features, labels, data quality)
3. If better but < 0.65: Consider regime-specific models
4. If > 0.65: Proceed to deployment!

---

**Notering:** Phase 3.5 implementation komplett. Redo för user validation och retraining.
