# README for AI Agents (Local Development)

## Last update: 2025-12-02

This document explains the current workflow for Genesis-Core, highlights today's deliverables, and lists the next tasks for the hand-off.

## 1. Deliverables (latest highlights: 2025-12-03)

- **CHAMPION UPDATE (2025-12-03)**: Uppdaterade `config/strategy/champions/tBTCUSD_1h.json` med parametrar från `run_20251203_105838` (Trial 001).

  - **Orsak**: Tidigare champion var optimerad för en kodbas med ATR-bugg (14 vs 28 period) och HTF-logikfel. Nya parametrar är anpassade för den fixade logiken.
  - **Resultat**: Backtest 2024-01-01 till 2024-12-31 ger 201 trades, PF 1.25, +3.36% return.
  - **Nyckeländringar**: `entry_conf_overall` höjd till 0.24 (från 0.09), `ltf_override_threshold` sänkt till 0.36 (från 0.66).

- **PHASE 3 FINE TUNING (v7) - DEBUGGING (2025-12-03)**:

  - **Zero Trades Fix**: Löste problemet med 0 trades i v7 genom att tillåta negativa deltas i `risk.risk_map_deltas` (t.ex. `conf_0` ner till -0.30). Detta lät optimizern sänka trösklar tillräckligt för att generera trades (1000+ i test).
  - **Regression**: Vid omkörning av smoke-test (`tBTCUSD_1h_optuna_phase3_fine_v7_smoke.yaml`) uppstod `TypeError: float() argument must be a string or a real number, not 'dict'` i `param_transforms.py`.
  - **Analys**: `deltas.get()` returnerar en dict istället för float, vilket tyder på att `runner.py` expanderar dot-notation keys felaktigt för `risk.risk_map_deltas`.
  - **Status**: Pausad för felsökning. Dokumentation uppdaterad i `docs/daily_summaries/daily_summary_2025-12-03.md`.

- **PHASE 3 FINE TUNING STARTED (2025-12-03)**: Startade optimering med `config/optimizer/tBTCUSD_1h_optuna_phase3_fine_v2.yaml` (100 trials, PF > 1.20 mål).

  - **Konfiguration**: Nästlad YAML-struktur för att passera preflight.
  - **Motor**: Vectorized Fibonacci (~240 bars/sec) + Single-threaded (`max_concurrent: 1`).
  - **Status**: Körs nu (Run ID: `optuna_phase3_fine_12m_v4`).

- **FIBONACCI VECTORIZATION (2025-12-03)**: Vektoriserade `detect_swing_points` i `src/core/indicators/fibonacci.py` för att eliminera iterativ `while`-loop. Implementerade O(1) tröskelberäkning (`min(max_h, max_l)`) och NumPy-baserad filtrering.

  - **Prestanda**: Benchmark visar ~15ms per call (3.2M bars/sec) på syntetisk data.
  - **Verifiering**: Alla unit tests (`tests/test_fibonacci.py`) passerade. Smoke test (`tBTCUSD_1h_champion_centered_smoke.yaml`) körde 5 trials framgångsrikt med ~70s runtime och genererade trades.
  - **Extended Smoke Test**: Körde 12-månaders test (2024-01-01 till 2024-12-31) med 5 trials. Total tid 5:59 min. Resultat: Stabilt, ~240 bars/sec. Trial 0 gav positiv avkastning (+1.66%). Noterade `[DEBUG] Invalid swing` varningar i loggen (icke-kritisk, indikerar High < Low i vissa marknadslägen).
  - **Cleanup**: Minskade loggbrus i `decision.py` (kommenterade ut FORENSIC logs).
  - **Status**: Redo för fullskalig optimering.

- **PRECOMPUTE TIMING FIX (2025-12-02)**: Löste kritisk timing-bug som hindrade precompute features från att fungera i Optuna-optimeringar. Root cause: `precompute_features`-flaggan sattes EFTER `engine.load_data()` (runner.py line 816), men feature-generering sker UNDER `load_data()` (engine.py line 233). Solution: Flyttade flag-setting till före load_data() (lines 807-810). Resultat: 20x speedup verifierad (~100 bars/sec vs ~10 bars/sec), 5-trial smoke test går från 30 min till 2.5 min. Ytterligare fixes: Import-arkitektur (src.core → core), preflight-validering (`check_precompute_functionality()`), varningar när PRECOMPUTE utan fast_window. Cache thread-safety issue upptäckt vid max_concurrent>1 (temporary fix: max_concurrent=1). Dokumentation: `docs/bugs/PRECOMPUTE_TIMING_FIX_20251202.md`. Commit: 5551fcc pushat till Phase-7d.

- **MODE ENFORCEMENT (2025-11-27)**: Löste determinism-problemet mellan streaming och fast mode. Implementerade:
  1. **Validation i BacktestEngine**: Kastar ValueError om `fast_window=True` utan `GENESIS_PRECOMPUTE_FEATURES=1`, varnar vid omvänd kombination
  2. **Default till fast mode**: `run_backtest.py` och `runner.py` defaultar nu till fast mode (`GENESIS_FAST_WINDOW=1` + `GENESIS_PRECOMPUTE_FEATURES=1`) för determinism
  3. **Deprecated streaming mode**: `compare_modes.py` deprecerad - kör endast fast mode och visar varning att använda `run_backtest.py` istället
  4. Root cause: Streaming och fast mode körde olika code paths (iterativ vs batch) vilket gav olika trade counts (530 vs 886, 1078 vs 889 i olika körningar). Detta påverkade alla tester och optimeringar.
  5. Dokumentation: Alla nya backtests och optimeringar använder nu konsekvent fast mode för reproducerbarhet.
  6. **Verifierad determinism (manuella backtests)**: Dubbelkörning med champion-config (2024-06-01 till 2024-08-01) gav EXAKT identiska resultat (43 trades, -1.47%, PF 0.77, score -100.2217) i båda körningarna.
  7. **Verifierad determinism (optimizer)**: Dubbelkörning med 3-trial grid gav EXAKT identiska scores i alla trials (Trial 1: -100.2123, Trial 2: -100.3729, Trial 3: -100.5498) med 15+ decimalers precision. Detta bekräftar att både manuella backtester OCH optimizer-körningar nu är helt deterministiska.
  8. **Tests implementerade**: 5 unit tests (pytest) + 2 deterministiska verifieringstester (manuella dubbelkörningar)
  9. **Filerna uppdaterade**: `src/core/backtest/engine.py`, `scripts/run_backtest.py`, `src/core/optimizer/runner.py`, `scripts/compare_modes.py`
  10. **Dokumentation skapad**: `docs/bugs/MODE_ENFORCEMENT_20251127.md` (fullständig teknisk beskrivning + båda verifieringstesterna)
