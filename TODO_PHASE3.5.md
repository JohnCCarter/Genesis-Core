# TODO - Phase 3.5: ML Improvement

**Branch:** phase-4  
**Status:** 🚀 PÅGÅR  
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

### **Förbättrad Performance (Mål):**
- AUC: **> 0.65** (meaningful edge)
- Accuracy: **> 0.60** (consistent wins)
- Features: **12-15** (balanced, no overfitting)
- Signal Rate: **30-40%** (filter low confidence)
- Label Strategy: Triple-barrier with realistic profit targets
- Sharpe Ratio: **> 1.5** (backtest validation)

---

## 📋 **PRIORITY 1: FEATURE EXPANSION** ⚡

**Mål:** Lägg till kompletterande features utan att överträna (2 → 12 features)

### **Task 1.1: Volatility Features** 🌊
- [ ] Implementera Bollinger Band Width i `indicators/`
  - [ ] `bollinger_bands(close, period=20, std_dev=2)`
  - [ ] `bb_width = (upper - lower) / middle`
  - [ ] `bb_position = (close - lower) / (upper - lower)` (squeeze indicator)
- [ ] Lägg till ATR-normalized metrics
  - [ ] `atr_normalized_move = price_change / atr`
  - [ ] `volatility_regime = atr / atr_ma(50)` (high/low vol)
- [ ] Test: Verifiera BB och ATR calculations

### **Task 1.2: Volume Features** 📈
- [ ] Implementera volume metrics i `indicators/`
  - [ ] `volume_change = (volume - volume_ma(20)) / volume_ma(20)`
  - [ ] `volume_spike = volume > 2 * volume_ma(20)`
  - [ ] `volume_trend = ema(volume, 10) / ema(volume, 50)`
- [ ] Test: Verifiera volume calculations

### **Task 1.3: Regime Detection Features** 📊
- [ ] Implementera regime classifier i `strategy/regime.py`
  - [ ] Bull: `price > ema(50) AND adx > 25`
  - [ ] Bear: `price < ema(50) AND adx > 25`
  - [ ] Ranging: `adx < 20`
  - [ ] Trending strength: `adx_value` (redan har ADX)
- [ ] Lägg till trend confirmation
  - [ ] `ema_alignment = ema(10) > ema(50) > ema(200)` (bull)
  - [ ] `ema_slope = (ema_now - ema_prev) / ema_prev`
- [ ] Test: Regime classification accuracy

### **Task 1.4: Multi-Timeframe Features** 🔄
- [ ] Implementera MTF feature extraction
  - [ ] Fetch 1h data för 15m model
  - [ ] Fetch 4h data för 15m model
  - [ ] Align timestamps (forward-fill)
- [ ] Add MTF momentum features
  - [ ] `h1_ema_trend = ema(10, 1h) > ema(50, 1h)`
  - [ ] `h4_rsi = rsi(14, 4h)`
  - [ ] `h1_adx = adx(14, 1h)` (higher TF trend strength)
- [ ] Test: MTF alignment and lag prevention

### **Task 1.5: Update Feature Extraction** 🔧
- [ ] Modify `strategy/features.py`
  - [ ] Add all new features to `extract_features()`
  - [ ] Maintain backward compatibility
  - [ ] Document feature definitions
- [ ] Modify `scripts/precompute_features.py`
  - [ ] Support multi-timeframe data loading
  - [ ] Compute all 12-15 features
  - [ ] Save to parquet with new schema
- [ ] Test: End-to-end feature generation

---

## 📋 **PRIORITY 2: TRIPLE-BARRIER LABELS** 🎯

**Mål:** Förbättra label quality med realistiska trade-setups

### **Task 2.1: Implement Triple-Barrier Logic**
- [ ] Create `src/core/ml/labeling.py` (update existing)
  - [ ] `generate_triple_barrier_labels()`
    - [ ] Profit threshold: +0.3% (configurable)
    - [ ] Stop threshold: -0.2% (configurable)
    - [ ] Max holding period: 5 candles (configurable)
    - [ ] Label = 1 if profit hit first
    - [ ] Label = 0 if stop hit first
    - [ ] Label = None if timeout with small move
  - [ ] Adaptive thresholds based on ATR
    - [ ] `profit_threshold = 1.5 * atr`
    - [ ] `stop_threshold = 1.0 * atr`
- [ ] Test: Triple-barrier labeling logic (25+ tests)

### **Task 2.2: Label Quality Metrics**
- [ ] Implement label analytics
  - [ ] Label distribution (1 vs 0 vs None)
  - [ ] Average holding period per label
  - [ ] Risk-reward ratio validation
  - [ ] Noise reduction vs simple labeling
- [ ] Visualization: Label quality report
- [ ] Test: Label quality validation

### **Task 2.3: Integration with Training**
- [ ] Update `scripts/train_model.py`
  - [ ] Use triple-barrier labels
  - [ ] Skip None labels (only train on clear signals)
  - [ ] Report label statistics
- [ ] Retrain models with new labels
- [ ] Compare performance: old vs new labels

---

## 📋 **PRIORITY 3: CONFIDENCE THRESHOLDS** 🛡️

**Mål:** Filter low-quality predictions, trade only high-confidence setups

### **Task 3.1: Enhance Decision Logic**
- [ ] Modify `strategy/decision.py`
  - [ ] Add `min_confidence` parameter (default 0.60)
  - [ ] Add `min_edge` parameter (default 0.20)
  - [ ] Logic:
    ```python
    if buy_prob > min_confidence and (buy_prob - sell_prob) > min_edge:
        return "LONG"
    elif sell_prob > min_confidence and (sell_prob - buy_prob) > min_edge:
        return "SHORT"
    else:
        return "NONE"  # HOLD
    ```
