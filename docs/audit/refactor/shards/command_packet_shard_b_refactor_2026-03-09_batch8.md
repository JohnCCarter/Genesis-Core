# COMMAND PACKET

- **Mode:** `RESEARCH` — source: branch `feature/refactor-tests-structure-b` via `docs/governance_mode.md` branch mapping
- **Risk:** `LOW` — why: tests/docs-only structural refactor, no production code edits
- **Required Path:** `Full` (explicit selector evidence retained)
- **Objective:** Continue Shard B maintainability refactor by deduplicating repeated side-effect patch scaffolding in optimizer runner tests while preserving assertion parity.
- **Candidate:**
  - Extract helper for repeated `patch("core.optimizer.runner.run_trial", side_effect=...)`.
  - Extract helper for repeated `patch("core.optimizer.runner._ensure_run_metadata", side_effect=...)`.
- **Base SHA:** `749da6e8`

## Skill Usage

- `repo_clean_refactor` (repo-local SPEC): scope lock, no-behavior-change, minimal reversible diffs.
- `python_engineering` (repo-local SPEC): pytest/ruff-first validation and Python quality constraints.

## Scope

- **Scope IN:**
  - `tests/test_optimizer_runner.py`
  - `docs/audit/refactor/command_packet_shard_b_refactor_2026-03-09_batch8.md`
- **Scope OUT:**
  - all non-test paths except listed governance artifact under `docs/audit/refactor/`
  - all other test files
- **Expected changed files:**
  - `tests/test_optimizer_runner.py`
  - `docs/audit/refactor/command_packet_shard_b_refactor_2026-03-09_batch8.md`
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
- **Notes applied:** dedupe begränsad till test-helper extraction och call-site replacement utan assertions-/beteendeförändring.

## Implementation summary (batch8)

- Added helper: `_run_trial_side_effect_patch(side_effect)`
- Added helper: `_ensure_run_metadata_side_effect_patch(side_effect)`
- Replaced repeated inline `patch(..., side_effect=...)` call-sites with these helpers.
- Scope hygiene enforced: removed transient `scripts/build/__pycache__/` before post-audit.

## Gate evidence

- `python -m pytest tests/test_optimizer_runner.py -q` → **PASS** (`19 passed`)
- `python -m pre_commit run --all-files` → **PASS**
- `python -m ruff check .` → **PASS**
- determinism replay selectors → **PASS** (`5 passed`)
- feature cache invariance selectors → **PASS** (`9 passed`)
- pipeline invariant selectors → **PASS** (`4 passed`)
- smoke selector (`tests/test_import_smoke_backtest_optuna.py`) → **PASS** (`1 passed`)

## Scope check before post-audit

- Changed files in scope:
  - `tests/test_optimizer_runner.py`
  - `docs/audit/refactor/command_packet_shard_b_refactor_2026-03-09_batch8.md`
- Out-of-scope drift: none (transient `__pycache__` removed).

## Post-code governance audit

- **Opus verdict:** `APPROVED_WITH_NOTES`
- **Note addressed:** gate-evidence revalidated in current session (same required gate stack), scope remained locked to the two Scope IN files.
