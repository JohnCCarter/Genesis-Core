# Optimizer Runner & Reporting (Phase 7)

_Last updated: 2025-12-16_

## 1. Overview

Phase 7 extends the optimiser so that we can iterate from a coarse search to a fine-grained Optuna study and capture the best configuration as a champion.

Key components:

- `src/core/optimizer/runner.py` - expands the search space, executes backtests, calculates scores/constraints and now caches completed trials under `results/hparam_search/<run>/_cache/`.
- `scripts/run_backtest.py` - executes individual backtests.
- `config/optimizer/*.yaml` - defines the search space (grid or Optuna).
- `config/strategy/champions/*.json` - stores the active champion (updated today with the fine Optuna winner).
- `scripts/summarize_hparam_results.py` / `scripts/optimizer.py summarize` - quick summaries of run results.
- `ChampionManager` & `ChampionLoader` - persist and reload champions for pipeline/backtest.

## 2. Recommended workflow (coarse -> proxy -> fine)

1. **Coarse grid** - run `config/optimizer/tBTCUSD_1h_coarse_grid.yaml` to map the region:

   ```powershell
   python -m core.optimizer.runner config/optimizer/tBTCUSD_1h_coarse_grid.yaml
   ```

2. **Proxy Optuna (fast)** - 2 month window with Hyperband:

   ```powershell
   python test_optuna_new_1_3months.py --config config/optimizer/tBTCUSD_1h_proxy_optuna.yaml
   ```

   Study file: `optuna_tBTCUSD_1h_proxy.db` (resumable).

3. **Fine Optuna (full 6 months)** - narrow bounds around the proxy winners:

   ```powershell
   python test_optuna_new_1_3months.py --config config/optimizer/tBTCUSD_1h_fine_optuna.yaml
   ```

   Study file: `optuna_tBTCUSD_1h_fine.db`.

4. **Summaries** - after each run:

   ```powershell
   python -m scripts.summarize_hparam_results --run-dir results/hparam_search/<run_id>
   # or
   python scripts/optimizer.py summarize <run_id> --top 5
   ```

5. **Config-equivalence proof (rekommenderas)** - verifiera att trial-config och backtest-resultat använder samma effective config:

```powershell
python scripts/check_trial_config_equivalence.py --run-dir results/hparam_search/<run_id> --all
```

Förväntat utfall är `[OK]` per trial. Om `[MISMATCH]`: stoppa och felsök innan fler trials körs.

6. **Full validation** (optional) - confirm the best candidate with the original 6-month config: `config/optimizer/tBTCUSD_1h_new_optuna.yaml` (`optuna_tBTCUSD_1h_6m.db`).
7. **Champion update** - promote the best trial by updating `config/strategy/champions/<symbol>_<tf>.json`.
8. **Document** - record the results in `docs/daily_summaries/daily_summary_YYYY-MM-DD.md` and this file.

## 3. Latest champion (23 Oct 2025)

Champion file: `config/strategy/champions/tBTCUSD_1h.json`

- Source run: `run_20251023_141747`, trial `trial_002`.
- Parameters:
  - `thresholds.entry_conf_overall = 0.35`
  - `thresholds.regime_proba.balanced = 0.70` (other regimes unchanged)
  - `risk_map = [[0.45, 0.015], [0.55, 0.025], [0.65, 0.035]]`
  - `exit_conf_threshold = 0.40`, `max_hold_bars = 20`
- Backtest: `results/backtests/tBTCUSD_1h_20251023_162506.json` -> net +10.43 %, PF 3.30, 75 trades.
- Metadata fields in the champion reference the trial log, config and run meta.

## 4. Result caching

- Every unique parameter set is hashed and stored in `_cache/<hash>.json`. If the same parameters are requested again the cached payload is returned and the backtest is skipped.
- Cached payloads live inside each run directory (e.g. `results/hparam_search/run_20251023_141747/_cache/`).
- The cache entry contains score, metrics and paths so it can be reused by rerunning the optimiser.

