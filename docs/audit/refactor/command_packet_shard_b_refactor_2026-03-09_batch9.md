# COMMAND PACKET

- **Mode:** `RESEARCH` — source: branch `feature/refactor-tests-structure-b` via `docs/governance_mode.md` branch mapping
- **Risk:** `LOW` — why: tests/docs-only structural refactor, no production code edits
- **Required Path:** `Full` (explicit selector evidence retained)
- **Objective:** Continue Shard B maintainability refactor by deduplicating repeated run-trial patch scaffolding in optimizer runner tests while preserving assertion parity.
- **Candidate:**
  - Extract helper for repeated `patch("core.optimizer.runner._get_default_config", return_value={})`.
  - Extract helper for repeated `patch("core.optimizer.runner._get_default_runtime_version", return_value=1)`.
  - Extract helper for repeated `patch("core.optimizer.runner._run_backtest_direct", side_effect=...)`.
- **Base SHA:** `e865c755`

## Skill Usage

- `repo_clean_refactor` (repo-local SPEC): scope lock, no-behavior-change, minimal reversible diffs.
- `python_engineering` (repo-local SPEC): pytest/ruff-first validation and Python quality constraints.

## Scope

- **Scope IN:**
  - `tests/test_optimizer_runner.py`
  - `docs/audit/refactor/command_packet_shard_b_refactor_2026-03-09_batch9.md`
- **Scope OUT:**
  - all non-test paths except listed governance artifact under `docs/audit/refactor/`
  - all other test files
- **Expected changed files:**
  - `tests/test_optimizer_runner.py`
  - `docs/audit/refactor/command_packet_shard_b_refactor_2026-03-09_batch9.md`
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
- **Notes applied:** dedupe hålls strikt till patch-helper extraction och call-site replacement i testfilen.

## Implementation summary (batch9)

- Added helper: `_default_config_patch()`
- Added helper: `_default_runtime_version_patch()`
- Added helper: `_run_backtest_direct_side_effect_patch(side_effect)`
- Replaced repeated inline patch call-sites in two `run_trial`-fokuserade tester.
- Scope hygiene enforced: transient `scripts/build/__pycache__/` removed before post-audit.

## Gate evidence

- `python -m pytest tests/test_optimizer_runner.py -q` → **PASS** (`19 passed`)
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
  - `docs/audit/refactor/command_packet_shard_b_refactor_2026-03-09_batch9.md`
- Out-of-scope drift: none (transient `__pycache__` removed).

## Post-code governance audit

- **Opus verdict:** `APPROVED_WITH_NOTES`
- **Note addressed:** raw gate outputs captured in current session (targeted pytest, pre-commit, ruff, selectors + smoke); scope re-checked and kept to the two Scope IN files.
