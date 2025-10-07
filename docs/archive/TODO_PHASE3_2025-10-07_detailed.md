# TODO - Phase 3: ML & Backtest

## Status: Phase 1 ✅ & Phase 2 ✅ KLART | Phase 3 → Priority 1 KLART ✅

---

## 🎯 Mål: Phase 3
- Samla historisk data
- Bygga backtest-framework
- Träna ML-modeller från historik
- Validera och deploya champion-modeller

---

## Prioritet 1: Data Foundation (KRITISKT) ✅ KLART

### 1.1 Historical Data Fetcher ✅
- [x] Implementera `scripts/fetch_historical.py`
  - [x] Bitfinex REST API integration (`/v2/candles/trade:TIMEFRAME:SYMBOL/hist`)
  - [x] Pagination för stora dataset (max 10000 candles/request)
  - [x] Rate limiting (27 req/min för candles endpoint)
  - [x] Error handling & retry med backoff (rate limit detection)
  - [x] Progress tracking (tqdm progressbar)

### 1.2 Data Storage ✅
- [x] Skapa `data/` directory structure:
  ```
  data/
  ├── candles/
  │   ├── tBTCUSD_1m.parquet    (98,273 candles, 2.3 MB)
  │   ├── tBTCUSD_15m.parquet   (8,632 candles, 233 KB)
  │   ├── tBTCUSD_1h.parquet    (2,160 candles, 71 KB)
  │   ├── tETHUSD_15m.parquet   (8,638 candles, 311 KB)
  │   ├── tETHUSD_1h.parquet    (2,160 candles, 86 KB)
  │   └── ...
  ├── features/
  │   └── (pre-computed features)
  └── metadata/
      ├── *_meta.json           (fetch metadata)
      └── *_validation.json     (quality reports)
  ```
- [x] Använd Parquet-format (pandas/pyarrow)
- [x] Schema: `[timestamp, open, high, low, close, volume]`
- [x] Indexering på timestamp för snabb lookup
- [x] Dokumenterad i `data/DATA_FORMAT.md`

### 1.3 Data Validation ✅
- [x] Implementera `scripts/validate_data.py`
  - [x] Check för gaps (missing timestamps) med coverage %
  - [x] Check för duplicates
  - [x] Check för outliers (price spikes >10%)
  - [x] Check för zero volume
  - [x] Check för OHLC consistency
  - [x] Generera data quality report med quality score (0-1)
  - [x] Spara validation report till metadata

### 1.4 Data Versioning ✅
- [x] Metadata-fil per dataset
  ```json
  {
    "symbol": "tBTCUSD",
    "timeframe": "15m",
    "fetched_at": "2025-10-07T...",
    "start_date": "2025-07-09...",
    "end_date": "2025-10-07...",
    "total_candles": 8632,
    "months_requested": 3,
    "source": "bitfinex_public_api"
  }
  ```
  Plus validation report:
  ```json
  {
    "summary": {
      "quality_score": 0.9991,
      "total_candles": 8632
    },
    "gaps": {"coverage": 0.9991, "missing_count": 8},
    "duplicates": {"duplicate_count": 0},
    "outliers": {"outlier_count": 0},
    "zero_volume": {"zero_volume_count": 0},
    "ohlc": {"total_invalid": 0}
  }
  ```
- [x] Git LFS → INTE NÖDVÄNDIG (totalt ~3 MB)

### 1.5 Initial Data Collection ✅
- [x] Fetch 3 månader tBTCUSD: 1m (75% coverage), 15m (99.91%), 1h (100%)
- [x] Fetch 3 månader tETHUSD: 15m (99.98%), 1h (100%)
- [x] Validera kvalitet: 15m/1h = EXCELLENT (>99.9%)
- [x] Dokumentera i `data/DATA_FORMAT.md`

**🎉 RESULTAT:**
| Symbol | Timeframe | Candles | Coverage | Quality | Size |
|--------|-----------|---------|----------|---------|------|
| tBTCUSD | 1m  | 98,273 | 75.83% | [POOR] | 2.3 MB |
| tBTCUSD | 15m | 8,632  | 99.91% | [EXCELLENT] | 233 KB |
| tBTCUSD | 1h  | 2,160  | 100%   | [EXCELLENT] | 71 KB |
| tETHUSD | 15m | 8,638  | 99.98% | [EXCELLENT] | 311 KB |
| tETHUSD | 1h  | 2,160  | 100%   | [EXCELLENT] | 86 KB |

