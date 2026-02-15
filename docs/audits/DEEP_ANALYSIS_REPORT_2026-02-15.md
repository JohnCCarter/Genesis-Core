# Deep Analysis Report — Genesis-Core (2026-02-15, rev 2)

Samlad rapport fran tre parallella agentanalyser, reviderad efter manuell
verifiering. Utformad som stod for Opus 4.6 och Codex 5.3 i fortsatt
repo-cleanup (D39+).

**Analyserade av:**

- `feature-dev:code-explorer` — Djupanalys av oanvand/foraldrad kod och filer
- `feature-dev:code-reviewer` — Kodkvalitet, buggar, sakerhet
- `pr-review-toolkit:silent-failure-hunter` — Tysta fel

**Referenskontext:** D1-D38 genomforda (se AGENTS.md §7).

**Revideringslogg:**

- Rev 1 (2026-02-15): Ursprunglig rapport fran tre agenter.
- Rev 2 (2026-02-15): Manuell verifiering — 3 findings nedgraderade till
  FALSK_POSITIV, 2 findings markerade STALE, severity justerade, statuskolumn
  tillagd, git-index-bevis tillagt, kategorisering av dead code forfinad,
  Fas E (git hygien) borttagen (alla pastaenden verifierade som felaktiga).

---

## Statusdefinitioner

| Status        | Betydelse                                                            |
| ------------- | -------------------------------------------------------------------- |
| VERIFIERAD    | Manuellt bekraftad i aktuell kodbas                                  |
| DELVIS        | Korrekt observation men overdrivet/felangivet i severity/beskrivning |
| FALSK_POSITIV | Pastaende stammer inte vid verifiering                               |
| STALE         | Var sant men ar atgardat (D37/D38 eller tidigare)                    |

---

## Del 1: Kodkvalitet och buggar (code-reviewer)

### VERIFIERADE

#### CR-1. Cache double-insert i features_asof.py — VERIFIERAD

- **Fil:** `src/core/strategy/features_asof.py:880-892`
- **Status:** VERIFIERAD
- **Severity:** LOW (redundant kod, inte korruption)
- **Problem:** `_feature_cache[cache_key] = result` skrivs tva ganger i rad
  (rad 880 + 884). `OrderedDict` overskriver samma nyckel, sa det ar
  funktionellt harmlost men indikerar copy-paste-skuld.
- **Fix:** Ta bort duplicerat assignment (rad 884).

#### CR-4. Backtest mode-validering tillater tyst inkonsistens — VERIFIERAD

- **Fil:** `src/core/backtest/engine.py:189-206`
- **Status:** VERIFIERAD
- **Severity:** MEDIUM
- **Problem:** `fast_window=False` + `GENESIS_PRECOMPUTE_FEATURES=1` loggar
  bara varning — borde vara hard error nar `GENESIS_MODE_EXPLICIT != "1"`.
- **Konfidens:** 88

#### CR-6. Precompute cache-key saknar config-hash — VERIFIERAD

- **Fil:** `src/core/backtest/engine.py:607-626`
- **Status:** VERIFIERAD
- **Severity:** HIGH — bryter reproducibilitet
- **Problem:** Cache-nyckel bygger pa `symbol, timeframe, len(df), start_ns,
end_ns` men INTE config-hash. Tva backtests med olika `atr_period` kan
  ateranvanda samma cache.
- **Konfidens:** 92

#### CR-7. Volume score kan returnera >1.0 — VERIFIERAD

- **Fil:** `src/core/strategy/evaluate.py:36-95`
- **Status:** VERIFIERAD
- **Severity:** LOW
- **Problem:** Dokumentation sager `[0,1]` men `cap_ratio` default 3.0 tillater >1.
- **Konfidens:** 85

#### CR-8. decision.py — shallow copy av mutable nested state — VERIFIERAD

- **Fil:** `src/core/strategy/decision.py:163-174`
- **Status:** VERIFIERAD
- **Severity:** LOW (defensiv forbattring)
- **Problem:** `override_state` kopierar listor men inte dicts/nested objects.
- **Konfidens:** 80

