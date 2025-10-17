### README för AI‑agenter (lokal utveckling)

Denna fil beskriver hur AI‑agenter ska arbeta lokalt med projektet.

**TODO – Nästa agent:**
- HTF‑repro 6h (dokument):
  - [ ] Avaktivera TP3/TP4 via konfig (0.0) och återskapa perioden 2025‑07‑01–2025‑10‑13 med warmup 50
  - [ ] FIX: `get_htf_fibonacci_context` använder nuvarande tid för `data_age_hours`; gör backtest‑säkert genom att mäta ålder relativt LTF‑bar (eller passera `asof_timestamp`) och lägg till enhetstest
  - [ ] Säkerställ 1D‑candles finns för perioden och att mapping 6h→1D används (inga `[DEBUG] HTF not available`)
  - [ ] Uppdatera `docs/6H_TIMEFRAME_OPTIMIZATION_RESULTS.md` med reproducerbara siffror + konfigsnapshot
- CLI‑overrides för backtest:
  - [ ] Lägg till flaggor i `scripts/run_backtest.py`: `--config-override <json>`, `--htf-partials a,b,c,d`, `--warmup`, `--start`, `--end`
  - [ ] Spara `configs`‑snapshot (hash + innehåll) i results JSON för reproducerbarhet
- Kalibrering & modeller:
  - [ ] Lägg till `calibration_by_regime` för 3h/6h, träna om med v18 och dokumentera resultat
  - [ ] Kör backtests 1h/3h/6h och uppdatera respektive docs (kort sammanfattning + diff mot föregående)
- Tester (kvalitet/stabilitet):
  - [ ] Enhetstester: HTF staleness‑gate, partial‑triggers (TP1/TP2/TP3/TP4), trail‑promotion, structure‑break
  - [ ] Integrationstest: End‑to‑end 6h backtest med HTF aktiv (verifiera att `position.exit_fib_levels` armeras)
- CI & pre‑commit:
  - [ ] Aktivera hooks lokalt: `pre-commit install` (svartlistade filer ignoreras redan i `.pre-commit-config.yaml`)
  - [ ] Verifiera GitHub Actions (ruff/black/pytest/bandit) kör på PR och push
  - [ ] Bandit lokalt (PowerShell): `bandit -r src scripts -f txt -o bandit-report.txt`
- Data & pipeline:
  - [ ] Säkerställ att `scripts/fetch_historical.py` täcker 1D för alla perioder som testas
  - [ ] Dokumentera standardflöde för v18 (IC, permutation, Partial‑IC) i `docs/FEATURE_COMPUTATION_MODES.md`
- Dokumentation:
  - [ ] Uppdatera denna fil med checklista och kommandon för exakt repro av 6h/1h/3h
  - [ ] Lägg in kort “Known pitfalls”: HTF‑staleness i backtest, skillnad mellan live vs backtest

## 🔒 Deployment Model

**Single-User Bot:**
- Genesis-Core är designad för en enskild utvecklare/trader
- Ingen multi-user support eller access control
- Full access till alla funktioner och konfigurationer
- API keys och secrets hanteras via `.env` (single instance)
- Production deployment: Personal VPS/cloud instance

#### Regler
- Följ Separation of concerns: `core/strategy/*` är rena, deterministiska funktioner.
- Inga hemligheter i loggar; använd `core.utils.logging_redaction` vid behov.
- Pausa vid osäkerhet, verifiera med tester innan du fortsätter.
- Skriv alltid enhetstester när du lägger till logik. Håll latens per modul < 20 ms.
- Använd `metrics` endast i orkestreringslager (`core/strategy/evaluate.py`), inte i pure‑moduler.

#### Setup (Windows PowerShell)
```powershell
python -m venv .venv
. .\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -e .[dev]          # Core + dev tools
pip install -e .[ml]           # ML dependencies (scikit-learn, pandas, pyarrow, matplotlib, seaborn, tqdm)
```

#### ML Pipeline (Phase-6 - Regime-Conditional Strategy)

**CURRENT WORKFLOW (v16 model, 18 månader data):**

