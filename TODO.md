# TODO - Genesis-Core

**Status:** Phase 1 & 2 ✅ KLART | Phase 3 ⏳ PÅGÅR  
**Senast uppdaterad:** 2025-10-07

---

## ✅ Phase 1 & 2: KLART (Arkiverat)

Allt från Phase 1 & 2 är komplett och testat. Se `docs/archive/TODO_2025-10-07_pre-phase3.md` för detaljer.

**Sammanfattning:**
- ✅ Strategy pipeline (features, probability, confidence, regime, decision)
- ✅ Observability (metrics, dashboard, audit logging)
- ✅ SSOT Config API (runtime.json, propose/validate)
- ✅ Backtest Framework (BacktestEngine, PositionTracker, Metrics, TradeLogger)
- ✅ Data Foundation (fetch_historical, validate_data, parquet storage)
- ✅ Comprehensive tests (115/115 passar)
- ✅ Code quality (0 linting errors, pristine)

---

## ⏳ Phase 3: ML Training Pipeline (PÅGÅR)

Se `TODO_PHASE3.md` för fullständig plan. Här är high-level översikt:

### Priority 3.1: Feature Engineering ✅ KLART
- [x] Implementera `scripts/precompute_features.py`
  - [x] Batch-process historical candles
  - [x] Extract EMA, RSI features (återanvänd extract_features())
  - [x] Spara till `data/features/*.parquet`
  - [x] Progress tracking med tqdm
- [x] Test: Verifiera feature output format
- [x] Processed: tBTCUSD 15m (8,632 rows), tBTCUSD 1h (2,160 rows)
- [x] Processed: tETHUSD 15m (8,638 rows), tETHUSD 1h (2,160 rows)
- [x] Total: ~604 KB features data

### Priority 3.2: Label Generation
- [ ] Implementera `src/core/ml/labeling.py`
  - [ ] Forward-looking returns (10/20/50 bars)
  - [ ] Binary labels: price_up (1) vs price_down (0)
  - [ ] Avoid lookahead bias
  - [ ] Handle edge cases (nära slutet av data)
- [ ] Test: Verifiera label alignment med features

### Priority 3.3: Training Script
- [ ] Implementera `scripts/train_model.py`
  - [ ] Load features + labels
  - [ ] Train/val/test split (60/20/20)
  - [ ] Logistic regression baseline (scikit-learn)
  - [ ] Hyperparameter tuning (GridSearchCV)
  - [ ] Save weights till model file (JSON)
  - [ ] Versioning (`tBTCUSD_v2.json`)
- [ ] Test: Verify model file format compatibility

### Priority 3.4: Model Evaluation
- [ ] Implementera `src/core/ml/evaluation.py`
  - [ ] Log loss, Brier score
  - [ ] ROC-AUC, Precision/Recall
  - [ ] Reliability diagram
  - [ ] Confusion matrix
- [ ] Generate evaluation report (JSON/HTML)

### Priority 3.5: Calibration
- [ ] Implementera `src/core/ml/calibration.py`
  - [ ] Isotonic regression (sklearn)
  - [ ] Platt scaling (logistic)
  - [ ] Save calibration params
  - [ ] Before/after reliability plots
- [ ] Test: Verify calibrated probabilities

### Priority 3.6: Champion Selection
- [ ] Implementera `scripts/select_champion.py`
  - [ ] Compare baseline vs ML-trained
  - [ ] Metrics side-by-side
  - [ ] Backtest comparison
  - [ ] Statistical significance test
  - [ ] Update `config/models/registry.json`
  - [ ] Backup old champion (rollback-support)
- [ ] Log decision i `logs/champion_selection.jsonl`

---

## 🎯 Milstones

- [ ] **Milestone 3.1:** Feature Engineering Complete (ETA: 1 vecka)
- [ ] **Milestone 3.2:** Training Pipeline Complete (ETA: 2 veckor)
- [ ] **Milestone 3.3:** First ML Model Trained (ETA: 3 veckor)
- [ ] **Milestone 3.4:** Champion Deployed (ETA: 4 veckor)

---

## 📝 Regler (fortsätter gälla)

- ✅ Separation of concerns
- ✅ Pure, deterministiska funktioner
- ✅ Latensbudget: ≤ 20 ms/modul
- ✅ Comprehensive tests för all ny logik
- ✅ Inga hemligheter i loggar
- ✅ Code review innan merge till main

---

## 🔗 Relaterade Dokument

- `PHASE3_CONFLICTS.md` - Potentiella konflikter & lösningar
- `GRANSKNING_2025-10-07.md` - Code review rapport
- `docs/archive/` - Arkiverad dokumentation (historik)

---

**Notering:** Starta inga implementationer utan uttryckligt godkännande. Diskutera approach först.
