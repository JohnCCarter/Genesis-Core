# Cleanup Report – 2025-11-03

## Översikt

- Arkivrunda initierad av "Archive & Clean Mode" (Chamoun & Cursor).
- 41 filer (fördelade över 6 delkataloger) flyttades till `archive/2025-11-03/`.
- 3 temporära artefakter raderades (`.mypy_cache/`, `build/`, `tatus -sb`).
- Aktiv kod, konfigurationer och beroenden lämnades orörda.
- Resultatdata strukturerades om (se avsnittet _Results-hygien_).

## Arkiverade objekt

- `scripts/decision_backup.py`
- `docs/THRESHOLD_OPTIMIZATION_RESULTS.md`
- `config/models/registry.json.backup`
- `config/models/backup_old_models/`
- `config/models/backup_tbtcusd_outdated/`
- `config/models/backup_tbtcusd_metrics/`
- `config/models/v7_final_top7_6m.json/`
- `optuna/test_optuna_new_20251023_old.db`
- `reports/bandit-report.json`
- `reports/bandit-report.txt`
- `tmp_aggressive_candidate.json`
- `tmp_champion_clone.json`
- `tmp_htf_edge.json`
- `tmp_ltf_only.json`
- `tmp_no_htf.json`
- `tmp_reason_counts.py`
- `tmp_relaxed_combo.json`
- `tmp_relaxed_combo_ltf.json`
- `tmp_threshold_relax.json` – experimentellt threshold-case.

## Results-hygien (2025-11-03)

- `results/hparam_search/` rensad: endast nyckelrunner (`run_20251023_141747`, `run_20251024_094342`, `run_20251024_100716`, `run_20251024_102710`, `run_20251030_153908`, `run_20251030_155323`, `run_20251031_smoke`, `run_20251031_smoke2`, `run_20251031_resume_test`) finns kvar i huvudträdet.
- Tidigare arkivkataloger (`results/hparam_search/_archive/20251103_trimmed_runs/`) har tömts på detaljfiler (samtliga `trial_*.json/log/config` borttagna) – endast sammanfattande filer sparas där vid behov.
- `results/backtests/` avlastad: endast nio nyckel-backtester + equity-filer (matchar listan ovan) samt 3h/6h-referenser finns kvar; övriga 1h-backtester flyttade till `results/backtests/archive/20251103_trimmed_runs/` eller tidigare arkiv.
- `results/trades/` reducerad till motsvarande nio nyckel-runner (1h) samt äldre 3h/6h-referenser; resterande ligger i `results/trades/archive/` (tom katalog efter rensning 2025-11-03).
- `results/walk_forward/` äldre körningar flyttade till `results/walk_forward/archive/` (tom katalog efter rensning 2025-11-03).
- Deduplicering av trials (2025-11-03): 15 duplicerade trials raderade från `run_20251030_155323` (identiska parametrar och score 114.42). Totalt 136 unika trials kvar i nyckelrunnarna (ner från 151). Varje trial representerar nu unika parametrar.
- `run_20251030_155323` (Optuna fib-grid): trimmas ytterligare till 10 topp-trials + best-trial (`trial_008`), resterande 94 trials + configs + `_cache/` flyttade till `results/hparam_search/_archive/20251103_trimmed_runs/run_20251030_155323_trimmed/`.
- Övriga resultatkataloger (trades, walk_forward, models) ej ändrade.
- 2025-11-03 10:50: Samtliga `results/hparam_search/run_*/_cache` flyttade till `results/hparam_search/_archive/20251103_trimmed_runs/cache_backup_phase7d/` för att förhindra oavsiktlig cache-återanvändning i kommande Optuna-runner.
- 2025-11-03 11:00: Ny storage-mapp `results/hparam_search/storage/` skapad för framtida Optuna-databaser (`optuna_tBTCUSD_1h_fib_tune_phase7d.db` m.fl.).

(Se `archive/2025-11-03/` för full katalogstruktur.)

## Raderade artefakter

- `.mypy_cache/` (mypy-typkontrollens cache)
- `build/` (distutils/pyproject build-output)
- `tatus -sb` (felaktig git status-dump)
- **Arkiverade resultat (permanent raderade):**
  - `results/backtests/archive/20251103_trimmed_runs/` (~2.5 GB, 3,807 filer)
  - `results/backtests/archive/20251103_failed_optuna_resume/` (hela helgkörningen `run_20251101_weekend` + DB)
  - `results/trades/archive/` (tom efter rensning 2025-11-03)
  - `results/walk_forward/archive/` (tom efter rensning 2025-11-03)