**Total disk: ~3 MB**

---

## Prioritet 2: Backtest Framework (HÖGT)

### 2.1 Core Backtest Engine
- [ ] Implementera `src/core/backtest/engine.py`
  - [ ] `BacktestEngine` class
  - [ ] Load candles från parquet
  - [ ] Replay chronologically (bar-by-bar)
  - [ ] Execute pipeline för varje bar
  - [ ] State management (carry state mellan bars)

### 2.2 Position Tracker
- [ ] Implementera `src/core/backtest/position_tracker.py`
  - [ ] Track open positions
  - [ ] Calculate unrealized PnL
  - [ ] Handle LONG/SHORT entries/exits
  - [ ] Commission/slippage simulation
  - [ ] Position sizing validation

### 2.3 Performance Metrics
- [ ] Implementera `src/core/backtest/metrics.py`
  - [ ] Total return
  - [ ] Sharpe ratio
  - [ ] Max drawdown
  - [ ] Win rate
  - [ ] Avg win/loss
  - [ ] Profit factor
  - [ ] Calmar ratio
  - [ ] Trades per day

### 2.4 Backtest Report
- [ ] Implementera `src/core/backtest/report.py`
  - [ ] Generate HTML report
  - [ ] Equity curve plot
  - [ ] Drawdown plot
  - [ ] Trade distribution
  - [ ] Monthly returns heatmap
  - [ ] Export till JSON/CSV

### 2.5 Backtest Script
- [ ] Implementera `scripts/run_backtest.py`
  ```bash
  python scripts/run_backtest.py \
    --symbol tBTCUSD \
    --timeframe 1m \
    --start 2024-04-01 \
    --end 2024-10-01 \
    --config config/runtime.seed.json \
    --output results/backtest_btc_1m.html
  ```

### 2.6 Tests
- [ ] `tests/test_backtest_engine.py`
- [ ] `tests/test_position_tracker.py`
- [ ] `tests/test_metrics.py`
- [ ] Integration test: full backtest med dummy data

---

## Prioritet 3: ML Training Pipeline (HÖGT)

### 3.1 Feature Engineering
- [ ] Implementera `scripts/precompute_features.py`
  - [ ] Batch-process alla candles
  - [ ] Extract features (EMA, RSI, ADX, ATR)
  - [ ] Spara till `data/features/`
  - [ ] Cache med timestamp-check

### 3.2 Label Generation
- [ ] Implementera `src/core/ml/labeling.py`
  - [ ] Forward-looking returns (10/20/50 bars)
  - [ ] Binary: price_up (1) vs price_down (0)
  - [ ] Avoid lookahead bias
  - [ ] Handle bars nära slutet (no future data)

### 3.3 Training Script
- [ ] Implementera `scripts/train_model.py`
  - [ ] Load features + labels
  - [ ] Train/val/test split (60/20/20)
  - [ ] Logistic regression baseline (sklearn)
  - [ ] Hyperparameter tuning (GridSearchCV)
  - [ ] Save weights till model file
  - [ ] Versioning (`tBTCUSD_v2.json`)

### 3.4 Model Evaluation
- [ ] Implementera `src/core/ml/evaluation.py`
  - [ ] Log loss
  - [ ] Brier score
  - [ ] ROC-AUC
  - [ ] Precision/Recall
  - [ ] Reliability diagram
  - [ ] Confusion matrix

### 3.5 Calibration
- [ ] Implementera `src/core/ml/calibration.py`
  - [ ] Isotonic regression (sklearn)
  - [ ] Platt scaling (logistic)
  - [ ] Save calibration params
  - [ ] Before/after reliability plots

### 3.6 Model Comparison
- [ ] Implementera `scripts/compare_models.py`
  - [ ] Baseline (placeholder vikter) vs ML-tränad
  - [ ] Metrics side-by-side
  - [ ] Backtest båda
  - [ ] Statistical significance test

### 3.7 Champion Selection
- [ ] Implementera `scripts/select_champion.py`
  - [ ] Compare candidates
  - [ ] Select based on log loss + robusthet
  - [ ] Update `config/models/registry.json`
  - [ ] Backup old champion (rollback-support)
  - [ ] Log decision i `logs/champion_selection.jsonl`

---

## Prioritet 4: Integration & Validation (MEDIUM)