- **OPTIMIZER REPRODUCTION SOLVED (2025-11-26)**: Löste mysteriet med Trial 1032 (+22.75% i optimizer vs -16.65% manuellt). Root cause var att optimizern kör med `GENESIS_FAST_WINDOW=1` och `GENESIS_PRECOMPUTE_FEATURES=1`, vilket ger en annan exekveringsväg (batch) än default (streaming). Manuella backtester måste använda dessa miljövariabler för att matcha optimizern. Skapade `scripts/run_backtest_fast.py` för enkel reproduktion. Dokumentation: `docs/bugs/OPTIMIZER_REPRODUCTION_ENV_VARS_20251126.md`.
- **OPTUNA CACHE REUSE FIX (2025-11-20)**: Implementerade Alternativ B för att eliminera duplicat-loop (98.8% → <10%). Objective-funktionen återanvänder nu cachade scores istället för att returnera -1e6/0.0, vilket ger TPE optimal feedback. Ny `score_memory` dict sparar scores per parameter-hash; när `make_trial` returnerar `from_cache=True` payload, returneras verklig score direkt. Cache-statistik loggas efter varje run (hit rate, unique backtests); varningar vid >80% (för smal sökrymd) eller <5% (god diversitet). Informationsförlust: 0-5% (vs 10-20% för Alt A, 80-90% för Alt C). Dokumentation: `docs/optuna/CACHE_REUSE_FIX_20251120.md`. Smoke-test: `scripts/test_optuna_cache_reuse.py`. Backup: `src/core/optimizer/runner.py.backup_20251120`.
- **CHAMPION REPRODUCIBILITY (2025-11-20)**: Implementerade Alternativ 1 - Complete Config Storage för att lösa reproducerbarhetsproblem. Champions sparar nu `merged_config` (runtime + trial params) och `runtime_version` i både backtest-resultat och champion-filer. Backtest-kod detekterar "complete champions" och skippar runtime-merge, vilket garanterar identiska resultat oavsett framtida runtime-ändringar. Backward-compatible: gamla champions utan merged_config fortsätter fungera med runtime-merge. Dokumentation: `docs/config/CHAMPION_REPRODUCIBILITY.md`. Verifierade med champion_base.json (222 trades) och aggressive.json (938 trades) - båda sparar merged_config korrekt.
- **CRITICAL BUG FIX (2025-11-20)**: Löste zero-trade bug orsakad av `float(None)` TypeError i `decision.py`. Root cause: `min_edge = float((cfg.get("thresholds") or {}).get("min_edge", 0.0))` kastade exception när config innehöll `"min_edge": null` explicit. Exception fångades tyst och resulterade i 0 trades trots giltiga kandidater. Solution: Införde `safe_float()` helper som hanterar None korrekt. Resultat: champion_base.json gick från 0 → 3 trades, balanced.json från 0 → 2147 trades. Full dokumentation i `docs/bugs/FLOAT_NONE_BUG_20251120.md`.
- Champion tBTCUSD 1h återställd till originalparametrarna från `run_20251023_141747`; manuell backtest (`tBTCUSD_1h_20251114_154009.json`) visar 0 trades tills `htf_fib`/`ltf_fib` metadata matas genom pipelinen.
- Ny Optuna-konfiguration `config/optimizer/tBTCUSD_1h_optuna_remodel_v1.yaml` (120 trials, bred sökrymd inkl. fib-gates, risk map, exit/MTF) är live i run `run_20251114_remodel_bootstrap`; bootstrap-trials producerar nu 100+ trades och constraints filtrerar 1–2-trade-spikar.
- Robust scoring: PF/DD från trades/equity via `core.backtest.metrics.calculate_metrics` (inte summary). Skyddat `return_to_dd`.
- `PositionTracker.get_summary()` rapporterar korrekt `profit_factor` (gross_profit/gross_loss) och `max_drawdown` från equity‑kurva.
- Constraints separerade från scoringens “hard_failures” och styrs via YAML (`include_scoring_failures`).
- Determinism: runner sätter `GENESIS_RANDOM_SEED=42` om inte redan satt.
- Performance‑läge: `GENESIS_FAST_WINDOW=1`, `GENESIS_PRECOMPUTE_FEATURES=1` (se `docs/features/FEATURE_COMPUTATION_MODES.md`).
- YAML‑schema: bladnoder MÅSTE ha `type: fixed|grid|float|int|loguniform` (annars values/value‑fel).
- Optuna-sökrymden breddad: fler kontinuerliga noder (entry/regime/hysteresis/max hold/risk map/HTF+LTF flippar) och `bootstrap_random_trials` (32 RandomSampler-trials sekventiellt) innan TPE.
- Soft constraints returnerar nu `score - 1e3` (tidigare -1e6) för bättre signal till samplern utan att belöna felaktiga försök.
- `RuntimeConfig`-schemat täcker nu `warmup_bars`, `htf_exit_config` samt kompletta `htf_fib`/`ltf_fib` block; `config/runtime.json` version 94 är uppdaterad till champion-parametrarna från `config/strategy/champions/tBTCUSD_1h.json` så fib-gates/partials testas i runtime direkt.
- `features.percentiles/versions` accepteras nu av `RuntimeConfig`, så tmp-profiler som styr feature-klippning/flaggar kan patchas via `scripts/apply_runtime_patch.py` utan att fältet tappas bort.
- `RuntimeConfig` tillåter extra metadata (`description`, `status`, `feature_coefficients`, kommentar-fält osv.) i alla sektioner; tmp-profiler som `config/tmp/v17_6h_exceptional.json` kan därmed patchas rakt in utan att förlora dokumentation.
- `core/strategy/decision.py` loggar nu varje gate-orasak (`[DECISION] ...`) – EV-block, proba/edge, HTF/LTF-fib orsaker, hysteresis/cooldown samt risk sizing – så 0-trade runs kan felsökas direkt i loggen utan att tweaka i blindo.
- **Phase-8 reset**: fullständig snapshot av `config/`, `data/`, `reports/`, `results/` och `cache/` ligger under `results/_archive/Phase8_kickoff/`. Aktiva kataloger har tömts (endast seedad `config/runtime.json` + tracked baselinefiler kvar) så nästa agent startar från helt ren miljö.
- **Phase 2d (v6) Success (2025-11-21)**: Löste "Zero Trades"-problemet genom att sänka tröskelvärdena (Entry 0.24-0.34, Zones 0.22-0.30). Run `run_20251121_103811` genererade ~100-120 trades/år med PF ~1.04. Phase 3 (Fine Tuning) är förberedd för att höja kvaliteten. Dokumentation: `docs/optimization/PHASE2D_SUMMARY_20251121.md`.
- **Phase 3 Started (2025-11-21)**: Startade "Fine Tuning" (Phase 3) med `config/optimizer/tBTCUSD_1h_optuna_phase3_fine.yaml`. Mål: PF > 1.15 genom att förfina exits och entries baserat på Phase 2d-resultat. Körs via `scripts/run_phase3_fine.py`.
- **PR #19 Merged (2025-11-21)**: Merged performance fixes (Champion Loader Cache, Batch Percentiles, Series Creation, Optuna Config Cache). Local Optuna fixes (Cache Reuse, Abort Heuristic) were preserved and combined.
- **PR #21 Merged (2025-11-21)**: Merged Optuna performance optimizations (Batch SQLite, Caching, WAL mode) with 58-332x speedup. Includes critical fix for dot-notation parameter expansion (`_expand_dot_notation`) to ensure correct optimization. Validated with smoke test.
- **Phase 3 Restarted (2025-11-21)**: Restarted Phase 3 optimization after verifying `runtime.json` has `htf_fib` enabled. Previous run might have used incorrect config or was stopped. New run ID: `optuna_phase3_fine_12m`.
- **Phase 3 Retry (2025-11-21)**: Restarted again with `optuna_phase3_fine_12m_v2` and `MAX_CONCURRENT=2` due to SQLite `disk I/O error` on previous attempt.
- **Phase 3 Fix & Success (2025-11-21)**: Fixed critical bug where dot-notation keys in Optuna config were ignored by the runner (causing identical results). Patched `src/core/optimizer/param_transforms.py` to expand dot-notation. Re-ran optimization (`run_20251121_140023`) which produced varied results. Best trial (`trial_009`) achieved Score 0.1634, PF 1.16, Return +6.15%, meeting the Phase 3 target. Documentation: `docs/optimization/PHASE3_FIX_AND_RESULTS_20251121.md`.
- **Phase 3 Wide Failure (2025-11-25)**: Run `run_20251125_082700` crashed at trial 177 (SQLite I/O error). Analysis revealed 0 valid trials due to `LTF_FIB_BLOCK` preventing trades (fixed `long_max_level=0.786` blocked strong trends). Action: Widen search space for Fib levels and tolerances, reduce concurrency. Docs: `docs/optimization/PHASE3_WIDE_FAIL_ANALYSIS_20251125.md`.
- **Phase 3 Wide v2 Started (2025-11-25)**: Launched `run_20251125_090251` with corrected parameters (Fib levels optimized, tolerance up to 3.0 ATR) and reduced concurrency (2 workers). Early logs show healthy trade volume.
- **Phase 3 Wide v3 (2025-11-25)**: Restarted optimization (`run_20251125_100252` approx) after fixing a critical bug in `BacktestEngine` where `max_hold_bars` was ignored, causing positions to be held indefinitely and reducing trade count. v3 should produce significantly more trades.
- **OPTIMIZER REPORTING FIX (2025-11-25)**: Fixed a critical bug where optimization trials were incorrectly reported as having exactly 5 trades. Root cause was a case-sensitive regex in `runner.py` failing to match `[SAVED] Results: ...`, causing a fallback to a dummy file (`tBTCUSD_1h_diffcache_2.json`) that contained 5 trades. Deleted the trap file and updated regex to be robust. Docs: `docs/bugs/OPTIMIZER_REPORTING_FIX_20251125.md`.
- **COMMISSION FEE UPDATE (2025-11-25)**: Updated default commission rate from 0.1% to 0.2% (Taker fee) in `BacktestEngine`, `PositionTracker`, and `run_backtest.py` to better reflect realistic costs on Bitfinex. This increases the total round-trip cost estimate to ~0.50% (incl. slippage). Phase 3 Wide optimization was restarted to incorporate these stricter cost assumptions.
- **ATR PERIOD FIX (2025-11-25)**: Fixed a critical bug where `features_asof.py` and `engine.py` ignored the configured `atr_period` (e.g., 28) and hardcoded `atr_14`. This caused `LTF_FIB_BLOCK` to reject trades due to incorrect volatility tolerance. Refactored both files to respect the config. Verification: Backtest trades increased from 1 to 978 (PF 1.01). Docs: `docs/bugs/ATR_PERIOD_FIX_20251125.md`.
- **PARITY TEST SUCCESS (2025-11-25)**: Confirmed mathematical parity between Optuna optimization pipeline (`runner.py`) and manual backtest (`run_backtest.py`). Initial discrepancy (-0.85% vs +0.46%) was resolved by aligning `warmup_bars` (150 vs 120). Both engines now produce identical trade counts (386) and returns (-0.85%) when configured identically. Docs: `docs/validation/PARITY_TEST_20251125.md`.
- **ARCHIVED BUGGY RUNS (2025-11-25)**: Archived all `run_20251125_*` and `optuna_phase3_wide_v*.db` to `results/hparam_search/_archive/20251125_buggy_runs/`. These runs were affected by the ATR Period, Max Hold, and Commission bugs.
- **LTF PARITY INVESTIGATION (2025-11-26)**: `features_asof` filtrerar nu bort prekompade swing-serier när `_global_index` visar att backtestfönstret börjar mitt i historiken (window_start_idx > 0). Detta hindrar LTF-gaten från att få nivåer som inte finns i streamingflödet. `scripts/diagnose_feature_parity.py --start-bar 190 --bars 40 --warmup 150` visar dock fortfarande 7 avvikelser (bar 210–228). Både streaming och precompute kör nu “slow path”, så kvarvarande skillnader beror på LTF-swing-detektionen snarare än ATR. Nästa steg: dumpa `swing_high/low` + `levels` per bar eller instrumentera `debug_fib_flow` för att jämföra nivåerna.
- **Phase 3 Wide v7 Ready (2025-11-25)**: Created `config/optimizer/tBTCUSD_1h_optuna_phase3_wide_v7.yaml` with `warmup_bars: 150` and updated study name. This is the clean start for Phase 3 Wide exploration.
- **In-process QA/optimizer test (2025-11-25)**: Körde hela verktygssviten (black, ruff, bandit, pytest samt `pre-commit run --all-files`) direkt i samma process som huvudagenten. Testet bekräftade att in-process-läget fungerar funktionellt men gav ingen prestandafördel och försvårade logg-isolering, så vi fortsätter med subprocess-läget i den ordinarie optimeringspipen.
- **PERFORMANCE OVERHAUL (2025-11-26)**: Genomförde omfattande optimeringar av backtestmotorn:
  1. **Vectorization**: `rsi.py`, `atr.py` och `adx.py` omskrivna till NumPy för O(1)/O(N) prestanda istället för Python-loopar.
  2. **Optuna Pruning**: Implementerade stöd för `pruning_callback` i `BacktestEngine` och `scripts/run_backtest.py`. Optuna kan nu avbryta dåliga trials tidigt (var 100:e bar).
  3. **RAM Caching (Experimental)**: Lade till `GENESIS_IN_PROCESS=1` stöd i `runner.py`. OBS: På Windows orsakar GIL massiv prestandaförlust (12x långsammare), så använd `GENESIS_IN_PROCESS=0` (Subprocess) som default.
  4. **Reduced Logging**: Tvingar `LOG_LEVEL=WARNING` i subprocesser för att minska I/O-overhead.
  5. **Critical Fixes**: Fixade `AttributeError` i `PositionTracker` (`current_capital` -> `current_equity`) och `runner.py` scope-fel.
     Dokumentation: `docs/performance/OPTIMIZATION_20251126.md`.