### NEDGRADERADE / FALSK_POSITIV

#### CR-2. "Mutable default" i FibonacciConfig — FALSK_POSITIV

- **Fil:** `src/core/indicators/fibonacci.py:17-31`
- **Status:** FALSK_POSITIV
- **Ursprunglig severity:** CRITICAL (85)
- **Verifiering:** Koden anvander `None`-sentinel + `__post_init__` som
  korrekt satter nya listor/dicts per instans. Det ar INTE en klassisk
  mutable-default-bugg. Typsignaturen `list[float] = None` ar stilistiskt
  suboptimalt (bor vara `list[float] | None = None`) men har ingen
  funktionell effekt.
- **Ev. forbattring:** Ren type-hint-fix, ej prioriterad.

#### CR-3. "Globala caches utan thread-safety" — DELVIS (overdrivet)

- **Fil:** `src/core/optimizer/runner.py:121-142`
- **Status:** DELVIS
- **Ursprunglig severity:** CRITICAL (90)
- **Justerad severity:** LOW
- **Verifiering:** Runner.py har 5 explicita `threading.Lock`-objekt:
  - `_OPTUNA_LOCK` (rad 121)
  - `_TRIAL_KEY_CACHE_LOCK` (rad 127)
  - `_DEFAULT_CONFIG_LOCK` (rad 132)
  - `_BACKTEST_DEFAULTS_LOCK` (rad 138)
  - `_STEP_DECIMALS_CACHE_LOCK` (rad 142)
- Pastaendet "utan thread-safety" ar felaktigt. Koden har redan guards.
  Kvarstaende observation: `_JSON_CACHE` (rad 250-256) saknar explicit lock,
  men det ar minor.

#### CR-5. "Subprocess utan shell=False" — FALSK_POSITIV

- **Fil:** `src/core/optimizer/runner.py:852, 1082, 1093`
- **Status:** FALSK_POSITIV
- **Ursprunglig severity:** IMPORTANT (82)
- **Verifiering:** `subprocess.run([sys.executable, ...])` med lista-argument
  har `shell=False` som **default** i Python. Att inte explicit skriva
  `shell=False` ar inte en sakerhetsbrist — det ar Pythons standard-beteende.

---

## Del 2: Tysta fel (silent-failure-hunter)

### RUNTIME-RISKER (paverkar trading/backtest/optimization)

#### SF-1. Backtest engine svaljer per-bar exceptions tyst — VERIFIERAD

- **Fil:** `src/core/backtest/engine.py:1000-1014`
- **Status:** VERIFIERAD
- **Severity:** CRITICAL
- **Problem:** `except Exception` som `continue` utan att rakna fel.
  I optimering (`verbose=False`) gommer detta ALLA berakningsfel.
  Optimeraren kan favorisera configs som genererar fler fel (och darmed
  skippar forlorande trades), vilket skapar selection bias.
- **Impact:** Optimizer valjer potentiellt trasiga configs som "bast".
- **Fix:** Rakna per-bar-fel, faila backtest om error rate > threshold.

#### SF-2. Decision sizing faller tyst till 0.0 — VERIFIERAD

- **Fil:** `src/core/strategy/decision.py:1052-1057`
- **Status:** VERIFIERAD
- **Severity:** HIGH
- **Problem:** `except Exception: size_base = 0.0` — fem separata
  `except Exception`-block i sizing-logiken. Resulterar i `size=0.0`
  trades som inflerar backtest-metrics.
- **Impact:** Paper-orders med size 0.

#### SF-3. Fibonacci features degraderar tyst — VERIFIERAD

- **Fil:** `src/core/strategy/features_asof.py:753-760`
- **Status:** VERIFIERAD
- **Severity:** HIGH
- **Problem:** 165 rader Fibonacci-berakning wrappat i `except Exception`.
  ML-modellen far 0.0 for alla Fibonacci-features vid fel.
- **Impact:** Fundamentalt annorlunda prediktioner utan synligt fel.

#### SF-4. HTF/LTF Fibonacci gate bypassas tyst vid fel — VERIFIERAD