```powershell
# 1. Data Collection (18+ months for robust validation)
python scripts/fetch_historical.py --symbol tBTCUSD --timeframe 1h --months 18

# 2. Feature Engineering (VECTORIZED - 27,734× faster!)
python scripts/precompute_features_fast.py --symbol tBTCUSD --timeframe 1h
# Features: rsi_inv_lag1, volatility_shift_ma3, bb_position_inv_ma3, 
#           rsi_vol_interaction, vol_regime

# 3. Model Training (with holdout + provenance)
python scripts/train_model.py --symbol tBTCUSD --timeframe 1h \
  --use-holdout --save-provenance

# 4. Regime Analysis (Find where edge exists)
python scripts/calculate_ic_by_regime.py \
  --model results/models/tBTCUSD_1h_v3.json \
  --symbol tBTCUSD --timeframe 1h

# 5. Feature Testing (by regime)
python scripts/test_features_by_regime.py \
  --symbol tBTCUSD --timeframe 1h --regime Bear

# 6. IC Metrics (validate predictive power)
python scripts/calculate_ic_metrics.py \
  --model results/models/tBTCUSD_1h_v3.json \
  --symbol tBTCUSD --timeframe 1h

# 7. Quintile Analysis (check Q5-Q1 spread)
python scripts/analyze_quintiles.py \
  --model results/models/tBTCUSD_1h_v3.json \
  --symbol tBTCUSD --timeframe 1h

# 8. Partial-IC (feature redundancy check)
python scripts/calculate_partial_ic.py \
  --symbol tBTCUSD --timeframe 1h --regime Bear --max-features 7

# 9. Vectorized Validation (ensure correctness)
python scripts/validate_vectorized_features.py \
  --symbol tBTCUSD --timeframe 1h --samples 200 --tolerance 0.01
```

**KEY FINDINGS (Phase-6):**
```
Best Regime: Bear Market
  IC:          +0.0784 (EXCELLENT)
  Spread:      +0.404% per 10 bars
  Annual ROI:  ~53% after fees (0.2%)
  Samples:     5,916 (45.6% of data)

Alternative: HighVol
  IC:          +0.0326 (GOOD)  
  Spread:      +0.158% per 10 bars
  Samples:     6,452 (49.8% of data)
```

**DEPRECATED (use Phase-6 workflow above):**
```
# Phase 3.5 scripts (triple-barrier labeling)
# python scripts/train_model.py --use-adaptive-triple-barrier
# python scripts/tune_triple_barrier.py
```

#### CI lokalt
```powershell
pwsh -File scripts/ci.ps1
```

#### Kör FastAPI lokalt
```powershell
uvicorn core.server:app --reload --app-dir src
```

#### URL:er
```
UI: http://127.0.0.1:8000/ui
Health: http://127.0.0.1:8000/health
```

#### Endpoints (REST)
- `/ui`, `/strategy/evaluate`, `/public/candles`, `/paper/submit`, `/paper/estimate`, `/paper/whitelist`
- `/auth/check`, `/debug/auth`, `/models/reload` (cache clear efter ML training)
- Konto (proxy mot Bitfinex v2 REST‑auth):
  - `/account/wallets`, `/account/positions`, `/account/orders`
- SSOT Config:
  - `GET /config/runtime`, `POST /config/runtime/validate`, `POST /config/runtime/propose`

#### Phase Status
- **Phase 1 & 2:** ✅ Complete (Core trading system, UI, SSOT, account endpoints)
- **Phase 3:** ✅ Complete (ML Pipeline: Data → Features → Training → Evaluation → Calibration → Champion Selection)
- **Quality Status:** ✅ All tests passing (140+ tests), CI clean, production ready

#### Strategy‑pipeline lokalt
Se exempel i `README.md` (GitHub‑läsare) eller kör tester:
```powershell
python -m pytest -q
```

#### Konfiguration (SSOT)
- Runtime: `config/runtime.json` är SSOT; seedas från `config/runtime.seed.json` om saknas. Filen är git‑ignorerad.
- API:
  - `GET /config/runtime` → `{ cfg, version, hash }`
  - `POST /config/runtime/validate` → `{ valid, errors, cfg? }`
  - `POST /config/runtime/propose` → kräver `Authorization: Bearer <token>` (env `BEARER_TOKEN`).
- UI:
  - Sätt bearer‑token i UI‑fältet (sparas i `localStorage.ui_bearer`).
  - “Föreslå ändring” POST:ar `/config/runtime/propose` och uppdaterar statuspanel (version/hash).
- Audit: ändringar loggas i `logs/config_audit.jsonl` (rotation ~5 MB) med `actor`, `paths`, `hash_before/after`.

#### Modellstruktur (per symbol)
- En fil per symbol, alla timeframes i samma JSON:
  - Ex: `config/models/tBTCUSD.json` innehåller nycklarna `1m`, `5m`, `15m`, `1h`, `4h`, `1D` med `{schema, buy, sell, calib}`.
  - `config/models/registry.json` mappar alla timeframes till samma fil (champion).
  - Registret och `ModelRegistry` stödjer även gamla “platta” filer (fallback): om rot har `{schema,buy,sell}` används den direkt; annars plockas vald timeframe, med fallback till `1m`.
