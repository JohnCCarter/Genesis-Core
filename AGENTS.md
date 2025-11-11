# README for AI Agents (Local Development)

## Last update: 2025-11-11

This document explains the current workflow for Genesis-Core, highlights today's deliverables, and lists the next tasks for the hand-off.

## 1. Deliverables (latest highlights: 2025-11-11)

- Robust scoring: PF/DD från trades/equity via `core.backtest.metrics.calculate_metrics` (inte summary). Skyddat `return_to_dd`.
- `PositionTracker.get_summary()` rapporterar korrekt `profit_factor` (gross_profit/gross_loss) och `max_drawdown` från equity‑kurva.
- Constraints separerade från scoringens “hard_failures” och styrs via YAML (`include_scoring_failures`).
- Determinism: runner sätter `GENESIS_RANDOM_SEED=42` om inte redan satt.
- Performance‑läge: `GENESIS_FAST_WINDOW=1`, `GENESIS_PRECOMPUTE_FEATURES=1` (se `docs/FEATURE_COMPUTATION_MODES.md`).
- YAML‑schema: bladnoder MÅSTE ha `type: fixed|grid|float|int|loguniform` (annars values/value‑fel).
- Optuna-sökrymden breddad: fler kontinuerliga noder (entry/regime/hysteresis/max hold/risk map/HTF+LTF flippar) och `bootstrap_random_trials` (32 RandomSampler-trials sekventiellt) innan TPE.
- Soft constraints returnerar nu `score - 1e3` (tidigare -1e6) för bättre signal till samplern utan att belöna felaktiga försök.

## 2. Snabbguide (Optuna körflöde, uppdaterad)

1) Preflight & Validate

```powershell
python scripts/preflight_optuna_check.py config/optimizer/<config>.yaml
python scripts/validate_optimizer_config.py config/optimizer/<config>.yaml
```

2) Miljö (snabbkörning)

```powershell
$Env:GENESIS_FAST_WINDOW='1'
$Env:GENESIS_PRECOMPUTE_FEATURES='1'
$Env:GENESIS_MAX_CONCURRENT='4'
$Env:GENESIS_RANDOM_SEED='42'
```

> Tip: Ange även `OPTUNA_MAX_DUPLICATE_STREAK=2000` och kontrollera att konfigen har `bootstrap_random_trials` (32–40) för att tvinga fram en deterministisk RandomSampler-uppstartsfas innan TPE tar över.

3) Start

```powershell
python -c "from core.optimizer.runner import run_optimizer; from pathlib import Path; run_optimizer(Path('config/optimizer/<config>.yaml'))"
```

4) Summera

```powershell
python scripts/optimizer.py summarize run_<YYYYMMDD_HHMMSS> --top 10
```

## 3. Optimisation workflow (coarse -> proxy -> fine)

**KRITISKT: Validera ALLTID innan lång körning (>30 min):**

```powershell
python scripts/validate_optimizer_config.py config/optimizer/<config>.yaml
```

Valideringen MÅSTE returnera 0 innan körning. Fixa alla [ERROR]-fel och granska [WARN]-varningar.

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

4. **Optional Fibonacci grid** - warm up HTF exit combinations quickly:

   ```powershell
   python -m core.optimizer.runner config/optimizer/tBTCUSD_1h_fib_grid_v2.yaml
   ```

   Use this before launching long Optuna runs when iterating on fib gating.

5. **Summaries**

   ```powershell
   python -m scripts.summarize_hparam_results --run-dir results/hparam_search/<run_id>
   python scripts/optimizer.py summarize <run_id> --top 5
   ```

6. **Full validation (optional)** - `config/optimizer/tBTCUSD_1h_new_optuna.yaml` (`optuna_tBTCUSD_1h_6m.db`).
7. **Champion update** - update `config/strategy/champions/<symbol>_<tf>.json` once a winner is validated.
8. **Documentation** - log outcomes in `docs/daily_summary_YYYY-MM-DD.md` and this file.

## 4. Champion status (unchanged)

Champion file: `config/strategy/champions/tBTCUSD_1h.json`

- Source run: `run_20251023_141747`, `trial_002`.
- Key parameters: `entry_conf_overall = 0.35`, `regime_proba.balanced = 0.70`, risk map `[[0.45, 0.015], [0.55, 0.025], [0.65, 0.035]]`, `exit_conf_threshold = 0.40`, `max_hold_bars = 20`.
- Exits: HTF fib trailing enabled (`fib_threshold_atr = 0.7`, `trail_atr_multiplier = 2.5`, partials 0.6/0.5).
- Entry fib gates are enabled in the champion config; ensure the runtime state supplies both `htf_fib` and `ltf_fib` metadata before activating in production.
- Backtest reference: `results/backtests/tBTCUSD_1h_20251023_162506.json` -> net +10.43 %, PF 3.30, 75 trades.

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

## 8. Next steps for hand-off (25 Oct 2025)

1. Wire `feats_meta["htf_fibonacci"]` into the decision state (`evaluate_pipeline`) so the new HTF entry gate can operate (currently only `ltf_fib` is forwarded).
2. Tune the fib gates: rerun `config/optimizer/tBTCUSD_1h_fib_grid_v2.yaml` with tighter `fib_threshold_atr` / tolerance ranges and compare against the champion (target >= 260 score).
3. Decide between grid-first vs Optuna-first for fib parameters; if Optuna is chosen, script a warm-start study that seeds the current champion values.
4. Add regression tests around the new decision gates (HTF/LTF) covering missing context, ATR=0, and tolerance handling.
5. Re-run Bandit with the scoped command and capture a clean report for future reference.

## 9. Recent history (Phase-7a/7b, 21 Oct 2025)