- **Fil:** `src/core/strategy/features_asof.py:803-815, 838-849`
- **Status:** VERIFIERAD
- **Severity:** HIGH
- **Problem:** Vid fel satts `available=False`, decision.py:s
  `missing_policy="pass"` tillater trade utan Fibonacci-gating.
- **Impact:** Sakerhetsgate kopplas bort tyst.

#### SF-5. Cache hash-kollision med GENESIS_FAST_HASH=1 — VERIFIERAD

- **Fil:** `src/core/strategy/features_asof.py:178-184`
- **Status:** VERIFIERAD
- **Severity:** MEDIUM
- **Problem:** `f"{asof_bar}:{last_close:.4f}"` — identisk hash for
  olika datasets med samma bar-index och close-pris.
- **Impact:** Stale features fran annat dataset.

#### SF-8. Vectorized vs per-bar ADX-diskrepans — VERIFIERAD

- **Fil:** `src/core/indicators/vectorized.py:47-74` vs `adx.py`
- **Status:** VERIFIERAD
- **Severity:** HIGH — determinism-brott
- **Problem:** Vectorized ADX anvander `rolling().mean()` (SMA) internt,
  per-bar ATR anvander Wilder's exponential smoothing (alpha=1/n).
- **Impact:** Precomputed features != per-bar features.

#### SF-9. Optimizer trial skippar korrupta filer tyst vid resume — VERIFIERAD

- **Fil:** `src/core/optimizer/runner.py:711-736`
- **Status:** VERIFIERAD
- **Severity:** MEDIUM
- **Problem:** `except (ValueError, OSError): continue` utan logging.

#### SF-10. `_as_config_dict` svaljer Pydantic-fel — VERIFIERAD

- **Fil:** `src/core/strategy/features_asof.py:59-69`
- **Status:** VERIFIERAD
- **Severity:** MEDIUM
- **Problem:** `except Exception: return {}` — forlorar multi_timeframe config tyst.

#### SF-11. Profit factor inf-propagation i metrics — VERIFIERAD

- **Fil:** `src/core/backtest/metrics.py:68`
- **Status:** VERIFIERAD
- **Severity:** LOW
- **Problem:** `float("inf")` clipped till 5.0 ger maximal PF-bonus for
  1-trade strategier. Hanterat men potentiellt missvisande.

#### SF-12. Precompute cache write-fel ignoreras — VERIFIERAD

- **Fil:** `src/core/backtest/engine.py:543-544`
- **Status:** VERIFIERAD
- **Severity:** LOW
- **Problem:** `except Exception: pass` vid cache-skrivning.

### API-RISKER (paverkar server endpoints)

#### SF-6. /strategy/evaluate returnerar 200 med dummy-data — VERIFIERAD

- **Fil:** `src/core/server.py:626-639`
- **Status:** VERIFIERAD
- **Severity:** MEDIUM
- **Problem:** Om `candles` saknas i payload: hardkodad dummy-data.

#### SF-7. paper_submit byter tyst symbol — VERIFIERAD

- **Fil:** `src/core/server.py:814-817`
- **Status:** VERIFIERAD
- **Severity:** MEDIUM
- **Problem:** Okand symbol -> tyst byte till `tTESTBTC:TESTUSD`.
  Plus: wallet-cap `except Exception: pass` (rad 912-914).

#### SF-13. /health returnerar "ok" vid config-lasfel — VERIFIERAD

- **Fil:** `src/core/server.py:122-128`
- **Status:** VERIFIERAD
- **Severity:** LOW
- **Problem:** `except Exception: return {"status": "ok", ...None}`.

### REDUNDANT

#### SF-14. Feature cache double-insert — REDUNDANT (= CR-1)

- **Status:** REDUNDANT — samma som CR-1.

---

## Del 3: Oanvand/foraldrad kod och filer (code-explorer)

### 3.1 Kod som bara anvands i tester (TEST_ONLY)

Dessa moduler har inga runtime-anvandare men har aktiva test-filer.
Radering kraver att associerade tester ocksa tas bort.

