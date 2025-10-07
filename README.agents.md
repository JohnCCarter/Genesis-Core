### README för AI‑agenter (lokal utveckling)

Denna fil beskriver hur AI‑agenter ska arbeta lokalt med projektet.

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

#### ML Pipeline (Phase 3 Complete)
```powershell
# Data collection
python scripts/fetch_historical.py --symbol tBTCUSD --timeframe 15m --months 3

# Feature engineering
python scripts/precompute_features.py --symbol tBTCUSD --timeframe 15m

# Model training
python scripts/train_model.py --symbol tBTCUSD --timeframe 15m

# Model evaluation
python scripts/evaluate_model.py --model results/models/tBTCUSD_15m_v2.json

# Model calibration
python scripts/calibrate_model.py --model results/models/tBTCUSD_15m_v2.json

# Champion selection
python scripts/select_champion.py --symbol tBTCUSD --timeframe 15m --ml-model results/models/tBTCUSD_15m_v2.json
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
- `src/core/backtest` – BacktestEngine, PositionTracker, Metrics, TradeLogger (Phase 2 ✅)
- `src/core/config` – config, schema, settings, validator
- `src/core/indicators` – EMA/RSI/ADX/ATR
- `src/core/io` – Bitfinex REST/WS-klienter
- `src/core/observability` – metrics/dashboard
- `src/core/risk` – sizing/guards/pnl
- `src/core/strategy` – features/prob_model/decision/evaluate
- `src/core/symbols` – SymbolMapper
- `src/core/utils` – nonce/logging/backoff/crypto (HMAC signature)
- `config/models` – modellfiler per symbol (alla timeframes i samma fil)
- `data/` – historical candles (parquet), features, metadata (Phase 3)
- `results/` – backtest outputs (JSON, CSV, plots)
- `scripts/` – verktyg/CI/fetch_historical/validate_data/run_backtest

---

#### Phase Status (2025-10-07)
- ✅ **Phase 1 & 2:** Core system + Backtest framework KLART
- ⏳ **Phase 3:** ML Training Pipeline (se `TODO_PHASE3.md`)

**Kvalitetsstatus:**
- ✅ 115/115 tester passar
- ✅ 0 linting errors (ruff)
- ✅ 0 formatting issues (black)
- ✅ 0 critical security warnings (bandit)

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
