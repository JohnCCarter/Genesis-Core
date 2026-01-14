# Feature/Indicator Audit (SSOT) – tBTCUSD 1h – audit_20260114_tBTCUSD_1h

> Read-only, evidence-based rapport enligt `docs/analysis/FEATURE_INDICATOR_AUDIT_RUNBOOK.md`.

## Kör-header

- Symbol/timeframe: `tBTCUSD_1h`
- Run-id: `audit_20260114_tBTCUSD_1h`
- Datumintervall (snapshot_id eller sample_start/end):
  - Evidens finns i `results/backtests/` (se urval nedan), t.ex.
    - 2024-01-01 → 2024-12-31: `results/backtests/tBTCUSD_1h_20260112_142153.json`
    - 2025-01-01 → 2025-12-11: `results/backtests/tBTCUSD_1h_20260112_084045.json`
- Canonical mode (förväntat):
  - `GENESIS_FAST_WINDOW=1`
  - `GENESIS_PRECOMPUTE_FEATURES=1`
  - `GENESIS_MODE_EXPLICIT=0`
- Hypotes: De 10 schema-features i `config/models/tBTCUSD_1h.json` produceras i SSOT (`features_asof.py`) och matas till modellen via `ModelRegistry` → `predict_proba_for` → `evaluate_pipeline`.

## Existerande körningar (evidens för datumintervall + mode)

Följande backtest-artefakter finns lokalt och innehåller `backtest_info.start_date/end_date` samt `execution_mode`:

- `results/backtests/tBTCUSD_1h_20260112_142153.json`
  - period: `2024-01-01 00:00:00+00:00` → `2024-12-31 00:00:00+00:00`
  - execution_mode: `fast_window=true`, `env_precompute_features="1"`, `mode_explicit="0"`
  - htf: `env_htf_exits="1"`, `use_new_exit_engine=true`, `htf_candles_loaded=true`
  - provenance:
    - `config_provenance.config_file`: `config\strategy\champions\tBTCUSD_1h.json`
    - `runtime_version_used`: `22` (i artefakten), `runtime_version_current`: `23`
- `results/backtests/tBTCUSD_1h_20260112_084045.json`
  - period: `2025-01-01 00:00:00` → `2025-12-11 00:00:00`
  - execution_mode: `fast_window=true`, `env_precompute_features="1"`, `mode_explicit="1"`
  - provenance:
    - `config_provenance.config_file`: `results\hparam_search\run_20260109_154651\trial_013_config.json`
    - `runtime_version_used`: `23` (i artefakten), `runtime_version_current`: `23`
- `results/backtests/tBTCUSD_1h_20260112_124656.json`
  - period: `2024-01-01 00:00:00+00:00` → `2024-02-15 00:00:00+00:00`
  - execution_mode: `fast_window=true`, `env_precompute_features="1"`, `mode_explicit="1"`

Not: det finns fler `tBTCUSD_1h_*.json` i `results/backtests/` (2026-01-12). Denna rapport använder dem endast som evidens för period/mode, inte som prestationsutvärdering.

Praktisk tolkning:

- Om du vill låsa audit-rapporten mot **champion** som användes i en helårsrun: använd `tBTCUSD_1h_20260112_142153.json` (pekar direkt på `config/strategy/champions/tBTCUSD_1h.json`).
- Om du vill låsa audit-rapporten mot en **Optuna-trial**: använd `tBTCUSD_1h_20260112_084045.json` (pekar på en specifik `trial_013_config.json`).

### Rekommendation: dubbel-baseline (båda) ✅

Ja – det är oftast bättre att köra på **båda** baselines, men med **olika roll** (så vi slipper blanda äpplen och päron):

- **Baseline A (primär, “champion-baseline”)**

  - Artefakt: `results/backtests/tBTCUSD_1h_20260112_142153.json`
  - Syfte: Förankra auditen i “vad som faktiskt körs” när champion-configen används.
  - Vad vi använder den till: SSOT→indikator→schema→pipeline-kedjan, canonical mode, samt att `config_provenance.config_file` pekar på championfilen.