| Fil                                 | Test-fil                           | Git-index |
| ----------------------------------- | ---------------------------------- | --------- |
| `src/core/strategy/ema_cross.py`    | `tests/test_strategy_ema_cross.py` | tracked   |
| `src/core/indicators/fvg.py`        | `tests/test_fvg.py`                | tracked   |
| `src/core/strategy/validation.py`   | `tests/test_validation_min.py`     | tracked   |
| `src/core/backtest/walk_forward.py` | `tests/test_walk_forward.py`       | tracked   |

### 3.2 Kod som bara anvands i arkiverade scripts (ARCHIVE_ONLY)

| Fil                               | Anvandarscript                    | Git-index |
| --------------------------------- | --------------------------------- | --------- |
| `src/core/indicators/macd.py`     | `scripts/archive/debug/...`       | tracked   |
| `src/core/strategy/fvg_filter.py` | `scripts/generate_meta_labels.py` | tracked   |

### 3.3 Helt oanvanda moduler (TRULY_DEAD)

| Fil                                | Enda referens                              | Git-index |
| ---------------------------------- | ------------------------------------------ | --------- |
| `src/core/strategy/example.py`     | `docs/architecture/ARCHITECTURE_VISUAL.md` | tracked   |
| `src/core/ml/overfit_detection.py` | `docs/architecture/ARCHITECTURE_VISUAL.md` | tracked   |

### 3.4 Minimalt anvanda moduler (behover verifiering)

| Fil                                    | Kommentar                                | Kategori            |
| -------------------------------------- | ---------------------------------------- | ------------------- |
| `src/core/indicators/bollinger.py`     | I features_asof men EJ i aktiva modeller | RUNTIME (passiv)    |
| `src/core/io/bitfinex/ws_*.py` (3 st)  | WebSocket — ej anvand i backtest         | FUTURE_USE          |
| `src/core/ml/decision_matrix.py`       | Bara select_champion.py                  | SCRIPT_ONLY         |
| `src/core/ml/visualization.py`         | Bara select_champion.py                  | SCRIPT_ONLY         |
| `src/core/backtest/exit_strategies.py` | Legacy exits, HTF Fib used now           | RUNTIME (fallback?) |
| `src/core/utils/provenance.py`         | Bara train_model.py + test               | SCRIPT_ONLY         |
| `src/core/strategy/htf_selector.py`    | I evaluate.py men statisk HTF=1D         | RUNTIME             |
| `src/core/strategy/regime_unified.py`  | I evaluate.py — behover runtime-check    | RUNTIME             |

### 3.5 Deprecated scripts (30+ i scripts/)

Kandidater for arkivering till `scripts/archive/`:

- `smoke_test.py`, `smoke_test_eth.py`, `submit_test.py`
- `train_meta_model.py`, `train_regression_model.py`
- `debug_trial_1032.py`, `test_ws_public.py`
- `probe_min_order_sizes.py`, `probe_min_order_sizes_live.py`
- `smoke_submit_call.py`, `smoke_submit_flow.py`
- `analyze_feature_importance.py`, `analyze_feature_synergy.py`, `analyze_permutation_importance.py`
- `benchmark_optimizations.py`, `fdr_correction.py`, `monitor_feature_drift.py`
- `inspect_ui.py`, `migrate_model_structure.py`, `reliability.py`
- `calculate_ic_by_regime.py`, `calculate_ic_metrics.py`, `calculate_partial_ic.py`, `feature_ic_v18.py`
- `compare_swing_strategies.py`, `compare_htf_exits.py`, `compare_modes.py`
- `filter_model_features.py`, `run_timeframe_sweep.py`
- `burn_in.py`, `build_auth_headers.py`
- `summarize_hparam_results.py`, `analyze_optuna_db.py`

### 3.6 Config bloat

| Kategori                             | Antal filer | Atgard                       |
| ------------------------------------ | ----------- | ---------------------------- |
| `config/models/` — oanvanda stubs    | ~90+        | Radera allt utom tBTCUSD\_\* |
| `config/tmp/` — temporara configs    | 17 av 18    | Radera (behall README.md)    |
| `config/optimizer/` — gamla phase3/4 | ~15         | Arkivera                     |

