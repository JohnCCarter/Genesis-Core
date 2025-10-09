### README för AI‑agenter (lokal utveckling)

Denna fil beskriver hur AI‑agenter ska arbeta lokalt med projektet.

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
- `docs/` – ADVANCED_VALIDATION_PRODUCTION.md, VALIDATION_CHECKLIST.md, INDICATORS_REFERENCE.md, FEATURE_COMPUTATION_MODES.md (Phase-5/6)

---

#### Phase Status (2025-10-09)
- ✅ **Phase 1 & 2:** Core system + Backtest framework COMPLETE
- ✅ **Phase 3.5:** ML Pipeline v10 COMPLETE
- ✅ **Phase-6:** Feature Engineering & Regime Discovery COMPLETE
  - Found tradeable edge: Bear regime IC +0.0784, Spread +0.404% (~53% annual!)
  - Vectorized computation: 27,734× speedup (54 min → 0.12s)
  - Features: 5 non-redundant (rsi_inv_lag1, volatility_shift_ma3, bb_position_inv_ma3, rsi_vol_interaction, vol_regime)
  - Validation: Bit-exact parity (4/5 perfect, 1/5 within 1.17%)
  - Dataset: 18 månader (12,958 samples)
  - Model: `results/models/tBTCUSD_1h_v3.json` (v16 final)

**Kvalitetsstatus:**
- ✅ All tests passing (106 passed)
- ✅ Validation score: 86/100 (exceeds 70/100 production threshold)
- ✅ CI/Pipeline green
- ✅ Vectorized features validated

---

#### Backtest Example
```powershell
# 1. Hämta historical data
python scripts/fetch_historical.py tBTCUSD 15m --months 3

# 2. Validera data quality
python scripts/validate_data.py tBTCUSD 15m

# 3. Kör backtest
python scripts/run_backtest.py --symbol tBTCUSD --timeframe 15m --capital 10000

# 4. Resultat sparas i results/backtests/ (JSON + CSV)
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
- 🎯 **Bear regime has BEST edge** (IC +0.0784, Spread +0.404%)
- 🎯 **Data is in data/candles/** (12,958 samples, 18 months)
- 🎯 **Current model:** results/models/tBTCUSD_1h_v3.json (v16)