- Lägga till symbol snabbt:
  1) Kopiera en befintlig JSON (t.ex. `tETHUSD.json`) till `tSYMBOLUSD.json`.
  2) Justera vikter under respektive timeframe vid behov.
  3) Lägg till `tSYMBOLUSD:{tf}` → filen i `registry.json` (alla timeframes pekar på samma fil).

#### UI‑säkerhet & dataflöde
- “Hämta publika candles” hämtar OHLCV och UI injicerar `symbol`/`timeframe` i Candles JSON.
- Validering: om `policy.symbol` ≠ `candles.symbol` visas röd varning under knappraden och “Kör pipeline” inaktiveras tills candles matchar.
- “Auto‑trösklar per symbol”: skriver minsta orderstorlek + 5% i `risk.risk_map` för vald symbol.
- “Låg tröskel (test)”: sätter `thresholds.entry_conf_overall = 0.20` (för snabb validering i test).

#### Orderstorlek & säkerhet
- Servern tvingar minsta orderstorlek per TEST‑symbol med 5% marginal (auto‑clamp).
- Valfritt wallet‑cap (env `WALLET_CAP_ENABLED=1`): begränsar LONG av USD‑saldo och SHORT av basvaluta i Exchange‑wallet.

#### SymbolMapper
- `SYMBOL_MODE=realistic|synthetic` (CI sätter `synthetic`).
- Strategi använder mänskliga symboler (`BTCUSD`); I/O mappar till Bitfinex (`tBTCUSD`) eller TEST (`tTESTBTC:TESTUSD`).
- TEST‑symboler bypassas (skickas oförändrade).

#### Filstruktur (kärna)
- `src/core/backtest` – BacktestEngine, PositionTracker, Metrics, TradeLogger
- `src/core/config` – config, schema, settings, validator
- `src/core/indicators` – EMA/RSI/ADX/ATR + vectorized.py (Phase-6)
- `src/core/io` – Bitfinex REST/WS-klienter
- `src/core/ml` – decision_matrix, overfit_detection, visualization (Phase-5)
- `src/core/observability` – metrics/dashboard
- `src/core/risk` – sizing/guards/pnl
- `src/core/strategy` – features/prob_model/decision/evaluate + features_asof.py (Phase-6)
- `src/core/symbols` – SymbolMapper
- `src/core/utils` – nonce/logging/backoff/crypto/data_loader/provenance (Phase-5/6)
- `config/models` – modellfiler per symbol (alla timeframes i samma fil)
- `config/` – validation_config.json, champion_weights.json (Phase-5)
- `data/` – candles (parquet), features (feather/parquet), metadata
- `results/` – models, ic_metrics, regime_analysis, feature_analysis, partial_ic (Phase-6)
- `scripts/` – fetch, precompute, train, analyze, validate (50+ scripts)
- `scripts/sync_precompute_and_train.py`: Kör precompute → curate → train → validate i en pipeline
  - Ex: `python scripts/sync_precompute_and_train.py --symbol tBTCUSD --timeframe 1h --feature-version v18`
- `docs/` – ADVANCED_VALIDATION_PRODUCTION.md, VALIDATION_CHECKLIST.md, INDICATORS_REFERENCE.md, FEATURE_COMPUTATION_MODES.md (Phase-5/6)

---

#### Phase Status (2025-10-10)
- ✅ **Phase 1 & 2:** Core system + Backtest framework COMPLETE
- ✅ **Phase 3.5:** ML Pipeline v10 COMPLETE
- ✅ **Phase-6:** Feature Engineering & Regime Discovery COMPLETE
- ✅ **Phase-6a:** CRITICAL BB BUG FIXED + Validation Complete
- ✅ **Exit Logic & Threshold Optimization:** Backtest infrastructure complete with fraktal-aware exits planned
  - **PROBLEM:** Bollinger Bands used sample std (ddof=1) in vectorized vs population std (ddof=0) in per-sample
  - **IMPACT:** 1.21% feature difference (bb_position_inv_ma3) → model trained on wrong data
  - **FIX:** Changed vectorized to ddof=0 (population std) to match per-sample
  - **VALIDATION:** Bit-exact parity achieved (3.44e-10 max diff, machine precision!)
  - **RECOMPUTED:** All features with correct BB (12,958 samples, tBTCUSD 1h)
  - **MODEL:** New v3 trained with correct features
  - **IC METRICS (with correct features):**
    - 5-bar: IC +0.0388 (GOOD, p<0.001, ICIR 0.54)
    - 10-bar: IC +0.0461 (GOOD, p<0.001, ICIR 0.50)
    - 20-bar: IC +0.0528 (EXCELLENT, p<0.001, ICIR 0.51)
  - **RESULT:** Features have STRONG signal with correct BB implementation!