## 2. Snabbguide (Optuna körflöde, uppdaterad)

1. Preflight & Validate

```powershell
python scripts/preflight_optuna_check.py config/optimizer/<config>.yaml
python scripts/validate_optimizer_config.py config/optimizer/<config>.yaml
```

2. Miljö (snabbkörning)

```powershell
$Env:GENESIS_FAST_WINDOW='1'
$Env:GENESIS_PRECOMPUTE_FEATURES='1'
$Env:GENESIS_MAX_CONCURRENT='4'
$Env:GENESIS_RANDOM_SEED='42'
```

> Tip: Ange även `OPTUNA_MAX_DUPLICATE_STREAK=2000` och kontrollera att konfigen har `bootstrap_random_trials` (32–40) för att tvinga fram en deterministisk RandomSampler-uppstartsfas innan TPE tar över.

3. Start

```powershell
python -c "from core.optimizer.runner import run_optimizer; from pathlib import Path; run_optimizer(Path('config/optimizer/<config>.yaml'))"
```

4. Summera

```powershell
python scripts/optimizer.py summarize run_<YYYYMMDD_HHMMSS> --top 10
```

## 3. Optimisation workflow (coarse -> proxy -> fine)

**KRITISKT: Validera ALLTID innan lång körning (>30 min):**