## 5. CLI usage (`scripts/optimizer.py`)

- `summarize <run_id> [--top N]` - prints meta, counts, total durations, best trial and top N trials without opening files manually.

Example:

```bash
python scripts/optimizer.py summarize run_20251023_141747 --top 5
```

## 6. Test coverage

- `tests/test_optimizer_runner.py` - runner integrations, champion writes, cache.
- `tests/test_optimizer_cli.py` - CLI summariser.
- `tests/test_champion_loader.py` - champion fallback/auto-reload.
- `tests/test_evaluate_pipeline.py` - ensures champion metadata is injected into pipeline meta.

## 7. Action items for next agent

1. Monitor performance of the new champion; roll back if unexpected behaviour is observed.
2. Decide on micro-tuning (very tight ranges or additional parameters - e.g. Fibonacci).
3. Build automation for the coarse -> proxy -> fine sequence (shell or Python helper).
4. Plan feature/exit parameters to expose for future autotuning.
5. Consider adding early-stop support (stop a backtest early when constraints already fail).

## 8. Phase 7d updates (2025-11-10)

### Scoring & Constraints

- Score beräknas nu robust från trades/equity via `core.backtest.metrics.calculate_metrics` (PF/DD hämtas inte längre naivt från `summary`).
- `return_to_dd` skyddas mot noll‑DD.
- Constraints separerade från scoringens “hard_failures”. I `config/optimizer/*.yaml` styrs detta via:

  ```yaml
  constraints:
    min_trades: 3
    min_profit_factor: 0.8
    max_max_dd: 0.35
    include_scoring_failures: false
  ```

  Sätt `include_scoring_failures: true` om du vill att scoringens hårda fel (t.ex. trades<10) även ska räknas som constraints‑skäl.

### YAML‑schema (bladnoder MÅSTE ha type)

- Bladparametrar kräver `type: fixed|grid|float|int|loguniform`. Annars tolkas `value/values` som undernoder och ger fel (t.ex. “'float' object has no attribute get”).
- Exempel:

  ```yaml
  thresholds:
    entry_conf_overall:
      type: float
      low: 0.25
      high: 0.65
      step: 0.025
  htf_exit_config:
    trail_atr_multiplier:
      type: float
      low: 1.7
      high: 2.8
      step: 0.05
    enable_trailing:
      type: fixed
      value: true
  ```

### Performance‑flaggor och determinism

- Miljövariabler för snabbkörning:
  - `GENESIS_FAST_WINDOW=1` aktiverar NumPy‑views och minskar overhead.
  - `GENESIS_PRECOMPUTE_FEATURES=1` använder förberäknade features (EMA50, swing points).
  - `GENESIS_MAX_CONCURRENT` kan överskrida `max_concurrent` i YAML för snabba experiment.
  - `GENESIS_RANDOM_SEED=42` sätts automatiskt i runnern om inte redan satt för determinism.
- Optuna‑sampler:
  - TPE med `constant_liar: true`, `multivariate: true`, `n_ei_candidates: 128–512` minskar dubbletter och förbättrar utforskning.

### Vanliga fel och lösningar

- “values/problem” i YAML: lägg till `type` på bladnoder (se ovan).
- `DuplicatedStudyError`: använd unika `study_name`/`storage` (t.ex. tidsstämpel) eller `resume: true`.
- "Optuna resume blocked: study signature mismatch": du försöker återuppta fel studie/DB eller så har config/kod/runtime/mode-flaggor drivit.
  Åtgärd: använd nytt `study_name` och/eller ny `storage` (eller verifiera att du pekar på rätt DB). För legacy-studier kan du backfilla
  `genesis_resume_signature` via `GENESIS_BACKFILL_STUDY_SIGNATURE=1`.
- 0 trades / långsam utforskning: bredda sökrymden för entry/toleranser/override (se `tBTCUSD_1h_optuna_fib_tune.yaml`), sänk constraints vid behov för tidig signaljakt.
