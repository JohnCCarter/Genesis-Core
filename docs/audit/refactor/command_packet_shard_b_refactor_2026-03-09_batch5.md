# COMMAND PACKET

- **Mode:** `RESEARCH` — source: branch `feature/refactor-tests-structure-b` via `docs/governance_mode.md` branch mapping
- **Risk:** `LOW` — why: tests/docs-only structural refactor, no production code edits
- **Required Path:** `Full` (explicit selector evidence retained)
- **Objective:** Continue Shard B maintainability refactor by deduplicating repeated environment setup and parameter-grid scaffolding in optimizer runner tests while preserving assertion parity.
- **Candidate:**
  - Extract helper(s) for repeated score-version env setup (`GENESIS_SCORE_VERSION` + paired `delenv` calls).
  - Extract helper for repeated entry-confidence parameter grid list (`[_entry_conf_params(0.4), _entry_conf_params(0.5)]`).
- **Base SHA:** `09d1ece0`

## Skill Usage

- `repo_clean_refactor` (repo-local SPEC): scope lock, no-behavior-change, minimal reversible diffs.
- `python_engineering` (repo-local SPEC): pytest/ruff-first validation and Python quality constraints.

## Scope

- **Scope IN:**
  - `tests/test_optimizer_runner.py`
  - `docs/audit/refactor/command_packet_shard_b_refactor_2026-03-09_batch5.md`
- **Scope OUT:**
  - all non-test paths except listed governance artifact under `docs/audit/refactor/`
  - all other test files
- **Expected changed files:**
  - `tests/test_optimizer_runner.py`
  - `docs/audit/refactor/command_packet_shard_b_refactor_2026-03-09_batch5.md`
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

## Gate evidence (executed)

Gate evidence below is reported from executed local runs.
Current changed files are constrained to batch5 scope (`tests/test_optimizer_runner.py` + this packet).
Remediation note: out-of-scope `scripts/build/__pycache__/` artifact was removed before post-audit.

- `python -m pre_commit run --all-files` -> PASS
- `python -m ruff check .` -> PASS
- targeted file (`tests/test_optimizer_runner.py`) -> PASS (`19 passed, 0 failed`)
- determinism replay selectors -> PASS (`5 passed, 0 failed`)
  - `tests/test_backtest_determinism_smoke.py`
  - `tests/test_config_authority_path_determinism.py`
- feature cache invariance selectors -> PASS (`9 passed, 0 failed`)
  - `tests/test_feature_cache.py`
  - `tests/utils/diffing/test_feature_cache.py`
- pipeline invariant selectors -> PASS (`4 passed, 0 failed`)
  - `tests/test_backtest_hook_invariants.py`
  - `tests/test_pipeline_fast_hash_guard.py`
- smoke selector -> PASS (`1 passed, 0 failed`)
  - `tests/test_import_smoke_backtest_optuna.py`