- **Baseline B (sekundär, “Optuna-trial-baseline”)**
  - Artefakt: `results/backtests/tBTCUSD_1h_20260112_084045.json`
  - Syfte: Visa att samma kedja håller även när config kommer från en specifik Optuna-trial.
  - Vad vi använder den till: beviskedjan “trial_config → effective config (merged_config) → backtest-resultat”, och att `skip_champion_merge` inte smyger in beroenden.

Praktisk payoff:

- Om båda baselines visar samma feature-producering (SSOT) och samma mode-guardrails → högre förtroende att auditen inte är “överanpassad” till en enda konfigkälla.
- Om de skiljer sig → vi har en tydlig felsökningsingång: _är skillnaden config (thresholds, signal_adaptation, fib-gates) eller mode/provenance (mode_explicit, precompute readiness, champion-merge)?_

### Baseline provenance (A/B) – copy/paste-bevis

Nedan är de fält vi explicit använder som “bevisankare” för att kunna reproducera samma konfig/mode i efterhand.

- **Baseline A (champion, primär)**

  - artefakt: `results/backtests/tBTCUSD_1h_20260112_142153.json`
  - period: `2024-01-01 00:00:00+00:00` → `2024-12-31 00:00:00+00:00`
  - build: `git_hash=41fc7fe55d20773b9435ce13908453154e9df4c2`, `seed=42`, `timestamp=2026-01-12T14:21:53.301230`
  - execution_mode: `fast_window=true`, `env_precompute_features="1"`, `mode_explicit="0"`, `precomputed_ready=true`
  - provenance:
    - `config_provenance.config_file`: `config\strategy\champions\tBTCUSD_1h.json`
    - `runtime_version_used=22`, `runtime_version_current=23`
    - `merged_config` finns i artefakten (full effective config)

- **Baseline B (Optuna-trial, sekundär)**
  - artefakt: `results/backtests/tBTCUSD_1h_20260112_084045.json`
  - period: `2025-01-01 00:00:00` → `2025-12-11 00:00:00`
  - build: `git_hash=41fc7fe55d20773b9435ce13908453154e9df4c2`, `seed=42`, `timestamp=2026-01-12T08:40:45.155557`
  - execution_mode: `fast_window=true`, `env_precompute_features="1"`, `mode_explicit="1"`, `precomputed_ready=true`
  - provenance:
    - `config_provenance.config_file`: `results\hparam_search\run_20260109_154651\trial_013_config.json`
    - `runtime_version_used=23`, `runtime_version_current=23`
    - `merged_config` finns i artefakten (full effective config)

Not: För att undvika manuell scroll i stora JSON:er kan du använda `scripts/extract_backtest_provenance.py` för att extrahera dessa rader.

## Källor (primära bevis)

- Modell + schema:
  - `config/models/registry.json` (mapping `tBTCUSD:1h` → champion)
    - Bevis: `"tBTCUSD:1h": {"champion": "config/models/tBTCUSD_1h.json"}`
  - `config/models/tBTCUSD_1h.json` (schema-lista)
- SSOT feature extraction:
  - `src/core/strategy/features_asof.py` (`_extract_asof(...)` är dokumenterad som SSOT)
- Orkestrering:
  - `src/core/strategy/evaluate.py` (`evaluate_pipeline(...)`)
- Canonical env-policy:
  - `src/core/pipeline.py` (`GenesisPipeline.setup_environment`)
- Backtest/precompute injection:
  - `src/core/backtest/engine.py` (`BacktestEngine.load_data`, `BacktestEngine.run`)
- Optuna/runner determinism & guardrails:
  - `src/core/optimizer/runner.py`
- Scoring versioning:
  - `src/core/optimizer/scoring.py`

## Canonical mode (bevis)

`GenesisPipeline.setup_environment(...)` tvingar canonical 1/1-mode om `GENESIS_MODE_EXPLICIT != 1`:

- Bevis: `src/core/pipeline.py` sätter
  - `os.environ["GENESIS_FAST_WINDOW"] = "1"`
  - `os.environ["GENESIS_PRECOMPUTE_FEATURES"] = "1"`

## Modell: schema för tBTCUSD_1h (bevis)