- Locked snapshot: `tBTCUSD_1h_2024-10-22_2025-10-01_v1`.
- Baseline backtest: `results/backtests/tBTCUSD_1h_20251020_155245.json`.
- Runner enhancements: resume/skip, metadata, concurrency, retries.
- ChampionManager & ChampionLoader integrated into pipeline/backtest flows.
- Walk-forward runs (`wf_tBTCUSD_1h_20251021_090446`, ATR zone tweak `wf_tBTCUSD_1h_20251021_094334`).
- Optuna integration (median pruner), CLI summary (`scripts/optimizer.py summarize --top N`), documentation in `docs/optimizer.md` and `docs/TODO.md`.
- Exit improvement plan documented in `docs/FIBONACCI_FRAKTAL_EXITS_IMPLEMENTATION_PLAN.md`.

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
- Model training: `scripts/train_model.py` (see `docs/FEATURE_COMPUTATION_MODES.md`).
- Indicator reference: `docs/INDICATORS_REFERENCE.md`.
- Exit logic: `docs/EXIT_LOGIC_IMPLEMENTATION.md`.
- Validation checklist: `docs/VALIDATION_CHECKLIST.md`.
- Next exits phase (Fibonacci): `docs/FIBONACCI_FRAKTAL_EXITS_IMPLEMENTATION_PLAN.md`.
- Model cache reset: `curl -X POST http://127.0.0.1:8000/models/reload` after retraining.

---

> **Kom ihag:** folj flodet _coarse -> proxy -> fine_, utnyttja cache-filerna och dokumentera resultaten i `docs/daily_summary_YYYY-MM-DD.md`. Nasta agent borjar med att aktivera HTF-filtret i beslutslogiken, kalibrera fib-parametrarna och uppdatera dokumentationen darefter.

## 14. Uppdateringar 30 okt 2025

- Upstream-merge lade till `.github/copilot-instructions.md` (kort agentguide), förfinade beslutslogiken (`src/core/strategy/decision.py`, `evaluate.py`) samt indikatorerna (`src/core/indicators/fibonacci.py`, `htf_fibonacci.py`).
- Nya referensdokument: `docs/FIB_GATING_DEBUG_20251027.md`, `docs/RISK_MAP_CONFIDENCE_TUNING.md` – använd dem när fib-toleranser eller riskkartor justeras.
- Temporära JSON-profiler (`tmp_*.json`) och `tmp_reason_counts.py` innehåller kandidatkonfigurationer och statistik från senaste fib-gating-debuggen. Rensa eller migrera värdefulla varianter till `config/` innan de tas bort.
- Champion-filen `config/strategy/champions/tBTCUSD_1h.json` uppdaterades med finjusterade fibparametrar. Stäm av mot nya `state_out`-fält och säkerställ att HTF/LTF-konteksten nu flödar hela vägen från `features_asof` -> `evaluate_pipeline` -> `decision`.
- `cursor-active-rules.mdc` är nedtrimmad (~50 rader) och `AGENTS.md` ersätter tidigare `README.agents.md`; håll båda synkade med de här noteringarna inför nästa handoff.

## 15. Roller för parallella agenter

- **Agent A – Optimering & körningar**
  - Starta `python -m core.optimizer.runner ...` / Optuna-jobb enligt plan (coarse → proxy → fine → fib-grid).
  - Säkerställ att resultaten sparas i `results/hparam_search/run_*` och att `tmp_*`-konfigurationer versioneras vid behov.
  - Meddela resultat-ID, score, trades och nyckelmetriker till Agent B efter varje körning.
- **Agent B – Analys & dokumentation**
  - Jämför inkomna resultat mot champion (`score ≥ 260`), uppdatera `AGENTS.md` + relevanta docs (`docs/FIB_GATING_DEBUG_*.md`, `docs/RISK_MAP_CONFIDENCE_TUNING.md`).
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

1) Bredda sökrymden initialt (fler trades):
   - `thresholds.entry_conf_overall.low: 0.25`
   - `htf_fib.entry.tolerance_atr: 0.20–0.80`
   - `ltf_fib.entry.tolerance_atr: 0.20–0.80`
   - Tillåt `multi_timeframe.allow_ltf_override: true` i grid och sänk `ltf_override_threshold: 0.65–0.85`.
2) Mildra constraints tidigt:
   - `constraints.min_trades: 1–3`, `min_profit_factor: 0.8`, `max_max_dd: 0.35`
   - Låt `include_scoring_failures: false` så scoringens hårda fel inte kortsluter utforskning.
3) Sampler‑inställningar:
   - `tpe` med `constant_liar: true`, `multivariate: true`, höj `n_ei_candidates` (128–512).
   - `OPTUNA_MAX_DUPLICATE_STREAK` högt (t.ex. 2000) så studien inte avbryts för tidigt.
4) Unika `study_name`/`storage` per körning (timestamp) och tom `_cache/` per kampanj.

### Rekommenderad kodförbättring (nästa agent)

1) Straffa duplicat i objective:
   - I `src/core/optimizer/runner.py::_run_optuna.objective`: om payload markerats `skipped` eller `duplicate`, returnera en stor negativ poäng (t.ex. `-1e6`) i stället för `0.0`. Detta bryter TPE‑degenerering mot samma parametrar.
   - Tips: Säkerställ noll‑straff för legitima cache‑träffar endast om du vill återrapportera verklig poäng; för duplicat inom run använd hårt straff.
2) Telemetri/varning:
   - Räkna andel skippade trials; varna om `skipped_ratio > 0.5` (“hög duplicatfrekvens – bredda sökrymden eller sänk constraints”).
3) Pre‑random boost:
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