- [ ] Test: Confidence filtering logic

### **Task 3.2: Configuration Integration**
- [ ] Add confidence params to `config/strategy/defaults.json`
  - [ ] `"min_confidence": 0.60`
  - [ ] `"min_edge": 0.20`
  - [ ] `"enable_confidence_filter": true`
- [ ] Update FastAPI endpoints
  - [ ] `/strategy/evaluate` respects confidence filter
  - [ ] Response includes `confidence_filtered: bool`
- [ ] Test: E2E with confidence filtering

### **Task 3.3: Backtesting with Filters**
- [ ] Run backtest with different thresholds
  - [ ] `min_confidence = [0.50, 0.55, 0.60, 0.65, 0.70]`
  - [ ] Measure: Signal rate, Win rate, Sharpe ratio
- [ ] Find optimal threshold
- [ ] Document results

---

## 📋 **PRIORITY 4: REGIME-SPECIFIC MODELS** 🔄

**Mål:** Train specialized models for different market conditions

### **Task 4.1: Regime Classification**
- [ ] Implement robust regime detector
  - [ ] Use ADX + EMA for regime detection
  - [ ] Label historical data with regime
  - [ ] Validate regime transitions
- [ ] Test: Regime accuracy on historical data

### **Task 4.2: Split Training Data by Regime**
- [ ] Create `scripts/train_regime_models.py`
  - [ ] Split data: Bull, Bear, Ranging
  - [ ] Train separate model per regime
  - [ ] Handle imbalanced regime data
  - [ ] Save regime-specific models
- [ ] Test: Regime model training

### **Task 4.3: Regime-Aware Inference**
- [ ] Update `strategy/prob_model.py`
  - [ ] Detect current regime
  - [ ] Load appropriate regime model
  - [ ] Fallback to general model if needed
- [ ] Update model registry
  - [ ] Support regime-specific model loading
  - [ ] Cache regime models
- [ ] Test: Regime-aware predictions

---

## 📋 **PRIORITY 5: VALIDATION & BACKTESTING** ✅

**Mål:** Verifiera förbättrad performance innan deployment

### **Task 5.1: Walk-Forward Validation**
- [ ] Implement walk-forward CV
  - [ ] Train on N months, test on next 1 month
  - [ ] Roll forward, retrain, test
  - [ ] Aggregate results
- [ ] Measure: AUC, Sharpe, Win rate per period
- [ ] Test: Walk-forward implementation

### **Task 5.2: Comprehensive Backtesting**
- [ ] Run full backtest with improvements
  - [ ] New features (12-15)
  - [ ] Triple-barrier labels
  - [ ] Confidence thresholds
  - [ ] Regime-specific models
- [ ] Generate performance report
  - [ ] Sharpe ratio > 1.5
  - [ ] Max drawdown < 15%
  - [ ] Win rate > 55%
  - [ ] Signal rate 30-40%
- [ ] Compare: Baseline vs Improved

### **Task 5.3: Out-of-Sample Testing**
- [ ] Reserve latest 20% data for final test
- [ ] Zero training on test set
- [ ] Measure production-like performance
- [ ] Validate: AUC > 0.65, Sharpe > 1.5

---

## 📋 **PRIORITY 6: DOCUMENTATION & CLEANUP** 📝

**Mål:** Document improvements and prepare for Phase 4 deployment

### **Task 6.1: Update Documentation**
- [ ] Update `README.md` with Phase 3.5 results
- [ ] Update `TODO.md` with completion status
- [ ] Create `docs/PHASE3.5_RESULTS.md`
  - [ ] Before/after comparison
  - [ ] Feature importance analysis
  - [ ] Backtest results
  - [ ] Lessons learned

### **Task 6.2: Code Quality**
- [ ] Run black, ruff, bandit
- [ ] Ensure all tests pass (177+)
- [ ] Update type hints
- [ ] Add docstrings

### **Task 6.3: CI/CD**
- [ ] Ensure GitHub Actions passes
- [ ] Update pre-commit hooks
- [ ] Commit and push to phase-4 branch

---

## 🎯 **SUCCESS CRITERIA**

Phase 3.5 är komplett när:

- ✅ **AUC > 0.65** (test set)
- ✅ **Sharpe Ratio > 1.5** (backtest)
- ✅ **Signal Rate: 30-40%** (confidence filtering works)
- ✅ **Win Rate > 55%** (profitable edge)
- ✅ **Features: 12-15** (balanced complexity)
- ✅ **All tests pass** (no regressions)
- ✅ **CI/CD green** (production ready)

---

## 📊 **PROGRESS TRACKING**

### **Week 1: Foundation (Days 1-5)**
- [ ] Day 1-2: Feature Expansion (volatility, volume)
- [ ] Day 3: Multi-timeframe features
- [ ] Day 4: Triple-barrier labels
- [ ] Day 5: Confidence thresholds

### **Week 2: Advanced (Days 6-10)**
- [ ] Day 6-7: Regime detection & models
- [ ] Day 8: Walk-forward validation
- [ ] Day 9: Comprehensive backtesting
- [ ] Day 10: Documentation & cleanup

---

## 🔗 **RELATERADE DOKUMENT**

- `TODO.md` - Main project TODO
- `docs/PHASE3_CONFLICTS.md` - Conflicts and solutions
- `README.md` - Project documentation
- `CHANGELOG.md` - Version history

---

**Notering:** Alla ändringar ska testas och valideras innan merge till main.