```powershell
python scripts/validate_optimizer_config.py config/optimizer/<config>.yaml
```

Valideringen MÅSTE returnera 0 innan körning. Fixa alla \[ERROR]-fel och granska \[WARN]-varningar.

**Preflight-checklista för Optuna-körningar (KÖR INNAN LÅNGA KÖRNINGAR):**

```powershell
python scripts/preflight_optuna_check.py config/optimizer/<config>.yaml
python scripts/validate_optimizer_config.py config/optimizer/<config>.yaml
```

**Checklista:**

- [ ] **Preflight-check**: Kör `preflight_optuna_check.py` → måste returnera 0
  - Optuna installerat
  - Storage skrivbart och **ingen** tidigare DB-fil när `resume=false`
  - Study resume fungerar (om resume=true)
  - Sampler har `n_startup_trials ≥ 15` + `n_ei_candidates` satt
  - Timeout/max_trials korrekt konfigurerat
  - Parametrar valid
  - Gamla run-cacher flyttade/arkiverade innan start (töm `_cache/`)
- [ ] **Champion-validering**: Kör `validate_optimizer_config.py` → måste returnera 0
  - Championens partial_1_pct och partial_2_pct finns i sökrymden eller är fixerade korrekt
  - Championens signal_adaptation hanteras (antingen i sökrymden eller medvetet utelämnad)
  - Championens parametrar kan reproduceras i sökrymden
  - Inga kritiska parametrar är utelämnade eller fixerade till fel värden
- [ ] **Baseline-test**: Testa championens exakta parametrar på samma tidsperiod först
- [ ] **max_trials vs timeout**: Om du vill köra i X timmar, sätt `max_trials: null` och `timeout_seconds: X*3600`. Om både max_trials och timeout är satta stoppar Optuna när första gränsen nås.

1. **Coarse grid** - `config/optimizer/tBTCUSD_1h_coarse_grid.yaml`

   ```powershell
   python -m core.optimizer.runner config/optimizer/tBTCUSD_1h_coarse_grid.yaml
   ```

2. **Proxy Optuna (fast 2m)** - `config/optimizer/tBTCUSD_1h_proxy_optuna.yaml`

   ```powershell
   python test_optuna_new_1_3months.py --config config/optimizer/tBTCUSD_1h_proxy_optuna.yaml
   ```

   Study file: `optuna_tBTCUSD_1h_proxy.db` (resumable).

3. **Fine Optuna (6m)** - `config/optimizer/tBTCUSD_1h_fine_optuna.yaml`

   ```powershell
   python test_optuna_new_1_3months.py --config config/optimizer/tBTCUSD_1h_fine_optuna.yaml
   ```

   Study file: `optuna_tBTCUSD_1h_fine.db`.

4. **Optional Fibonacci grid** - warm up HTF exit kombinationer snabbt:

   ```powershell
   python -m core.optimizer.runner config/optimizer/tBTCUSD_1h_fib_grid_v2.yaml
   ```

   Använd detta innan du startar långa Optuna-körningar när du itererar på fib gating.

5. **Sammanfattningar**

   ```powershell
   python -m scripts.summarize_hparam_results --run-dir results/hparam_search/<run_id>
   python scripts/optimizer.py summarize <run_id> --top 5
   ```

6. **Full validation (optional)** - `config/optimizer/tBTCUSD_1h_new_optuna.yaml` (`optuna_tBTCUSD_1h_6m.db`).
7. **Champion update** - update `config/strategy/champions/<symbol>_<tf>.json` once a winner is validated.
8. **Documentation** - log outcomes in `docs/daily_summaries/daily_summary_YYYY-MM-DD.md` and this file.

## 4. Champion status

Champion file: `config/strategy/champions/tBTCUSD_1h.json`

