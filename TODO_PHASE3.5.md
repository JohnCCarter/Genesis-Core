# TODO - Phase 3.5: ML Improvement

**Branch:** phase-4  
**Status:** ✅ IMPLEMENTATION KLART | ⏳ VALIDATION ÅTERSTÅR  
**Goal:** Förbättra ML model från AUC 0.517 → 0.65+ innan production deployment  
**Senast uppdaterad:** 2025-10-08

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
  - Profit target: +0.3% (configurable)
  - Stop loss: -0.2% (configurable)
  - Max holding: 5 bars
  - Filters noise: Small moves → None label
  - 18 comprehensive tests

- `generate_adaptive_triple_barrier_labels()` - ATR-adaptive
  - Volatility-aware barriers
  - High vol → wider barriers
  - Low vol → tighter barriers

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

## ⏳ **ÅTERSTÅENDE ARBETE**

### **Priority 5.1: Regenerate Features** ⏳ NÄSTA STEG
- [ ] Update `scripts/precompute_features.py`
  - [ ] Extract 11 features istället för 2
  - [ ] Verify all indicators calculate correctly
  - [ ] Handle NaN values från BB/Volume (require ~60 bars)
- [ ] Kör på tBTCUSD 15m
- [ ] Verify parquet output innehåller 11 columns
- [ ] **Estimerad tid:** 5-10 min

### **Priority 5.2: Retrain Models** ⏳ KRITISKT
- [ ] Update `scripts/train_model.py`
  - [ ] Option: Use triple-barrier labels (--use-triple-barrier flag?)
  - [ ] Skip None labels (only train on clear signals)
  - [ ] Report label distribution
- [ ] Train ny model:
  - [ ] Input: 11 features
  - [ ] Labels: Triple-barrier (profit +0.3%, stop -0.2%)
  - [ ] Split: 60/20/20 (train/val/test)
- [ ] **Jämför resultat:**
  - [ ] Old: 2 feat, simple labels, AUC 0.517
  - [ ] New: 11 feat, triple-barrier, AUC ???
- [ ] **Success target:** AUC > 0.65
- [ ] **Estimerad tid:** 10-15 min

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

### **Priority 5.4: Validation & Decision** ⏳ FINAL
- [ ] Out-of-sample testing (latest 20% data)
- [ ] Compare old vs new champion
- [ ] **Decision:**
  - [ ] If AUC > 0.65 AND Sharpe > 1.5 → Deploy
  - [ ] If insufficient → Iterate (regime models, more features)
- [ ] Generate `docs/PHASE3.5_RESULTS.md`

---

## 📊 **IMPLEMENTATION STATUS**

### **✅ KLART (2025-10-08):**
- ✅ Bollinger Bands indicator (23 tests)
- ✅ Volume indicators (36 tests)
- ✅ Enhanced regime detection (11 tests)
- ✅ Triple-barrier labeling (18 tests)
- ✅ Confidence edge filtering (5 tests)
- ✅ Feature integration (11 features)
- ✅ All 270 tests pass
- ✅ Code quality (black, ruff, bandit)
- ✅ Committed & pushed to phase-4

### **⏳ KVAR ATT GÖRA:**
- ⏳ Regenerate features (11 features)
- ⏳ Retrain models (triple-barrier labels)
- ⏳ Backtest with thresholds
- ⏳ Validate AUC improvement
- ⏳ Generate results report
- ⏳ **Total estimerad tid:** ~45-60 min

---

## 🚀 **QUICK START GUIDE**

### **För att fortsätta Phase 3.5 Validation:**

**Steg 1: Regenerate Features**
```bash
python scripts/precompute_features.py --symbol tBTCUSD --timeframe 15m
```

**Steg 2: Retrain Model**
```bash
python scripts/train_model.py \
  --symbol tBTCUSD \
  --timeframe 15m \
  --use-triple-barrier \
  --profit-pct 0.3 \
  --stop-pct 0.2
```

**Steg 3: Evaluate New Model**
```bash
python scripts/evaluate_model.py \
  --model results/models/tBTCUSD_15m_v3.json \
  --symbol tBTCUSD \
  --timeframe 15m
```

**Steg 4: Compare Results**
```bash
python scripts/select_champion.py \
  --baseline baseline \
  --ml-model v2 \
  --ml-improved v3
```

---

## 📈 **EXPECTED IMPROVEMENTS**

| Metric | Before | After (Target) | Method |
|--------|--------|----------------|--------|
| Features | 2 | **11** ✅ | Implemented |
| AUC | 0.517 | **> 0.65** ⏳ | Need retraining |
| Accuracy | 0.500 | **> 0.60** ⏳ | Need retraining |
| Signal Rate | 100% | **30-40%** ⏳ | Config min_edge |
| Win Rate | ~50% | **> 55%** ⏳ | Triple-barrier + edge |
| Sharpe Ratio | ~0 | **> 1.5** ⏳ | Need backtest |

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
