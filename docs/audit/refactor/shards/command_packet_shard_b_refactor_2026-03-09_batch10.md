# COMMAND PACKET

- **Mode:** `RESEARCH` — source: branch `feature/refactor-tests-structure-b` via `docs/governance_mode.md` branch mapping
- **Risk:** `LOW` — why: tests/docs-only structural refactor, no production code edits
- **Required Path:** `Full` (explicit selector evidence retained)
- **Objective:** Continue Shard B maintainability refactor by deduplicating repeated patch scaffolding for optimizer runner tests while preserving assertion parity.
- **Candidate:**
  - Extract helper for repeated `patch("core.optimizer.runner.expand_parameters", return_value=...)`.
  - Extract helper for repeated `patch("core.optimizer.runner.ChampionManager")`.
  - Replace repeated call-sites in the three champion-related tests only.
- **Base SHA:** `4adce45c`

## Skill Usage

- `repo_clean_refactor` (repo-local SPEC): scope lock, no-behavior-change, minimal reversible diffs.
- `python_engineering` (repo-local SPEC): pytest/ruff-first validation and Python quality constraints.

## Scope

- **Scope IN:**
  - `tests/test_optimizer_runner.py`
  - `docs/audit/refactor/command_packet_shard_b_refactor_2026-03-09_batch10.md`
- **Scope OUT:**
  - all non-test paths except listed governance artifact under `docs/audit/refactor/`
  - all other test files
- **Expected changed files:**
  - `tests/test_optimizer_runner.py`
  - `docs/audit/refactor/command_packet_shard_b_refactor_2026-03-09_batch10.md`
- **Max files touched:** `2`

## Gates required

- `python -m pre_commit run --all-files`
- `python -m ruff check .`
- `python -m pytest tests/test_optimizer_runner.py -q`
- Selectors (mode-required):
  - determinism replay
  - feature cache invariance
  - pipeline hash/invariant guard
  - smoke test

### Selector mapping (explicit)

- determinism replay: `tests/test_backtest_determinism_smoke.py`,
  `tests/test_config_authority_path_determinism.py`
- feature cache invariance: `tests/test_feature_cache.py`,
  `tests/utils/diffing/test_feature_cache.py`
- pipeline hash/invariant guard: `tests/test_backtest_hook_invariants.py`,
  `tests/test_pipeline_fast_hash_guard.py`
- smoke test: `tests/test_import_smoke_backtest_optuna.py`

## Stop Conditions

- Scope drift beyond listed files
- Any behavior/assertion parity drift
- Determinism, feature cache, pipeline invariant, or smoke regression
- Forbidden paths touched

## Output required

- **Implementation Report**
- **PR evidence template**

## Pre-code governance review

- **Opus verdict:** `APPROVED`
- **Notes applied:** refaktor begränsad till helper extraction + call-site replacement i tre champion-relaterade tester.

## Implementation summary (batch10)

- Added helper: `_expand_parameters_patch(values)`
- Added helper: `_champion_manager_patch()`
- Replaced repeated inline `patch("core.optimizer.runner.expand_parameters", ...)` and
  `patch("core.optimizer.runner.ChampionManager")` in:
  - `test_run_optimizer_updates_champion`
  - `test_run_optimizer_validation_stage_promotes_validation_best`
  - `test_run_optimizer_promotion_negative_cases_do_not_write_champion`
- Scope hygiene enforced: transient `scripts/build/__pycache__/` removed before post-audit.

## Gate evidence

- `python -m pytest tests/test_optimizer_runner.py -q` → **PASS** (`19 passed`)
  - Note: first attempt had transient Windows file-lock `PermissionError` in `test_run_optimizer_optuna_strategy`; rerun after cleaning `results/hparam_search/run_optuna/` passed.
- `python -m pre_commit run --all-files` → **PASS**
- `python -m ruff check .` → **PASS**
- determinism replay selectors → **PASS** (`5 passed`)
- feature cache invariance selectors → **PASS** (`9 passed`)
- pipeline invariant selectors → **PASS** (`4 passed`)
- smoke selector (`tests/test_import_smoke_backtest_optuna.py`) → **PASS** (`1 passed`)
- `python scripts/run_skill.py --skill repo_clean_refactor --manifest dev` → **STOP/no_steps** (expected SPEC-skill behavior)
- `python scripts/run_skill.py --skill python_engineering --manifest dev` → **STOP/no_steps** (expected SPEC-skill behavior)

## Scope check before post-audit

- Changed files in scope:
  - `tests/test_optimizer_runner.py`
  - `docs/audit/refactor/command_packet_shard_b_refactor_2026-03-09_batch10.md`
- Out-of-scope drift: none (transient `__pycache__` removed).

## Post-code governance audit

- **Opus verdict:** `APPROVED_WITH_NOTES`
- **Note addressed:** final scope-freshness check executed immediately before commit; scope remained restricted to the two Scope IN files.