Modellfilen `config/models/tBTCUSD_1h.json` definierar exakt 10 feature keys som modellen konsumerar:

1. `rsi_inv_lag1`
2. `volatility_shift_ma3`
3. `bb_position_inv_ma3`
4. `rsi_vol_interaction`
5. `vol_regime`
6. `fib05_prox_atr`
7. `fib_prox_score`
8. `fib05_x_ema_slope`
9. `fib_prox_x_adx`
10. `fib05_x_rsi_inv`

Bevis: `config/models/tBTCUSD_1h.json` fältet `schema`.

Regression guard (test): `tests/test_feature_schema_contract_tBTCUSD_1h.py` verifierar att SSOT producerar alla schema-keys med finita värden.

## SSOT: Feature computation (bevis)

### SSOT-definition

`src/core/strategy/features_asof.py::_extract_asof(...)`:

- Dokumenterat: “**This is the SINGLE SOURCE OF TRUTH for feature calculation.**”
- Invariants:
  - använder bars `[0:asof_bar]` (inklusive)
  - **ingen lookahead** (använder aldrig bars `> asof_bar`)

Bevis: docstring i `_extract_asof(...)`.

### Inputs (OHLCV + ev timestamp)

`_extract_asof(...)` kräver att följande listor har samma längd:

- `open`, `high`, `low`, `close`, `volume`

Bevis: inputvalidering i `_extract_asof(...)`.

För HTF/LTF-context försöker den även läsa `timestamp` (om finns i candles-dict) vid skapande av fib-context.

Bevis: `_candles_for_htf` och pass-through av `candles.get("timestamp")` i `features_asof.py`.

## Schema-features → producer/indikatorer (SSOT-tabell)

Alla schema-features för `tBTCUSD_1h` produceras i `src/core/strategy/features_asof.py::_extract_asof(...)`.

| feature_key            | producer (SSOT)                   | upstream indikatorer                         | inputs                      | notes                                                                                                                                              |
| ---------------------- | --------------------------------- | -------------------------------------------- | --------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| `rsi_inv_lag1`         | `features_asof.py::_extract_asof` | RSI(14)                                      | close                       | Beräknas som `(rsi_lag1_raw - 50) / 50`. RSI läses helst från `precomputed_features["rsi_14"]`, annars `calculate_rsi(...)`.                       |
| `volatility_shift_ma3` | `features_asof.py::_extract_asof` | ATR(atr_period) + ATR(50) → volatility_shift | high/low/close              | `vol_shift_ma3` = 3-bar MA av volatility_shift. volatility_shift beräknas via `calculate_volatility_shift(atr_vals, atr_long)` om ej precompute.   |
| `bb_position_inv_ma3`  | `features_asof.py::_extract_asof` | Bollinger(20, 2)                             | close                       | `bb_position_inv_ma3` = MA3 av `1 - bb_position` (bb_position kommer från `bollinger_bands(...)["position"]` eller precompute `bb_position_20_2`). |
| `rsi_vol_interaction`  | `features_asof.py::_extract_asof` | RSI(14) + volatility_shift                   | close (+ ATR via vol shift) | `rsi_current` = (RSI-50)/50. Interaktion = `rsi_current * clip(vol_shift_current, 0.5, 2.0)`.                                                      |
| `vol_regime`           | `features_asof.py::_extract_asof` | volatility_shift                             | close (+ ATR via vol shift) | Binär: `1.0 if vol_shift_current > 1.0 else 0.0`.                                                                                                  |
| `fib05_prox_atr`       | `features_asof.py::_extract_asof` | Fibonacci swings/levels/features + ATR       | high/low/close              | Från `calculate_fibonacci_features(...)` (`fib_feats`). Klampas till [0,1].                                                                        |
| `fib_prox_score`       | `features_asof.py::_extract_asof` | Fibonacci swings/levels/features + ATR       | high/low/close              | Från `fib_feats["fib_prox_score"]`. Klampas till [0,1].                                                                                            |
| `fib05_x_ema_slope`    | `features_asof.py::_extract_asof` | fib05_prox_atr + EMA-slope                   | close (+ fib feats)         | `fib05_x_ema_slope = fib05_prox_atr * ema_slope`. EMA-slope använder EMA(period=20, lookback=5) för `1h` (timeframe-parametrar i filen).           |
| `fib_prox_x_adx`       | `features_asof.py::_extract_asof` | fib_prox_score + ADX(14)                     | high/low/close              | `adx_latest/100` normaliseras. `fib_prox_x_adx = fib_prox_score * adx_normalized`.                                                                 |
| `fib05_x_rsi_inv`      | `features_asof.py::_extract_asof` | fib05_prox_atr + RSI(14)                     | close (+ fib feats)         | `fib05_x_rsi_inv = fib05_prox_atr * (-rsi_current)` där `rsi_current=(RSI-50)/50`.                                                                 |