- Source run: `run_20251023_141747`, `trial_002` (parametrarna återställda 2025-11-14).
- Key parameters: `entry_conf_overall = 0.35`, `regime_proba.balanced = 0.70`, risk map `[[0.45, 0.015], [0.55, 0.025], [0.65, 0.035]]`, `exit_conf_threshold = 0.40`, `max_hold_bars = 20`, HTF/LTF-fib-gates aktiva.
- Senaste backtest (2025-11-14, `results/backtests/tBTCUSD_1h_20251114_154009.json`) gav 0 trades → pipelinen matar ännu inte `htf_fib`/`ltf_fib` metadata när gatesen är på. Åtgärda innan champion används skarpt.
- Historisk referens: `results/backtests/tBTCUSD_1h_20251023_162506.json` -> net +10.43 %, PF 3.30, 75 trades.

## 5. Result caching

- Parameter hashes stored per run in `_cache/<hash>.json` (under each `results/hparam_search/run_*` directory).
- Re-running an identical configuration reuses cached payloads and skips redundant backtests.
- Cached entries include backtest paths, scores and metrics for quick reuse.

## 6. CLI usage (`scripts/optimizer.py`)

- `summarize <run_id> [--top N]` prints meta, counts, durations, best trials.

  ```bash
  python scripts/optimizer.py summarize run_20251023_141747 --top 5
  ```

## 7. Test & QA status

- Targeted tests that previously failed due to `Settings` validation now pass:

  ```powershell
  python -m pytest tests/test_config_api_e2e.py::test_runtime_endpoints_e2e -q
  python -m pytest tests/test_exchange_client.py::test_build_and_request_smoke -q
  python -m pytest tests/test_ui_endpoints.py::test_debug_auth_masked -q
  ```

  They rely on the local `.env`; keep placeholder secrets or inject fixtures before running in CI.

- Bandit run touched the full `.venv`, producing 1,100+ third-party findings. Prefer:

  ```powershell
  bandit -r src -ll --skip B101,B102,B110
  ```

  Adjust the ignore list as needed to keep focus on first-party code.

## 8. Next steps for hand-off (Dec 2025)

1. **Monitor Phase 3 Fine Tuning**:

   - Ensure `optuna_phase3_fine_12m_v4` completes at least 50-100 trials.
   - Analyze results using `scripts/analyze_optuna_db.py`.
   - Target: PF > 1.20.

2. **Validate Best Candidate**:

   - Once a candidate with PF > 1.20 is found, run a full backtest with `scripts/run_backtest.py` to verify metrics and trade distribution.
   - Check for "Invalid swing" warnings in logs (non-critical but worth noting).

3. **Prepare Phase 4 (Walk-Forward)**:

   - If Phase 3 is successful, prepare a Walk-Forward Analysis (WFA) configuration to validate robustness over rolling windows.

4. **Documentation**:
   - Keep `docs/optimization/PHASE3_FINE_TUNING_LOG.md` updated with major events.
   - Update `config/strategy/champions/tBTCUSD_1h.json` if a new champion is crowned.

## 9. Recent history (Phase-7a/7b, 21 Oct 2025)

- Locked snapshot: `tBTCUSD_1h_2024-10-22_2025-10-01_v1`.
- Baseline backtest: `results/backtests/tBTCUSD_1h_20251020_155245.json`.
- Runner enhancements: resume/skip, metadata, concurrency, retries.
- ChampionManager & ChampionLoader integrated into pipeline/backtest flows.
- Walk-forward runs (`wf_tBTCUSD_1h_20251021_090446`, ATR zone tweak `wf_tBTCUSD_1h_20251021_094334`).
- Optuna integration (median pruner), CLI summary (`scripts/optimizer.py summarize --top N`), documentation in `docs/optimizer.md` and `docs/TODO.md`.
- Exit improvement plan documented in `docs/fibonacci/FIBONACCI_FRAKTAL_EXITS IMPLEMENTATION_PLAN.md`.

## 10. Deployment and operations

- Designed for single-user operation; secrets live in `.env`.
- Production deployment: personal VPS or equivalent.
- Champion configs in `config/strategy/champions/`, loaded by `ChampionLoader`.

## 11. Agent rules

- Keep `core/strategy/*` deterministic and side-effect free.
- Do not log secrets; use `core.utils.logging_redaction` if needed.
- Pause when uncertain and verify with tests.
- Add unit tests for new logic; target < 20 ms per module.
- Use `metrics` only in orchestration (`core/strategy/evaluate.py`).
- Respect cached results and always save backtests under `results/backtests/`.

## 12. Setup (Windows PowerShell)

```powershell
python -m venv .venv
. .\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -e .[dev,ml]
```

## 13. Quick start and key references

- Feature pipeline: `src/core/strategy/features_asof.py`, `scripts/precompute_features_v17.py`.
- Backtesting: `scripts/run_backtest.py --symbol tBTCUSD --timeframe 1h --capital 10000`.
- Model training: `scripts/train_model.py` (see `docs/features/FEATURE_COMPUTATION_MODES.md`).
- Indicator reference: `docs/INDICATORS_REFERENCE.md`.
- Exit logic: `docs/exit_logic/EXIT_LOGIC_IMPLEMENTATION.md`.
- Validation checklist: `docs/validation/VALIDATION_CHECKLIST.md`.
- Next exits phase (Fibonacci): `docs/fibonacci/FIBONACCI_FRAKTAL_EXITS_IMPLEMENTATION_PLAN.md`.
- Model cache reset: `curl -X POST http://127.0.0.1:8000/models/reload` after retraining.

---

> **Kom ihag:** folj flodet _coarse -> proxy -> fine_, utnyttja cache-filerna och dokumentera resultaten i `docs/daily_summaries/daily_summary_YYYY-MM-DD.md`. Nasta agent borjar med att aktivera HTF-filtret i beslutslogiken, kalibrera fib-parametrarna och uppdatera dokumentationen darefter.

## 14. Uppdateringar 30 okt 2025

