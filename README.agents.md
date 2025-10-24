# README for AI Agents (Local Development)
_Last update: 2025-10-23_

This document explains the current workflow for Genesis-Core, highlights today's deliverables, and lists the next tasks for the hand-off.

## 1. Deliverables on 23 Oct 2025
- Added result caching in `src/core/optimizer/runner.py` (`results/hparam_search/<run>/_cache/<hash>.json`) to skip duplicate backtests.
- Introduced a three-step optimisation pipeline:
  1. `config/optimizer/tBTCUSD_1h_coarse_grid.yaml` - coarse sweep (27 combinations).
  2. `config/optimizer/tBTCUSD_1h_proxy_optuna.yaml` - 2-month Optuna run with Hyperband for fast feedback.
  3. `config/optimizer/tBTCUSD_1h_fine_optuna.yaml` - 6-month fine-tuning around the winning region.
- New summary helper: `python -m scripts.summarize_hparam_results --run-dir <results/hparam_search/run_...>`.
- Winning configuration (trial_002, run_20251023_141747):
  - `entry_conf_overall = 0.35`
  - `regime_proba.balanced = 0.70`
  - `risk_map = [[0.45, 0.015], [0.55, 0.025], [0.65, 0.035]]`
  - `exit_conf_threshold = 0.40`, `max_hold_bars = 20`
  - Backtest: `results/backtests/tBTCUSD_1h_20251023_162506.json` -> net +10.43 %, PF 3.30, 75 trades.

## 2. Optimisation workflow (coarse -> proxy -> fine)
1. Run coarse sweep: `python -m core.optimizer.runner config/optimizer/tBTCUSD_1h_coarse_grid.yaml`.
2. Run proxy Optuna: `python test_optuna_new_1_3months.py --config config/optimizer/tBTCUSD_1h_proxy_optuna.yaml` (study `optuna_tBTCUSD_1h_proxy.db` resumes automatically).
3. Run fine Optuna: `python test_optuna_new_1_3months.py --config config/optimizer/tBTCUSD_1h_fine_optuna.yaml`.
4. Summarise each run with `scripts/summarize_hparam_results`.
5. If required, run the full 6-month config `config/optimizer/tBTCUSD_1h_new_optuna.yaml` for validation.
6. Check the `_cache` directory before launching new backtests to reuse existing results.

### Quick commands
```powershell
python -m scripts.summarize_hparam_results --run-dir results/hparam_search/run_YYYYMMDD_HHMMSS
python test_optuna_new_1_3months.py --config config/optimizer/tBTCUSD_1h_proxy_optuna.yaml
python test_optuna_new_1_3months.py --config config/optimizer/tBTCUSD_1h_fine_optuna.yaml
```

## 3. Champion candidate to verify next
| Parameter | Value |
|-----------|-------|
| `entry_conf_overall` | 0.35 |
| `regime_proba.balanced` | 0.70 |
| `risk_map` | `[[0.45, 0.015], [0.55, 0.025], [0.65, 0.035]]` |
| `exit_conf_threshold` | 0.40 |
| `max_hold_bars` | 20 |

- Source: `results/hparam_search/run_20251023_141747/trial_002.json`.
- The next agent should update `config/strategy/champions/tBTCUSD_1h.json` after sanity checks.
- The proxy winner (`results/backtests/tBTCUSD_1h_20251023_152720.json`) remains a reference (net +8.98 %, PF 3.03).

## 4. Next steps (to continue tomorrow)
1. Promote the winning configuration to champion and update the runtime config.
2. Consider micro-tuning (even tighter ranges or additional parameters such as Fibonacci controls).
3. Automate the entire coarse -> proxy -> fine flow and plan for early-stopping support.
4. Update `docs/optimizer.md` once the champion is changed.
5. Plan which feature or exit parameters should be exposed for future autotune iterations.

## 5. Recent history (Phase-7a/7b, 21 Oct 2025)
- Locked snapshot: `tBTCUSD_1h_2024-10-22_2025-10-01_v1`.
- Baseline backtest recorded (`results/backtests/tBTCUSD_1h_20251020_155245.json`).
- Runner enhancements: resume/skip, metadata, concurrency, retries.
- ChampionManager & ChampionLoader integrated into pipeline/backtest flows.
- Walk-forward runs (`wf_tBTCUSD_1h_20251021_090446`, ATR zone tweak `wf_tBTCUSD_1h_20251021_094334`).
- Optuna integration (median pruner), CLI summary (`scripts/optimizer.py summarize --top N`), documentation in `docs/optimizer.md` and `docs/TODO.md`.
- Exit improvement plan documented in `docs/FIBONACCI_FRAKTAL_EXITS_IMPLEMENTATION_PLAN.md`.

## 6. Deployment and operations
- Designed for single-user operation; secrets live in `.env`.
- Production deployment: personal VPS or equivalent.
- Champion configs in `config/strategy/champions/`, loaded by `ChampionLoader`.

## 7. Agent rules
- Keep `core/strategy/*` deterministic and side-effect free.
- Do not log secrets; use `core.utils.logging_redaction` if needed.
- Pause when uncertain and verify with tests.
- Add unit tests for new logic; target < 20 ms per module.
- Use `metrics` only in orchestration (`core/strategy/evaluate.py`).
- Respect cached results and always save backtests under `results/backtests/`.

## 8. Setup (Windows PowerShell)
```powershell
python -m venv .venv
. .\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -e .[dev,ml]
```

## 9. Quick start and key references
- Feature pipeline: `src/core/strategy/features_asof.py`, `scripts/precompute_features_v17.py`.
- Backtesting: `scripts/run_backtest.py --symbol tBTCUSD --timeframe 1h --capital 10000`.
- Model training: `scripts/train_model.py` (see `docs/FEATURE_COMPUTATION_MODES.md`).
- Indicator reference: `docs/INDICATORS_REFERENCE.md`.
- Exit logic: `docs/EXIT_LOGIC_IMPLEMENTATION.md`.
- Validation checklist: `docs/VALIDATION_CHECKLIST.md`.
- Next exits phase (Fibonacci): `docs/FIBONACCI_FRAKTAL_EXITS_IMPLEMENTATION_PLAN.md`.
- Model cache reset: `curl -X POST http://127.0.0.1:8000/models/reload` after retraining.

---

> **Remember:** follow the _coarse -> proxy -> fine_ flow, leverage the cache, and log outcomes in `docs/daily_summary_YYYY-MM-DD.md`. The next agent starts by promoting the winner and updating the documentation.


```powershell
python -m venv .venv
. .\.venv\Scripts\Activate.ps1
pip install -e .[dev]
uvicorn core.server:app --reload --app-dir src