### 4.1 End-to-End Test
- [ ] Implementera `scripts/e2e_ml_workflow.py`
  - [ ] Fetch data → Precompute features → Train → Backtest → Deploy
  - [ ] Verify alla steg fungerar
  - [ ] Timing & resource usage

### 4.2 Live Validation
- [ ] Implementera `scripts/live_validation.py`
  - [ ] Samla live pipeline-resultat
  - [ ] Jämför predictions vs outcomes
  - [ ] Calculate drift (PSI/KS)
  - [ ] Alert vid degradation

### 4.3 Documentation
- [ ] `docs/ML_TRAINING.md` - Träningsprocedur
- [ ] `docs/BACKTEST_GUIDE.md` - Hur man kör backtest
- [ ] `docs/DATA_PIPELINE.md` - Data management
- [ ] `docs/CHAMPION_SELECTION.md` - Model selection process

### 4.4 CI/CD Integration
- [ ] Add backtest till CI (optional smoke test)
- [ ] Add data validation till CI
- [ ] Pre-commit hook för model file validation

---

## Prioritet 5: Monitoring & Maintenance (LÅG)

### 5.1 Drift Detection
- [ ] Automatisk PSI/KS calculation på live data
- [ ] Alert vid drift > threshold
- [ ] Weekly drift report

### 5.2 Model Retraining
- [ ] Scheduled retraining (monthly?)
- [ ] Incremental data updates
- [ ] Champion challenge process

### 5.3 Performance Dashboard
- [ ] Live trading metrics
- [ ] Model performance över tid
- [ ] Data quality monitoring

---

## Dependencies & Nya Paket

✅ **KLART:** ML dependencies redan tillagda i `pyproject.toml`
```toml
[project.optional-dependencies]
ml = [
    "scikit-learn>=1.3.0",
    "pandas>=2.0.0",
    "pyarrow>=13.0.0",  # Parquet support
    "matplotlib>=3.7.0",
    "seaborn>=0.12.0",
    "tqdm>=4.65.0",  # Progress bars
]
```

**Installation:** `pip install -e .[ml]`

---

## Milstolpar

- [ ] **Milestone 1:** Data Foundation Complete
  - 6 månader historisk data för BTC/ETH
  - Validation pipeline fungerar
  - Estimated: 1-2 veckor

- [ ] **Milestone 2:** Backtest Engine Complete
  - Full backtest för placeholder-vikter
  - Performance metrics genereras
  - Estimated: 2-3 veckor

- [ ] **Milestone 3:** ML Pipeline Complete
  - ML-modell tränad och kalibrerad
  - Bättre än baseline i backtest
  - Estimated: 2-3 veckor

- [ ] **Milestone 4:** Production Ready
  - Champion deployed till ModelRegistry
  - Live validation fungerar
  - Documentation komplett
  - Estimated: 1 vecka

**Total Estimated Time: 6-9 veckor**

---

## Risker & Mitigations

### Risk 1: Data Quality Issues
- **Risk:** Gaps, outliers, incorrect data från Bitfinex
- **Mitigation:** Robust validation, multiple data sources, manual inspection

### Risk 2: Overfitting
- **Risk:** ML-modell funkar i backtest men inte live
- **Mitigation:** Proper train/val/test splits, walk-forward validation, simple models först

### Risk 3: Lookahead Bias
- **Risk:** Använder framtida data i training → orealistiska resultat
- **Mitigation:** Strict time-based splits, review feature engineering noga

### Risk 4: Computational Resources
- **Risk:** Training/backtest tar för lång tid
- **Mitigation:** Start med små dataset, optimera senare, använd caching

---

## Nästa Konkreta Steg

**Förberedelser (Klart):**
- [x] ML dependencies i `pyproject.toml`
- [x] Data directory structure skapad
- [x] `.gitignore` uppdaterad
- [x] Schema dokumenterad
- [x] Phase-3 branch skapad

**Nästa (Priority 1.1 - Historical Data Fetcher):**
1. [x] Installera ML dependencies: `pip install -e .[ml]`
2. [ ] Implementera `scripts/fetch_historical.py`
3. [ ] Fetch 1 månad tBTCUSD 1m data (test)
4. [ ] Validera data quality
5. [ ] Expand till 6 månader alla timeframes

**Status:** Data Foundation påbörjad - redo för Historical Fetcher! 🚀