- ✅ **Phase-6b:** SYSTEMATIC INDICATOR VALIDATION (Quality Gate)
  - **FRAMEWORK:** Created `scripts/validate_all_indicators.py` - automated validation tool
  - **TESTED:** All 4 core indicators (EMA, RSI, ATR, Volatility Shift)
  - **RESULTS:** ALL PASSED with machine precision!
    - EMA (20): 0.00e+00 (PERFECT, bit-exact!)
    - RSI (14): 3.55e-14 (machine precision)
    - ATR (14): 6.82e-13 (machine precision)
    - Volatility Shift: 2.66e-15 (machine precision)
  - **CONCLUSION:** BB bug was ISOLATED - no other systematic errors found
  - **FRAMEWORK:** Permanent quality gate, can be rerun anytime
- ✅ **Phase-6c:** REGIME-AWARE CALIBRATION (ML-Regime Synchronization)
  - **PROBLEM:** ML trained on mixed regimes → mis-calibrated probabilities per regime
    - Bear: Calibration error 0.0590 (WORST), under-confident by ~18%
    - Bull: IC +0.0124 (p=0.66, NOT significant) - no predictive power
  - **SOLUTION:** Regime-specific calibration (Platt scaling per regime)
    - Bear: a=4.1452 (strong boost) → P(buy) 0.53 → 0.63 (+18%!)
    - Bull: a=1.2429 (mild) → minimal boost
    - Ranging: a=1.9756 (moderate) → moderate boost
  - **IMPLEMENTATION:**
    - Created `regime_unified.py` - EMA-based regime detection (matches analysis)
    - Updated `evaluate_pipeline()` - detect regime BEFORE ML prediction
    - Updated `predict_proba_for()` - apply regime-specific calibration
    - Config: Regime-specific thresholds (bear: 0.30, bull: 0.90, ranging: 0.50)
  - **VALIDATION:** Tested with real data across all regimes
    - Bear: P(buy)=0.6312, Passes threshold 0.30 → TRADE EXECUTED ✅
    - Bull: P(buy)=0.5156, Fails threshold 0.90 → BLOCKED 🚫
    - Ranging: P(buy)=0.4793, Fails threshold 0.50 → BLOCKED 🚫
  - **RESULT:** System now trades ONLY when (ML signal) AND (regime edge) both align!

**Kvalitetsstatus:**
- ✅ All tests passing (141 passed, 2025-10-10)
- ✅ Vectorized features: BIT-EXACT parity (3.44e-10)
- ✅ CI/Pipeline green (black, ruff, bandit, pytest)
- ✅ Features validated with correct BB implementation
- ✅ IC metrics: EXCELLENT (+0.0528 @ 20-bar)

---

#### Latest Updates (2025-10-10) - Exit Logic & Threshold Optimization

**CRITICAL FIXES:**
- 🐛 **Bug #1 FIXED**: BacktestEngine size extraction (`result.get("size")` → `meta["decision"]["size"]`)
  - Impact: ALL backtests were broken (0 trades)
  - Status: ✅ FIXED & VALIDATED
  
- 🐛 **Bug #2 FIXED**: EV filter LONG-only bias (blocked ALL short trades)
  - Impact: Strategy could never profit from downtrends
  - Status: ✅ FIXED (now calculates ev_long AND ev_short, uses max)

**EXIT LOGIC IMPLEMENTATION:**
- ✅ **5 Exit Conditions**: SL (2%), TP (5%), TIME (20 bars), CONF_DROP (<0.45), REGIME_CHANGE
- ✅ **Config Schema**: New `ExitLogic` model in runtime config
- ✅ **Infrastructure**: `close_position_with_reason()`, exit tracking, reason logging
- ✅ **Documentation**: 1800+ lines across 6 docs

**THRESHOLD OPTIMIZATION:**
- ✅ **Raised threshold**: 0.55 → 0.65 (entry_conf_overall)
- ✅ **Result 30m**: -41.88% → -12.21% (70% improvement, 789 → 123 trades)
- 🎉 **Result 1h**: -8.42% → **+4.89% PROFITABLE!** (508 → 8 trades, 75% win rate)
- ❌ **Result 6h**: -43.21% unchanged (deeper model issues, not threshold-related)