### 3.7 Operationsstadning

#### tmp/ katalogen

- **Git-index:** `git ls-files tmp/` = **inga traffar** (INTE tracked)
- **Lokal disk:** 60+ filer (cleanup-loggar, CI-loggar, debug-output)
- **Atgard:** Rent lokalt (rm), ingen git-operation behövs. Verifierat gitignored.

#### Root-level databasfiler — STALE (atgardade i D38)

- `optimizer_phase7b.db` — **finns inte langre i root** (flyttad i D38)
- `optuna_search.db` — **finns inte langre i root** (flyttad i D38)
- **Atgard:** Ingen — redan genomfort.

#### data/ tracking — VERIFIERAT KORREKT

- **Git-index:** `git ls-files data/raw/ data/curated/ data/features/ data/metadata/`
  = **inga traffar**
- Data-filer ar redan gitignored och untracked.
- **Atgard:** Ingen — rapporten var felaktig pa denna punkt.

### 3.8 results/ residual

**results/hparam_search/** — phase7b*\* directories, run_20251226*\* directories
**results/backtests/** — orphaned equity CSV, gamla oktober-runs

Behover verifieras mot git-index fore atgard.

### 3.9 docs/ops/ (100+ cleanup contracts)

- Behall som audit trail
- Overväg att flytta D1-D38 till `docs/ops/archive/cleanup_2026-02/`

---

## Del 4: Prioriterad atgardslista

### Fas A: Kodfix (kraver gated commit-kontrakt)

Dessa paverkar RUNTIME BEHAVIOR och kraver full Opus 4.6 gate-process.

| #   | Issue                                     | Fil                      | Severity | Status     |
| --- | ----------------------------------------- | ------------------------ | -------- | ---------- |
| A1  | CR-6: Precompute cache saknar config-hash | engine.py:607-626        | HIGH     | VERIFIERAD |
| A2  | SF-1: Per-bar exception swallowing        | engine.py:1000-1014      | CRITICAL | VERIFIERAD |
| A3  | SF-8: ADX vectorized/per-bar divergens    | vectorized.py:47-74      | HIGH     | VERIFIERAD |
| A4  | SF-2: Decision sizing silent 0.0          | decision.py:1052-1057    | HIGH     | VERIFIERAD |
| A5  | SF-4: HTF/LTF gate bypass vid fel         | features_asof.py:803-849 | HIGH     | VERIFIERAD |
| A6  | SF-3: Fibonacci features tyst degradering | features_asof.py:753-760 | HIGH     | VERIFIERAD |
| A7  | SF-5: Fast hash collision                 | features_asof.py:178-184 | MEDIUM   | VERIFIERAD |
| A8  | CR-4: Mode-validering inkonsistens        | engine.py:189-206        | MEDIUM   | VERIFIERAD |
| A9  | SF-6: /evaluate dummy-data fallback       | server.py:626-639        | MEDIUM   | VERIFIERAD |
| A10 | SF-7: paper_submit tyst symbol-byte       | server.py:814-817        | MEDIUM   | VERIFIERAD |

**VARNING:** A1, A2, A3 paverkar direkt DETERMINISM och REPRODUCIBILITET.
A2 kan orsaka att optimizer favoriserar trasiga configs.
Dessa bor fixas FORE nasta Optuna-korning.

**Borttagna fran Fas A (falsk_positiv / overdrivet):**

- ~~CR-2 (mutable default)~~ — FALSK_POSITIV: `None`-sentinel + `__post_init__` korrekt.
- ~~CR-3 (thread-unsafe caches)~~ — DELVIS: 5 threading.Lock finns redan.
- ~~CR-5 (shell=False)~~ — FALSK_POSITIV: lista-argument = `shell=False` default.
- ~~CR-1/SF-14 (double-insert)~~ — VERIFIERAD men severity sänkt till LOW (redundant kod, ej korruption).

### Fas B: Dead code removal (tooling — NO BEHAVIOR CHANGE)

**Obs (rev 3):** Detta ar en kandidatlista och ar **inte exekveringsklar** som
helhet. Varje punkt maste brytas ut till separat tranche med commit-kontrakt,
scope IN/OUT och git-index-bevis innan destruktiv atgard.

| #   | Fil                                      | Kategori     | Steg                  |
| --- | ---------------------------------------- | ------------ | --------------------- |
| B1  | src/core/strategy/example.py             | TRULY_DEAD   | git rm                |
| B2  | src/core/ml/overfit_detection.py         | TRULY_DEAD   | git rm                |
| B3  | src/core/strategy/ema_cross.py + test    | TEST_ONLY    | git rm (modul + test) |
| B4  | src/core/indicators/fvg.py + test        | TEST_ONLY    | git rm (modul + test) |
| B5  | src/core/indicators/macd.py              | ARCHIVE_ONLY | git rm                |
| B6  | src/core/strategy/validation.py + test   | TEST_ONLY    | git rm (modul + test) |
| B7  | src/core/backtest/walk_forward.py + test | TEST_ONLY    | git rm (modul + test) |
| B8  | src/core/strategy/fvg_filter.py          | ARCHIVE_ONLY | git rm                |

### Fas C: Script-arkivering (tooling — NO BEHAVIOR CHANGE)

**Obs (rev 3):** Kandidatlista. Exekveras tranche-vis med exakt fillista,
referenskontroll och Opus diff-audit per tranche.

Flytta 30+ deprecated scripts till `scripts/archive/`:

- Underkategorier: `debug/`, `experiments/`, `analysis/`, `testing/`

### Fas D: Config cleanup (tooling — NO BEHAVIOR CHANGE)

**Obs (rev 3):** Kandidatlista. Exekvering kraver separat tranche-kontrakt och
git-index-verifiering for varje path-grupp.

| #   | Scope                                   | Steg                 |
| --- | --------------------------------------- | -------------------- |
| D1  | config/models/ — 90+ oanvanda stubs     | git rm               |
| D2  | config/tmp/ — 17 temporara filer        | git rm               |
| D3  | config/optimizer/ — gamla phase configs | Flytta till archive/ |

### ~~Fas E: Git hygien~~ — BORTTAGEN

**Alla pastaenden i ursprunglig Fas E verifierade som felaktiga:**

- `git ls-files tmp/` = inga traffar (inte tracked)
- `git ls-files data/raw/ data/curated/ data/features/ data/metadata/` = inga traffar
- Ingen git rm --cached behovs.

### Fas F: Results cleanup (tooling — destruktiv)

**Obs (rev 3):** Kandidatlista. Inga batch-raderingar utan tranche-vis
exekvering och explicit git-index-bevis per kandidat.

Varje punkt kraver `git ls-files`-bevis fore atgard:

- results/hparam*search/phase7b*\* (7 dirs)
- results/hparam*search/run_20251226*\* (4 dirs)
- results/backtests/ orphaned equity CSV
- results/backtests/ oktober 2025 runs

### Fas G: Docs konsolidering

- Flytta docs/ops/REPO*CLEANUP_D\**\*.md till docs/ops/archive/cleanup_2026-02/
- Behall top-level summaries och backlog i docs/ops/

---

## Del 5: Rollfordelning Opus 4.6 / Codex 5.3

### Fas A (Kodfix) — KRAVER FULL GATE-PROCESS

```
Per issue:
1. Codex: Skriver commit-kontrakt (scope IN/OUT, gates)
2. Opus: Pre-code review + godkannande
3. Codex: Implementerar minimal fix
4. Opus: Diff-audit
5. Gates: pytest subset + determinism replay
6. Commit
```

**Rekommenderad ordning:** A2 -> A1 -> A3 -> A4 -> A5 -> A6 -> A7-A10

### Fas B-G (Cleanup) — Standardkontrakt per tranche

```
Per tranche (D39, D40, ...):
1. Codex: Commit-kontrakt med exakt fillista + git-index-bevis
2. Opus: Scope-verifiering
3. Codex: git rm / flytt
4. Opus: Diff-audit (inga out-of-scope raderingar)
5. Gates: black --check, ruff check, relevant pytest
6. Commit
```

**Krav (nytt i rev 2):** Varje destruktiv atgard maste forst verifiera
git-index-status (`git ls-files <path>`) for att undvika felaktiga
`git rm --cached` pa filer som inte ar tracked.

---

## Del 6: Sammanfattning

### Findings-oversikt med status

| ID         | Severity | Status              | Kategori                |
| ---------- | -------- | ------------------- | ----------------------- |
| CR-1/SF-14 | LOW      | VERIFIERAD          | runtime (redundant kod) |
| CR-2       | -        | FALSK_POSITIV       | -                       |
| CR-3       | LOW      | DELVIS (overdrivet) | runtime                 |
| CR-4       | MEDIUM   | VERIFIERAD          | runtime                 |
| CR-5       | -        | FALSK_POSITIV       | -                       |
| CR-6       | HIGH     | VERIFIERAD          | runtime (determinism)   |
| CR-7       | LOW      | VERIFIERAD          | runtime                 |
| CR-8       | LOW      | VERIFIERAD          | runtime                 |
| SF-1       | CRITICAL | VERIFIERAD          | runtime (optimizer)     |
| SF-2       | HIGH     | VERIFIERAD          | runtime (sizing)        |
| SF-3       | HIGH     | VERIFIERAD          | runtime (features)      |
| SF-4       | HIGH     | VERIFIERAD          | runtime (safety gate)   |
| SF-5       | MEDIUM   | VERIFIERAD          | runtime (cache)         |
| SF-6       | MEDIUM   | VERIFIERAD          | api                     |
| SF-7       | MEDIUM   | VERIFIERAD          | api                     |
| SF-8       | HIGH     | VERIFIERAD          | runtime (determinism)   |
| SF-9       | MEDIUM   | VERIFIERAD          | runtime (optimizer)     |
| SF-10      | MEDIUM   | VERIFIERAD          | runtime (config)        |
| SF-11      | LOW      | VERIFIERAD          | runtime (metrics)       |
| SF-12      | LOW      | VERIFIERAD          | runtime (cache)         |
| SF-13      | LOW      | VERIFIERAD          | api                     |

### Verifierade findings per severity

| Severity      | Antal verifierade                               | Prioritet |
| ------------- | ----------------------------------------------- | --------- |
| CRITICAL      | 1 (SF-1)                                        | OMEDELBAR |
| HIGH          | 5 (CR-6, SF-2, SF-3, SF-4, SF-8)                | HOG       |
| MEDIUM        | 6 (CR-4, SF-5, SF-6, SF-7, SF-9, SF-10)         | MEDEL     |
| LOW           | 7 (CR-1, CR-3, CR-7, CR-8, SF-11, SF-12, SF-13) | LAG       |
| FALSK_POSITIV | 2 (CR-2, CR-5)                                  | -         |
| STALE         | 2 (root DBs, git hygien)                        | -         |

### Cleanup-kategorier

| Kategori                                              | Volym              | Prioritet           |
| ----------------------------------------------------- | ------------------ | ------------------- |
| Kodfix (Fas A) — verifierade runtime-risker           | 10 issues          | OMEDELBAR for A1-A3 |
| Dead code (Fas B) — TEST_ONLY/ARCHIVE_ONLY/TRULY_DEAD | 8 moduler + tester | Fas B               |
| Script-arkivering (Fas C)                             | 30+ scripts        | Fas C               |
| Config cleanup (Fas D)                                | 100+ filer         | Fas D               |
| Results residual (Fas F)                              | 10+ dirs           | Fas F               |
| Docs konsolidering (Fas G)                            | 100+ ops-docs      | Fas G               |

**Viktigaste insikten:**
Kodfix (Fas A) bor prioriteras FORE fortsatt filstadning. Speciellt A2
(per-bar exception swallowing — CRITICAL), A1 (precompute cache utan
config-hash), och A3 (ADX divergens) paverkar direkt KVALITETEN PA
OPTIMIZER-RESULTAT och bor fixas innan nasta Optuna-korning.

---

_Rapport genererad 2026-02-15 av Claude Code (Opus 4.6) med tre parallella
analysagenter. Rev 2 efter manuell verifiering._