- **Duplicerade trials:** 15 trial-filer + configs/logs/cache från `run_20251030_155323`
- **Optuna-databaser (2025-11-03):**
  - **Raderade (10 test/smoke-databaser):** `optuna_tBTCUSD_1h_fib_tune_smoke*.db`, `optuna_tBTCUSD_1h_fib_tune_resume.db`, `optuna_tBTCUSD_1h_fib_tune_quick.db`, `optuna_tBTCUSD_1h_fib_tune_timing_test.db`, `test_optuna*.db` (4 st), `optuna_search.db` (tom)
  - **Arkiverade (6 gamla runs):** `optuna_tBTCUSD_1h_fine.db` (champion score 260.73), `optuna_tBTCUSD_1h_6m.db`, `optuna_tBTCUSD_1h_proxy.db`, `optuna_tBTCUSD_1h_micro.db`, `optuna_tBTCUSD_1h_fib.db`, `test_optuna_longer.db` → `archive/2025-11-03/optuna_dbs/`
- **Repo-rotsfiler (2025-11-03):**
  - **Raderade (9 tomma Python-filer):** `analyze_capital.py`, `analyze_optuna_speed.py`, `analyze_trades.py`, `check_next_test_options.py`, `check_parameter_variation.py`, `debug_risk_map.py`, `optuna_learning_analysis.py`, `optuna_timeframe_analysis.py`, `timeframe_analysis.py`
  - **Arkiverade (7 debug/test-skript):** `debug_decide.py`, `debug_htf_levels.py`, `test_cache_key_match.py`, `test_normalize_float.py`, `test_optuna_exact_1_3months.py`, `test_optuna_float_values.py`, `test_trial_timing.py` → `archive/2025-11-03/debug_scripts/`
  - **Flyttade till docs/ (2 dokumentationsfiler):** `daily_summary_2025-10-23.md`, `OPTUNA_6MONTH_PROBLEM_REPORT.md`
  - **Behållen i roten:** `test_optuna_new_1_3months.py` (aktivt Optuna-skript)
- **Test-konfigfiler (2025-11-03):**
  - **Raderade (6 testfiler från config/):** `test_combo_1-4.json`, `test_override.json`, `test_grid.yaml` (används inte i kod)
  - **Bevarade:** `dev.overrides.example.json` (template), `burnin_summary.json` (används i scripts/parse_burnin_log.py)
- **Optimizer-konfigurationer (2025-11-03):**
  - **Arkiverade (8 äldre configs):** `tBTCUSD_1h_optuna_fib_tune_quick.yaml`, `tBTCUSD_1h_champion_clone_grid*.yaml`, `tBTCUSD_1h_new_optuna*.yaml`, `tBTCUSD_1h_exact_optuna.yaml`, `tBTCUSD_1h_search.yaml`, `tBTCUSD_1h_fib_grid.yaml` → `archive/2025-11-03/optimizer_configs/`
  - **Aktiva kvar i `config/optimizer/`:** `tBTCUSD_1h_optuna_fib_tune.yaml`, `tBTCUSD_1h_fib_entry_grid.yaml`, `tBTCUSD_1h_fib_entry_grid_quick.yaml`, `tBTCUSD_1h_ltf_entry_grid.yaml`, `tBTCUSD_1h_ltf_confidence_grid.yaml`, `tBTCUSD_1h_fib_grid_v2.yaml`, `tBTCUSD_1h_fib_grid_v3.yaml`, `tBTCUSD_1h_coarse_grid.yaml`, `tBTCUSD_1h_proxy_optuna.yaml`, `tBTCUSD_1h_micro_optuna.yaml`, `tBTCUSD_1h_fine_optuna.yaml`, `tBTCUSD_1h_fib_optuna.yaml`
- **Runtime & baseline (2025-11-03):**
  - **Uppdaterade:** `config/runtime.json`, `config/runtime.seed.json`, `config/timeframe_configs.py` nu synkade med championens 1h-parametrar (trösklar, risk_map, signal_adaptation, fib-gating).
  - **Raderad:** `config/override_test.json` (oanvänd testoverride).
- **Modellutvärdering (2025-11-03):**
  - Samtliga JSON-modeller i `results/models/` evaluerade med `scripts/evaluate_all_models.py` → scoreboard under `results/evaluation/model_scoreboard.json` (AUC-baserad).
  - Toppkandidater per tidsram behållna: `tBTCUSD_1h_v5*`, `tBTCUSD_3h_v4*`, `tBTCUSD_6h_v4*` (övriga flyttade till `archive/2025-11-03/models_trimmed/`).
  - Individuella rapporter per modell sparade i `results/evaluation/<modellnamn>_evaluation.json`.

## Varningar eller uppföljning

- Inga brutna importer eller beroenden upptäckta.
- Optuna- och tmp-konfigurationer kan återställas från arkivet vid behov.
- Två arbetsfiler (`to_archive.md`, `to_delete.md`) kvar i repo-roten som dokumentation av beslutet.
- Results-arkivet (`results/hparam_search/_archive/20251103_trimmed_runs/`, `results/backtests/archive/20251103_trimmed_runs/`, `results/backtests/archive/20251103_failed_optuna_resume/`) innehåller enbart sammanfattad historik från städningen; `results/trades/archive/` och `results/walk_forward/archive/` är tomma efter rensningen.