**KEY DISCOVERIES:**
- 💡 **Overtrading was the problem**: 789 trades @ 0.3% cost = 237% capital lost to fees!
- 💡 **1h is sweet spot**: High quality + reasonable frequency = profitable edge
- 💡 **Fixed exits kill winners**: Need fraktal-aware, Fibonacci-driven exits (planned)
- 💡 **6h has separate issue**: High validation IC (+0.308) but backtest fails → investigate

**NEXT PHASE: Fibonacci Fraktal Exits**
- 📋 **Plan created**: `docs/FIBONACCI_FRAKTAL_EXITS_IMPLEMENTATION_PLAN.md` (1245 lines)
- 🎯 **Goal**: Replace fixed TP/SL with structure-aware exits respecting Fibonacci geometry
- 📈 **Expected**: 1h from +4.89% (8 trades) → +15-25% (20-30 trades)
- ⏳ **Status**: PLANNING PHASE (pre-requisites: HTF mapping, partial exits)

---

#### Current Runtime Config (2025-10-10)

```json
{
  "cfg": {
    "thresholds": {
      "entry_conf_overall": 0.65,  // Raised from 0.55 to reduce overtrading
      "regime_proba": {
        "balanced": 0.60,
        "ranging": 0.60,
        "bear": 0.60,
        "bull": 0.60,
        "highvol": 0.60
      }
    },
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
    "risk": {
      "risk_map": [[0.55, 0.02], [0.6, 0.03], [0.7, 0.04], [0.8, 0.05], [0.9, 0.06]]
    },
    "ev": {"R_default": 1.8},
    "gates": {"hysteresis_steps": 2, "cooldown_bars": 0}
  },
  "version": 61
}
```

#### Backtest Example
```powershell
# 1. Hämta historical data
python scripts/fetch_historical.py tBTCUSD 1h --months 18

# 2. Precompute features v17 (with Fibonacci)
python scripts/precompute_features_v17.py --symbol tBTCUSD --timeframe 1h

# 3. Kör backtest with exit logic
python scripts/run_backtest.py --symbol tBTCUSD --timeframe 1h --capital 10000

# 4. Resultat: +4.89% (8 trades, 75% win rate)
# Trades CSV: results/trades/tBTCUSD_1h_trades_YYYYMMDD_HHMMSS.csv
```

#### Models Cache Management
```powershell
# Efter ML training, rensa model cache:
curl -X POST http://127.0.0.1:8000/models/reload
```

---

## 🎯 **QUICK START FÖR NY AGENT (Hemma-dator)**

```powershell
# 1. Clone och checkout
git clone <repo-url>
cd Genesis-Core
git checkout phase-5

# 2. Setup environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .[dev,ml]

# 3. Verifiera installation
python -m pytest tests/ -q
python scripts/precompute_features_fast.py --symbol tBTCUSD --timeframe 1h

# 4. Läs key docs
# - docs/FEATURE_COMPUTATION_MODES.md (AS-OF semantik)
# - docs/VALIDATION_CHECKLIST.md (validation score 86/100)
# - docs/INDICATORS_REFERENCE.md (technical indicators guide)

# 5. Key files att förstå
# - src/core/strategy/features_asof.py (production features)
# - src/core/indicators/vectorized.py (fast batch computation)
# - scripts/calculate_ic_by_regime.py (regime discovery)
```

**IMPORTANT NOTES:**
- 🎯 **Use vectorized for testing/research** (27,734× faster)
- 🎯 **Use features_asof for production** (bit-exact, verified)
- 🎯 **1h timeframe is PROFITABLE** (+4.89%, 75% win rate @ threshold 0.65)
- 🎯 **Exit logic implemented** (SL/TP/TIME/CONF/REGIME aware)
- 🎯 **Data:** Curated datasets ligger i `data/curated/v1/candles/`; råfiler i `data/raw/bitfinex/`
- 🎯 **Current features:** v17 (14 features including Fibonacci combinations)
- 🎯 **Current model:** results/models/tBTCUSD_1h_v3.json (v16)
- 🎯 **Key docs:** 
  - `docs/EXIT_LOGIC_IMPLEMENTATION.md` (exit logic guide)
  - `docs/THRESHOLD_OPTIMIZATION_RESULTS.md` (optimization results)
  - `docs/FIBONACCI_FRAKTAL_EXITS_IMPLEMENTATION_PLAN.md` (next phase)
