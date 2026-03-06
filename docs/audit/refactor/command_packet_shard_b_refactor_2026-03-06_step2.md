# COMMAND PACKET

Historical note: this packet documents the volume-focused step2 subset only.
Current mixed authority/volume increments are governed by
`docs/audit/refactor/command_packet_shard_b_refactor_2026-03-06_batch2.md`.

- **Mode:** `RESEARCH` — source: branch mapping `feature/* -> RESEARCH`
- **Risk:** `LOW` — why: tests-only deduplication via parametrization, no production code edits
- **Required Path:** `Full` (non-trivial low-risk refactor)
- **Path note:** Change shape is quick-path-eligible (2 files, no runtime impact), but Full path is retained intentionally for explicit selector evidence.
- **Objective:** Reduce duplicated empty-input tests in `tests/test_volume.py` with a single parametrized parity test.
- **Candidate:** Consolidate identical `assert <indicator>([]) == []` tests for indicators that accept default params.
- **Base SHA:** `7052a86fc7314198289ccd32be98911f96e09f35`

## Skill Usage

- `repo_clean_refactor` (SPEC): scope lock, no-behavior-change, minimal reversible diffs.
- `python_engineering` (SPEC): pytest/ruff-first validation and Python quality constraints.

## Scope

- **Scope IN:**
  - `tests/test_volume.py`
- **Scope OUT:**
  - all non-test paths except this governance artifact:
    `docs/audit/refactor/command_packet_shard_b_refactor_2026-03-06_step2.md`
  - all other test files for this step
- **Expected changed files:**
  - `tests/test_volume.py`
  - `docs/audit/refactor/command_packet_shard_b_refactor_2026-03-06_step2.md`
- **Max files touched:** `2`

## Gates required

- `pre-commit run --all-files`
- `ruff check .`
- `pytest`
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
- pipeline hash/invariant guard: `tests/test_backtest_hook_invariants.py`
- smoke test: `tests/test_import_smoke_backtest_optuna.py`

## Stop Conditions

- Scope drift beyond `tests/test_volume.py`
- Any behavior or assertion-coverage ambiguity
- Determinism or pipeline invariant regression
- Refactor requires signature changes in production indicator functions
- Any accidental edits to other `test_empty_input` cases in `tests/test_volume.py`

## Output required

- **Implementation Report**
- **PR evidence template**

## Batch2 subset execution note

This step runs under the broader batch2 contract while executing code changes only in
`tests/test_volume.py`. `tests/test_authority_mode_resolver.py` remains unchanged in this
step; batch2 scope remains unchanged at packet level.

## Gate evidence (executed)

- `python -m pre_commit run --all-files` -> PASS
- `python -m ruff check .` -> PASS
- `pytest` -> PASS (`979 passed, 0 failed`)
- Selector suite -> PASS (`15 passed, 0 failed`)
  - determinism replay: `tests/test_backtest_determinism_smoke.py`,
    `tests/test_config_authority_path_determinism.py`
  - feature cache invariance: `tests/test_feature_cache.py`,
    `tests/utils/diffing/test_feature_cache.py`
  - pipeline invariant: `tests/test_backtest_hook_invariants.py`
  - smoke: `tests/test_import_smoke_backtest_optuna.py`