- Upstream-merge lade till `.github/copilot-instructions.md` (kort agentguide), förfinade beslutslogiken (`src/core/strategy/decision.py`, `evaluate.py`) samt indikatorerna (`src/core/indicators/fibonacci.py`, `htf_fibonacci.py`).
- Nya referensdokument: `docs/fibonacci/FIB_GATING_DEBUG_20251027.md`, `docs/risk/RISK_MAP_CONFIDENCE_TUNING.md` – använd dem när fib-toleranser eller riskkartor justeras.
- Temporära JSON-profiler (`tmp_*.json`) och `tmp_reason_counts.py` innehåller kandidatkonfigurationer och statistik från senaste fib-gating-debuggen. Rensa eller migrera värdefulla varianter till `config/` innan de tas bort.
- Champion-filen `config/strategy/champions/tBTCUSD_1h.json` uppdaterades med finjusterade fibparametrar. Stäm av mot nya `state_out`-fält och säkerställ att HTF/LTF-konteksten nu flödar hela vägen från `features_asof` -> `evaluate_pipeline` -> `decision`.
- `cursor-active-rules.mdc` är nedtrimmad (~50 rader) och `AGENTS.md` ersätter tidigare `README.agents.md`; håll båda synkade med de här noteringarna inför nästa handoff.

## 15. Roller för parallella agenter

- **Agent A – Optimering & körningar**
  - Starta `python -m core.optimizer.runner ...` / Optuna-jobb enligt plan (coarse → proxy → fine → fib-grid).
  - Säkerställ att resultaten sparas i `results/hparam_search/run_*` och att `tmp_*`-konfigurationer versioneras vid behov.
  - Meddela resultat-ID, score, trades och nyckelmetriker till Agent B efter varje körning.
- **Agent B – Analys & dokumentation**
  - Jämför inkomna resultat mot champion (`score ≥ 260`), uppdatera `AGENTS.md` + relevanta docs (`docs/fibonacci/FIB_GATING_DEBUG_*.md`, `docs/risk/RISK_MAP_CONFIDENCE_TUNING.md`).
  - Kör regressionstester (fib-gates, ATR=0, missing context) och flagga avvikelser.
  - Rensa/migrera temporära profiler när de inte längre behövs och synka status tillbaka till Agent A.
- **Gemensamma krav**
  - Följ `.cursor/rules/cursor-active-rules.mdc` (svenska svar, stegvis arbete, stabiliseringspolicy).
  - Koordinera via mini-loggar i chatten; vid osäkerhet, pausa och bekräfta innan nästa steg.

## 16. Fib-grid körning 2025-10-30 (run_20251030_110227)

- Körning utförd med aktiverad `.venv` och nytt konfigpaket `config/optimizer/tBTCUSD_1h_fib_grid_v3.yaml` (snävare `fib_threshold_atr` 0.6–0.7 och `trail_atr_multiplier` 2.3–2.7, trailing alltid aktiv).
- `python -m core.optimizer.runner ... --run-id run_20251030_110227` genererade 31 försök (15 giltiga). Bästa trial (`trial_001`, `tBTCUSD_1h_20251030_120515.json`) gav score 46.89, total_return +1.87 %, PF 1.91, 91 trades – långt under championmålet (260+).
- Upprepade parametrar (t.ex. enable_partials true/false) ligger fortfarande på championens baseline; överväg att öppna upp tolerans-grid för HTF-entry i stället eller kombinera med LTF-gate-justering.
- Observera att tidigare körningar utan aktiv venv hamnade under `.venv/Lib/results/...` och misslyckades p.g.a. `ModuleNotFoundError: scripts`. Lämna dem som referens men blanda inte ihop med projektets run-logg.
- Nästa steg: antingen justera grid-intervallet (t.ex. `fib_threshold_atr` ≥ 0.7 med toleranser) eller gå vidare till warm-startad Optuna baserat på championens parametrar. Dokumentera jämförelser och uppdatera fib-debuggares anteckningar.

## 17. Entry-grid snabbkörning 2025-10-30 (run_20251030_115454)

- Snabb testkörning med `config/optimizer/tBTCUSD_1h_fib_entry_grid_quick.yaml` (8 kombinationer: HTF tolerance 0.45/0.55, LTF tolerance 0.4/0.5, fib-nivåer enligt champion, entry missing_policy=pass).
- `python -m core.optimizer.runner ... --run-id run_20251030_fibentry_quick` skapade `results/hparam_search/run_20251030_115454` (5 försök, 2 giltiga). Bästa trial (`trial_001`) gav score 46.89, +1.87 %, PF 1.91, 91 trades – identiskt med exit-griden, ingen förbättring vs champion.
- Slutsats: Behöver öppna upp targetlistor/toleranser bredare (eller optimera entry_conf/signal_adaptation) innan nästa större körning; planera nattkörning med `tBTCUSD_1h_fib_entry_grid.yaml` (64 kombinationer) eller warm-startad Optuna.

## 18. Optuna-preflight 31 okt 2025