Bevis för indikator-implementationer (import/usage):

- `features_asof.py` importerar:
  - `calculate_rsi` (`src/core/indicators/rsi.py`)
  - `calculate_atr` (`src/core/indicators/atr.py`)
  - `calculate_adx` (`src/core/indicators/adx.py`)
  - `calculate_ema` (`src/core/indicators/ema.py`)
  - `bollinger_bands` (`src/core/indicators/bollinger.py`)
  - `calculate_volatility_shift` (`src/core/indicators/derived_features.py`)
  - `detect_swing_points` / `calculate_fibonacci_levels` / `calculate_fibonacci_features` (`src/core/indicators/fibonacci.py`)

## Features som produceras men inte ingår i modellens schema (tBTCUSD_1h)

SSOT producerar fler keys än de 10 som modellen konsumerar, t.ex.:

- `atr_14` (alltid satt i `features` dict)
- `fib_dist_min_atr`, `fib_dist_signed_atr`, `fib0618_prox_atr`, `swing_retrace_depth`

Bevis: `features_asof.py` bygger `features = {..., "atr_14": ...}` och `features.update({... fib_* ...})`.

Dessa är **inte nödvändigtvis “dead compute”**. Exempel: `evaluate_pipeline` använder `atr_14` (fallback) när den tar fram market-quality inputs (`atr_pct`).

- Bevis: `src/core/strategy/evaluate.py` försöker läsa `feats_meta.get("current_atr_used")`, annars `feats.get("atr_14")`.

För övriga fib-keys (t.ex. `fib0618_prox_atr`) har vi gjort en text-sökning i `src/**` och **inte hittat någon downstream-konsument** utanför feature-producering (SSOT) och indikatorn själv:

- Produceras i: `src/core/strategy/features_asof.py` och `src/core/strategy/features.py`
- Beräknas i: `src/core/indicators/fibonacci.py`
- Ingen verifierad usage hittad i: decision/exit/evaluate-pipeline (utöver att de ligger i `features`-dict)

Tolkning: dessa keys är för närvarande antingen (a) framtida/experimentella, (b) används endast för debugging/telemetri via artifacts, eller (c) en kandidat för städning om vi vill minimera compute.

## Indikator-inventory (implementation → usage)

| indikator                              | implementation                            | används av (verifierat)                                                              | notes                                                                                                               |
| -------------------------------------- | ----------------------------------------- | ------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------- |
| RSI                                    | `src/core/indicators/rsi.py`              | `rsi_inv_lag1`, `rsi_vol_interaction`, `fib05_x_rsi_inv`                             | SSOT läser helst `precomputed_features["rsi_14"]`.                                                                  |
| ATR                                    | `src/core/indicators/atr.py`              | volatility_shift, fib-features, `atr_14`                                             | SSOT kan använda `thresholds.signal_adaptation.atr_period` men säkrar även “true ATR(14)” för `features["atr_14"]`. |
| Bollinger Bands                        | `src/core/indicators/bollinger.py`        | `bb_position_inv_ma3`                                                                | SSOT läser `position` och inverterar.                                                                               |
| EMA                                    | `src/core/indicators/ema.py`              | `fib05_x_ema_slope` (via EMA-slope) + regime detection i `evaluate_pipeline` (EMA50) | `evaluate_pipeline` använder precompute `ema_50` om den finns (fast-path).                                          |
| ADX                                    | `src/core/indicators/adx.py`              | `fib_prox_x_adx`                                                                     | Normaliseras till [0,1] via `/100`.                                                                                 |
| Volatility shift                       | `src/core/indicators/derived_features.py` | `volatility_shift_ma3`, `rsi_vol_interaction`, `vol_regime`                          | Beräknas från ATR kort + lång (50) om ej precompute.                                                                |
| Fibonacci (LTF swings/levels/features) | `src/core/indicators/fibonacci.py`        | `fib05_prox_atr`, `fib_prox_score`, samt fib-dist/retrace keys                       | SSOT använder antingen precomputed swings (`fib_high_idx/low_idx/...`) eller `detect_swing_points(...)`.            |
| HTF/LTF fib-context                    | `src/core/indicators/htf_fibonacci.py`    | decision/exits via `feats_meta` (context)                                            | SSOT försöker skapa `htf_fibonacci_context` och `ltf_fibonacci_context` för vissa timeframes (inkl `1h`).           |

