# README for AI Agents (Local Development)
_Last update: 2025-10-24_

This document explains the current workflow for Genesis-Core, highlights today's deliverables, and lists the next tasks for the hand-off.

## 1. Deliverables on 24 Oct 2025
- Added intraday Fibonacci support via `get_ltf_fibonacci_context` in `src/core/indicators/htf_fibonacci.py` (symmetric helper for 1h/30m/6h timeframes).
- `src/core/strategy/features_asof.py` now emits both HTF and LTF Fibonacci context; `evaluate_pipeline` persists ATR/Fibonacci metadata in the decision state.
- Refactored `src/core/strategy/decision.py` to use shared level lookup helpers and optional HTF/LTF entry gates with ATR-based tolerances (debug info persisted in `state_out`).
- Added `config/optimizer/tBTCUSD_1h_fib_grid_v2.yaml` for fast grids over HTF exit parameters (partials/trailing toggles, ATR thresholds).
- Captured the latest grid outcomes under `results/hparam_search/run_20251024_*` with matching backtests in `results/backtests/tBTCUSD_1h_20251024_*.json` (champion is unchanged).

## 2. 24 Oct experiments (Fibonacci focus)
- `run_20251024_094342` (micro sweep without HTF gating): best `trial_001`, score 184.71, +7.39 % net (`results/backtests/tBTCUSD_1h_20251024_115054.json`), PF 4.47 across 62 trades.
- `run_20251024_100716` (HTF exit grid, ATR threshold 0.60-0.75, trailing 2.4-2.8): best `trial_008`, score 190.35, +7.62 % net (`results/backtests/tBTCUSD_1h_20251024_121459.json`), PF 4.59, 62 trades.
- `run_20251024_102710` (partials/trailing variants): best `trial_001`, same metrics as above (`results/backtests/tBTCUSD_1h_20251024_123436.json`).
- None of the new trials beat the reigning champion `run_20251023_141747/trial_002` (score 260.73, +10.43 %, 75 trades). Entry fib gating reduces trade count; calibration is still needed before promoting any new configuration.

## 3. Optimisation workflow (coarse -> proxy -> fine)
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