- Konfiguration `config/optimizer/tBTCUSD_1h_optuna_fib_tune.yaml` uppdaterades med championens partialer (0.6/0.5), `signal_adaptation` och heartbeat-parametrar (60s/180s).
- Seedning inför backtest körs nu deterministiskt (`GENESIS_RANDOM_SEED`, fallback 42) via `scripts/run_backtest.py`.
- Optuna-runnern (`src/core/optimizer/runner.py`) använder atomiska writes och öppnar storage via `RDBStorage` med heartbeat; loggar/cacher skrivs säkert.
- Full preflight: `scripts/validate_optimizer_config.py ...` → OK, `scripts/preflight_optuna_check.py ...` → OK (inkl. champion-validering).
- Röktest `run_20251031_smoke` mot separat DB `optuna_tBTCUSD_1h_fib_tune_smoke.db` (2 trials, loggar/best_trial.json sparade).
- Resume-test `run_20251031_resume_test` mot DB `optuna_tBTCUSD_1h_fib_tune_resume.db`; andra körningen återupptog studien (trial 3–4). Exporterade `trials.csv` + `best_params.json`.
- Systempreflight (Windows Update pausad, Power-plan Hög prestanda, temp-/nät-/diskkontroller) slutförd manuellt.
- Nästa steg: `pip freeze > reports/pip_freeze_20251031.txt` och helgkörning `run_20251101_weekend` efter dagens slut.
- Ny grid-konfig `config/optimizer/tBTCUSD_1h_ltf_confidence_grid.yaml` + skript `scripts/run_ltf_confidence_grid.py` för snabbtest av LTF-confidence mot HTF-gate (run_id genereras automatiskt, grid < 15 min).
- LTF-override: beslut logiken har ett konfigstyrt fallback (`override_confidence`) så LTF kan släppa igenom signaler när confidence ligger mellan 0.40–0.60; aktiverat i snabb-grid + override-test (`tmp_ltf_override_config.json`).
- Multi-timeframe override tillagd: `multi_timeframe`-blocket styr `use_htf_block`, `allow_ltf_override` och `ltf_override_threshold`. När override triggas loggas `[OVERRIDE] LTF override...` med symbol/tidsram och confidence för vidare analys.
- Adaptiv override (2025-10-31): `ltf_override_adaptive` beräknar tröskeln via percentil + regim-multiplikatorer, buffrar senaste LTF-konfidens och loggar varje beslut (`state_out['ltf_override_debug']`). Konfigurerat i `tmp_ltf_override_config*.json` och grid-varianten.
- 2025-10-31 16:12: Smoke-run `run_20251031_smoke2` körd mot `optuna_tBTCUSD_1h_fib_tune_smoke2.db` (1 trial, score -57.41, 23 trades). Exporter `trials.csv` + `best_params.json` skrevs till `results/hparam_search/run_20251031_smoke2/`.
- Resume-kontroll: `optuna.study.create_study(..., load_if_exists=True)` laddar smoke-studien och rapporterar 1 trial (bekräftad).
- Miljölogg 31 okt 16:05: `.venv` ok (`python 3.11.9`), `reports/pip_freeze_20251031.txt` uppdaterad, `powercfg /GETACTIVESCHEME` → Hög prestanda, `Get-PSDrive` visar 89 GB ledigt på C:.
- Manuellt kvar att dubbelkolla inför helgkörning: Windows Update-frysning, temperatur- och nätverksmonitorering påbörjade enligt rutin innan starttid.
- 2025-10-31 16:20: Timeout i `config/optimizer/tBTCUSD_1h_optuna_fib_tune.yaml` justerad till 230400s (~64h) så att körningen stannar senast runt måndag 3 nov 08:20; preflight och champion-validering körda igen (endast väntad timeout-varning).
- 2025-10-31 16:45: Samtliga `trial_*.log` flyttade till `results/hparam_search/_log_archive/20251031_preweekend/` för ren loggmiljö inför helgkörningen.
- 2025-11-03 08:05: Helgkörningen `run_20251101_weekend` avbruten p.g.a. cache-/resume-loop (identiska -80.29-score). Katalogen och `optuna_tBTCUSD_1h_fib_tune.db` arkiverade under `results/hparam_search/_archive/20251103_failed_resume/` för forensik.
- 2025-11-03 10:45: Phase-7d förberedelse – `config/optimizer/tBTCUSD_1h_optuna_fib_tune.yaml` uppdaterad med ny DB (`results/hparam_search/storage/optuna_tBTCUSD_1h_fib_tune_phase7d.db`), `resume=false`, bredare fib-/override-intervall samt TPE `n_startup_trials=25`, `n_ei_candidates=48`.
- 2025-11-03 10:50: Samtliga `results/hparam_search/run_*/_cache` flyttade till `results/hparam_search/_archive/20251103_trimmed_runs/cache_backup_phase7d/` för att undvika att nästa Optuna-run återanvänder gamla backtester.
- 2025-11-03 10:55: `scripts/preflight_optuna_check.py` utökad – varnar om DB-fil redan finns när `resume=false` samt kontrollerar sampler-kwargs. Ny preflight inkluderar kontroll av cachetömning och `n_startup_trials`.
- 2025-11-03 11:00: Dedikerad storage-mapp `results/hparam_search/storage/` skapad så kommande DB-filer isoleras per kampanj.
- 2025-11-03 11:05: `src/core/optimizer/runner.py` spårar nu param-signaturer per körning och hoppar över Optuna-förslag som upprepas fler än 10 gånger i rad (stoppar med fel om gränsen nås).

## 20. Optuna-duplicat – detektion och åtgärder (2025-11-10)

### Symptom

- Loggar likt: “Trial N finished with value: 0.0 … Best is trial M with value: 0.0”.
- Endast 1–2 `trial_*.json` trots många rapporterade trialnummer.
- Runner‑logg: `[Runner] Trial trial_001 … (score=-100.2)` och sedan inga fler lokala resultatfiler.

### Orsaker

- Skippade försök p.g.a. identiska parametrar inom run: runner markerar `duplicate_within_run` och hoppar över backtest för performance.
- Objective returnerar 0.0 för skippade trials → TPE får dålig signal och fortsätter föreslå liknande set.
- För strikt gating/constraints i uppstartsfasen (0 trades) ger ingen feedback till samplern.
- YAML‑blad utan `type:` kan tysta kollapsa sökrymden (schemafel → allt blir “fixed”).

### Omgående mitigering (utan kodändring)

1. Bredda sökrymden initialt (fler trades):
   - `thresholds.entry_conf_overall.low: 0.25`
   - `htf_fib.entry.tolerance_atr: 0.20–0.80`
   - `ltf_fib.entry.tolerance_atr: 0.20–0.80`
   - Tillåt `multi_timeframe.allow_ltf_override: true` i grid och sänk `ltf_override_threshold: 0.65–0.85`.
2. Mildra constraints tidigt:
   - `constraints.min_trades: 1–3`, `min_profit_factor: 0.8`, `max_max_dd: 0.35`
   - Låt `include_scoring_failures: false` så scoringens hårda fel inte kortsluter utforskning.
3. Sampler‑inställningar:
   - `tpe` med `constant_liar: true`, `multivariate: true`, höj `n_ei_candidates` (128–512).
   - `OPTUNA_MAX_DUPLICATE_STREAK` högt (t.ex. 2000) så studien inte avbryts för tidigt.
4. Unika `study_name`/`storage` per körning (timestamp) och tom `_cache/` per kampanj.

### Rekommenderad kodförbättring (nästa agent)

1. Straffa duplicat i objective:
   - I `src/core/optimizer/runner.py::_run_optuna.objective`: om payload markerats `skipped` eller `duplicate`, returnera en stor negativ poäng (t.ex. `-1e6`) i stället för `0.0`. Detta bryter TPE‑degenerering mot samma parametrar.
   - Tips: Säkerställ noll‑straff för legitima cache‑träffar endast om du vill återrapportera verklig poäng; för duplicat inom run använd hårt straff.
2. Telemetri/varning:
   - Räkna andel skippade trials; varna om `skipped_ratio > 0.5` (“hög duplicatfrekvens – bredda sökrymden eller sänk constraints”).
3. Pre‑random boost:
   - Överväg 20–30 initiala `RandomSampler`‑trials innan TPE (eller `tpe` med hög `n_startup_trials`) för att sprida förslag bättre.

### Checklista – innan långkörning