## Precompute + indexering: hur SSOT får rätt “as-of” (bevis)

### BacktestEngine: mode consistency

`BacktestEngine._validate_mode_consistency()` kräver:

- om `fast_window=True` → `GENESIS_PRECOMPUTE_FEATURES=1` (annars `ValueError`)

Bevis: `src/core/backtest/engine.py`.

### BacktestEngine.load_data: producerar precomputed_features

Om `GENESIS_PRECOMPUTE_FEATURES=1` sätts `engine.precompute_features=True` och engine försöker fylla `self._precomputed_features`.

- Precompute inkluderar bl.a. `atr_14`, `atr_50`, `ema_20`, `ema_50`, `rsi_14`, `bb_position_20_2`, `adx_14` samt fib-swing arrays.

Bevis: `src/core/backtest/engine.py` i `load_data()`.

### BacktestEngine.run: injicerar precomputed_features och \_global_index

- Före loop: injicerar `configs["precomputed_features"] = dict(self._precomputed_features)` om precompute finns.
- I huvudloopen: sätter `configs["_global_index"] = i` för varje bar.

Bevis: `src/core/backtest/engine.py`.

### SSOT: använder \_global_index + remap för fönster som startar mitt i historiken

`_extract_asof(...)` i `features_asof.py`:

- väljer `lookup_idx = config.get("_global_index", asof_bar)`
- remappar `precomputed_features` via `_remap_precomputed_features(pre, window_start_idx, lookup_idx)`

Bevis: `src/core/strategy/features_asof.py`.

### Viktig fallback (risk för jämförbarhet)

Om `GENESIS_PRECOMPUTE_FEATURES=1` men `precomputed_features` är tomt/saknas:

- SSOT loggar en engångsvarning och sätter `use_precompute=False` (dvs faller till slow path).

Bevis: `src/core/strategy/features_asof.py`.

## Optuna / runner: hur canonical mode görs reproducerbar (bevis)

I `src/core/optimizer/runner.py`:

- cache-nyckel inkluderar execution mode (`fw...pc...htf...`) för att undvika mixed-mode engine reuse.
- hard-guard: om `GENESIS_PRECOMPUTE_FEATURES=="1"` och `engine._precomputed_features` saknas → trial returnerar error (fail fast) istället för att riskera slow-path.
- runner tvingar `meta["skip_champion_merge"] = True` i `effective_cfg_for_run` innan `engine.run(...)`.

Bevis: `src/core/optimizer/runner.py`.

## Champion merge / determinism: vem mergar vad? (bevis + risk)

### evaluate_pipeline

`evaluate_pipeline(...)` i `src/core/strategy/evaluate.py`:

- Om `_global_index` finns i `configs` → `force_backtest_mode=True` och **ingen champion-merge görs här**.

Bevis: `force_backtest_mode = "_global_index" in configs` + kommentar om icke-reproducerbarhet.

### BacktestEngine.run

`BacktestEngine.run(...)` i `src/core/backtest/engine.py`:

- mergar champion config **om inte** `configs.meta.skip_champion_merge` är satt.

Bevis: `skip_champion_merge = bool(meta.get("skip_champion_merge"))` + `if not skip_champion_merge: ... configs = self._deep_merge(champion_cfg.config, configs)`.

### Tolkningspunkt (risk/observation)

- I optimeringsflödet mitigieras detta av runner (sätter `skip_champion_merge=True`).
- I manuella backtests (om man anropar engine/run utan att sätta meta-flaggan) kan man fortfarande få resultat som beror på “nuvarande” championfil.

Status: **Risk identifierad** (se rekommendationer).

## Scorer-versioning (bevis)

`src/core/optimizer/scoring.py::_resolve_score_version(...)`:

- väljer scoring-version från `GENESIS_SCORE_VERSION` (default `v1`).

Bevis: `raw = (score_version or os.environ.get("GENESIS_SCORE_VERSION") or "v1")...`.

## Kedja (diagram)

Raw candles (OHLCV, ev timestamp)
→ indikatorer (RSI/ATR/BB/EMA/ADX/Fib)
→ features (SSOT: `features_asof._extract_asof`, strict AS-OF)
→ modell/schema (`config/models/tBTCUSD_1h.json` via `ModelRegistry`)
→ probas (`predict_proba_for`)
→ confidence + market quality (`compute_confidence`, bl.a. ATR%)
→ decision (`decide`, använder `feats` + `feats_meta` inkl HTF/LTF fib-context)
→ backtest loop (`BacktestEngine.run`)
→ metrics/score (`calculate_metrics` → `score_backtest`)

## Downstream consumers: var features faktiskt används (bevis)

### 1) Schema-features → modellinput (direkt konsumtion)

De **10 schema-features** konsumeras av sannolikhetsmodellen – inte direkt av beslutsgates.

- `src/core/strategy/prob_model.py::predict_proba(...)`
  - bygger input-vektorn som:
    - `x = [float(features.get(k, 0.0)) for k in keys]`
  - där `keys` kommer från `schema` i `ModelRegistry`.
- `src/core/strategy/prob_model.py::predict_proba_for(...)`
  - hämtar `meta` (inkl `schema`, vikter och kalibrering) från `ModelRegistry` och anropar `predict_proba(...)`.

Praktisk tolkning:

- Om en schema-key saknas i `features` blir den **0.0** i modellen (dvs “tyst fallback”). Contract-testet låser därför att keys finns (se nedan).

### 2) Market-quality (ATR%) använder `atr_14` som fallback

- `src/core/strategy/evaluate.py::evaluate_pipeline(...)`
  - tar `current_atr` primärt från `feats_meta.get("current_atr_used")`
  - fallback: `feats.get("atr_14")`
  - beräknar sedan `atr_pct = current_atr / last_close` och skickar det till `compute_confidence(...)`.

### 3) Decision: konsumerar probas + confidence + meta-state (inte schema-features direkt)

- `src/core/strategy/evaluate.py::evaluate_pipeline(...)`

  - bygger `state` med:
    - `current_atr` och `atr_percentiles` (från `feats_meta`)
    - `htf_fib` och `ltf_fib` (från `feats_meta["htf_fibonacci"/"ltf_fibonacci"]`)
    - `last_close`
  - anropar `src/core/strategy/decision.py::decide(...)` med `probas`, `confidence`, `regime`, `state` och `cfg`.

- `src/core/strategy/decision.py::decide(...)`
  - använder `thresholds.signal_adaptation` + `state["atr_percentiles"]` för att välja ATR-zon och därmed tröskel.
  - använder `state["htf_fib"]` och `state["ltf_fib"]` för fib-gating (HTF-block, LTF-block) och optional LTF-override.
  - noterbart: funktionen tar **inte** emot `features`-dict och kan därför inte konsumera schema-features direkt; schema-features påverkar beslutet endast via `probas` (modelloutput).

### 4) Exits: konsumerar HTF fib-levels + ATR (prefix) i backtest

- `src/core/backtest/engine.py::BacktestEngine._check_htf_exit_conditions(...)`
  - hämtar `htf_fib_context` från:
    - precompute (`self._precomputed_features["htf_fib_0382"/"htf_fib_05"/"htf_fib_0618"]`) om möjligt, annars
    - `meta["features"]["htf_fibonacci"]` från pipeline.
  - beräknar `current_atr` som ATR(14) på **prefix** upp till `bar_index` (no-lookahead) och skickar till exit engine.
  - vid `GENESIS_HTF_EXITS=1` används strategy-level HTF-exit engine:
    - `src/core/strategy/htf_exit_engine.py::HTFFibonacciExitEngine.check_exits(...)`.