- [ ] YAML‑blad har `type:` (`fixed|grid|float|int|loguniform`).
- [ ] `study_name`/`storage` unika vid `resume=false`.
- [ ] `GENESIS_FAST_WINDOW` + `GENESIS_PRECOMPUTE_FEATURES` aktiva vid stora körningar.
- [ ] `GENESIS_RANDOM_SEED` satt (runner sätter 42 om saknas) – reproducera 2×.
- [ ] `OPTUNA_MAX_DUPLICATE_STREAK` satt till högt värde (≥200).
- [ ] Sökrymden ger trades i smoke (2–5 trials) innan långkörning.

#### Status 2025-11-11

- `config/optimizer/tBTCUSD_1h_optuna_smoke_loose.yaml` har nu bredare intervall (entry/regime/hysteresis/max_hold/risk_map) och boolska gridar för HTF/LTF‑gates & overrides. Championens risk map ligger kvar som separat grid-alternativ.
- Nytt fält `bootstrap_random_trials: 32` kör en sekventiell RandomSampler-fas innan TPE (`bootstrap_seed=42` för reproducerbarhet). Runnern väljer automatiskt `allow_resume=True` för andra fasen.
- Soft constraints returnerar `score - 1e3` istället för `-1e6` vilket håller dåliga försök långt under giltiga men ger TPE lite gradient.
- Smoke-run (`run_20251111_134030`, 32 bootstrap + 48 TPE, `max_concurrent=4`) gav 1 giltigt backtest (score 0.847, 99 trades). TPE-fasen producerade fortfarande hög duplicatfrekvens (~98.8%) → fortsätt öppna upp toleranser/risk_map och testa lägre `ltf_override_threshold` / mer varierade `signal_adaptation`.

## 19. HTF-exit tuning 3 nov 2025

- Nya temp-profilen `config/tmp/balanced_htf_tune.json` höjde `fib_threshold_atr` till 0.85 och sänkte `trail_atr_multiplier` till 1.6. Backtest (`tBTCUSD_1h_20251103_161008.json`) gav +5.42 %, PF 1.24 med 3/6 rena HTF-exits (endast 2 fallback).
- Baseline (`config/tmp/champion_base.json`) loggade 10 HTF, 8 HTF+fallback och 4 fallback-exits på +3.10 % netto – fallback används fortfarande för slutstängningar.
- Aggressiv profil (`config/tmp/aggressive.json`) gav 22 rena fallback-closer och max DD 10.9 % → aggressiva toleranser överlastar fallback-logiken.
- Rekommendation: öppna nästa grid/Optuna över `fib_threshold_atr` 0.80–0.90, `trail_atr_multiplier` 1.4–1.8 samt HTF/LTF toleranser, och tracka fallback-andelen (<40 %) som guardrail.

## 21. GENOMBROTT – signal_adaptation flaskhalsen identifierad (2025-11-13)

### Problem

Backtester gav konsekvent 34 trades, PF 0.92, -0.10% return oavsett ändringar i `entry_conf_overall`, `regime_proba`, HTF/LTF-gates eller exit-inställningar.

### Systematisk isoleringstestning

1. **Test: entry_conf_overall (0.32→0.28)** → 34 trades (oförändrat)
2. **Test: regime_proba (alla→0.50)** → 34 trades (oförändrat)
3. **Test: HTF/LTF-gates (disabled)** → 34 trades (oförändrat)
4. **Test: signal_adaptation ATR-zoner (sänkta)** → **176 trades (+5×), PF 1.31, +4.95%** ✅

### Genombrott-konfiguration

```yaml
signal_adaptation:
  zones:
    low: { entry: 0.25, regime: 0.45 } # från 0.33/0.60-0.70
    mid: { entry: 0.28, regime: 0.50 } # från 0.39/0.60-0.75
    high: { entry: 0.32, regime: 0.55 } # från 0.45/0.60-0.80
```

**Slutresultat med alla optimeringar:**

- **176 trades** (från 34), **PF 1.32** (från 0.92), **Return +8.41%** (från -0.10%)
- Positionsstorlek 3× högre (`risk_map` 0.015–0.045)
- Exit-threshold sänkt till 0.35
- HTF/LTF-gates återaktiverade med `tolerance_atr: 0.60`

### Optuna-problemet upptäckt

Alla Optuna-konfigurationer hade `signal_adaptation` **fixerat till 44–60% högre trösklar** än genombrott-värdena:

- Original Optuna: low 0.36, mid 0.42, high 0.48 (regime 0.60–0.88)
- Genombrott: low 0.25, mid 0.28, high 0.32 (regime 0.45–0.55)

**Konsekvens:** Optuna optimerade allt annat (fib-gates, exits, risk) medan ATR-zonerna garanterade få trades → därför identiska dåliga resultat.

**Åtgärd:** `config/optimizer/tBTCUSD_1h_optuna_smoke_loose.yaml` uppdaterad med 5 grid-varianter runt genombrott-värdena (entry 0.20–0.34, regime 0.38–0.58).

### Bugfix

- `src/core/backtest/engine.py` – fixade exit-konfigladdning från `configs['cfg']['exit']` → `configs['exit']` så att exit-inställningar faktiskt respekteras.

### Filer

- Analys: `docs/optuna/BREAKTHROUGH_CONFIG_20251113.md`
- Optuna-fix: `docs/optuna/OPTUNA_FIX_20251113.md`
- Konfig: `config/tmp/tmp_user_test.json`
- Backtest: `results/backtests/tBTCUSD_1h_20251113_163809.json`
- Uppdaterad Optuna: `config/optimizer/tBTCUSD_1h_optuna_smoke_loose.yaml`

### Nyckelinsikter

1. **signal_adaptation ATR-zoner är den primära entry-kontrollen** – toppnivå-trösklar används inte när zoner är definierade
2. **Systematisk isoleringstestning är kritisk** – ändra en parameter i taget för att identifiera verkliga flaskhalsar
3. **Optuna kan optimera fel sökrymd** – verifiera alltid att kritiska parametrar inte är fixerade till suboptimala värden
4. **Exit-konfigladdning måste vara korrekt** – bug i engine.py gjorde att exit-inställningar ignorerades

### Nästa steg

- Köra smoke test med max_concurrent=1 för att verifiera olika parametrar ger olika resultat
- Fixa cache thread-safety för att aktivera max_concurrent>1 (ytterligare 2x från parallellism)
- Vectorize Fibonacci swing detection för 1.5x speedup (totalt 30x)
- Kör full Proxy Optuna (50-80 trials, 6-9 månader) för PF > 1.25
- Walk-forward-validering med rullande fönster