Not: strategy-level exit engine läser HTF-levels via nycklarna `htf_fib_0382`, `htf_fib_05`, `htf_fib_0618`.

## Overlap / risk (med bevis)

### R1: Implicit slow-path när precompute saknas (jämförbarhet)

- Evidence: `features_asof.py` sätter `use_precompute=False` om env var är satt men `precomputed_features` saknas.
- Impact:
  - Om detta inträffar i en körning där du trodde du körde canonical precompute-path kan trials/backtests bli icke-jämförbara (prestanda och potentiellt semantik om andra delar också faller tillbaka).
  - Optuna-runnern mitigierar via fail-fast guard, men manuella körningar kan missa det.

### R2: `GENESIS_FAST_HASH` kan ge cache-kollisioner (correctness)

- Evidence: `_compute_candles_hash(...)` använder opt-in nyckel `f"{asof_bar}:{last_close:.4f}"` när `GENESIS_FAST_HASH` är satt.
- Impact:
  - Två olika fönster kan dela `asof_bar` och samma `last_close` → fel cache-hit → fel features.
  - Rekommenderas att hålla av i alla quality-/Optuna-/champion-körningar.

### R3: Dubbel “champion merge”-yta (stability / reproducibility)

- Evidence:
  - `evaluate_pipeline` har en guard för backtest (`_global_index` → ingen merge).
  - `BacktestEngine.run` gör ändå en champion-merge om `meta.skip_champion_merge` inte är satt.
- Impact:
  - Risk för förvirring om någon förväntar sig att `_global_index` ensamt räcker för att eliminera champion-beroende.
  - Runner mitigierar; men det är en footgun för ad-hoc körningar.

### R4: Delvis precompute (performance / drift-risk låg)

- Evidence:
  - Engine precomputar inte `volatility_shift` eller `ema_slope`.
  - SSOT beräknar dessa via slow-path (men med indicator-cache).
- Impact:
  - Främst performance; correctness-risk bedöms låg eftersom samma indikatorfunktioner används (men detta är en tolkning; verifiera gärna med ett parity-test om du vill hård-garantera).

### R5: HTF-exit adapter: nivå-keys mismatch (correctness)

- Evidence:
  - strategy-level HTF-exit engine (`src/core/strategy/htf_exit_engine.py`) läser `htf_fib_0382`/`htf_fib_05`/`htf_fib_0618`.
  - backtest-context kan hålla fib-levels keyed som floats `0.382/0.5/0.618`.
- Impact:
  - Om adaptern inte normaliserar kan exit-motorn tyst falla tillbaka till `"Invalid HTF Data"` → `HOLD`.

Status: **Åtgärdad i kod** (backtest-adaptern normaliserar nu nivånycklar innan `check_exits`).

## Rekommendationer (utan kod) – prioriterade

### 1) Correctness / determinism

1. För alla manuella backtests som ska jämföras med Optuna: sätt explicit `meta.skip_champion_merge=true` i config (eller använd samma runner-path) så att championfil inte påverkar.
2. Dokumentera/standardisera att `GENESIS_FAST_HASH` ska vara av i canonical runs (quality decisions).

### 2) Testability / traceability

3. ✅ Implementerat: schema-contract-test som laddar `config/models/tBTCUSD_1h.json` och assertar att alla schema keys finns i SSOT-output med finita värden.

- Bevis: `tests/test_feature_schema_contract_tBTCUSD_1h.py`.

4. Lägg till (förslag): test/guard som failar om `GENESIS_PRECOMPUTE_FEATURES=1` men `precomputed_features` saknas (för icke-runner-körningar), alternativt kräver en tydlig logg/flagga i resultatet.

### 3) Performance (endast om safe)

5. Om profiling visar att volatility_shift eller ema_slope dominerar: överväg att inkludera dem i engine precompute (men först efter parity-test + tydliga tests för “as-of” correctness).
