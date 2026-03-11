# COMMAND PACKET

- **Mode:** `RESEARCH` — source: branch `feature/refactor-tests-structure-b` via `docs/governance_mode.md` branch mapping
- **Risk:** `LOW` — why: tests/docs-only structural refactor, no production code edits
- **Required Path:** `Full` (explicit selector evidence retained)
- **Objective:** Continue Shard B maintainability refactor by deduplicating repeated guardrail tests in `tests/test_authority_mode_resolver.py` and `tests/test_volume.py` while preserving assertion parity.
- **Candidate:** Replace near-identical `None` asymmetry tests with one parametrized parity test, consolidate repeated two-input empty/mismatched-length tests for `obv` and `volume_price_divergence`, deduplicate invalid-parameter guardrails for `volume_change`, `volume_spike`, and `calculate_volume_ema`, consolidate empty-input/insufficient-data guardrails for moving-average and lookback helpers, merge strict canonicalization normalization tests with equivalent assertion shape, and consolidate repeated OBV sequence-assertion patterns.
- **Base SHA:** `7052a86fc7314198289ccd32be98911f96e09f35`

## Skill Usage

- `repo_clean_refactor` (SPEC): scope lock, no-behavior-change, minimal reversible diffs.
- `python_engineering` (SPEC): pytest/ruff-first validation and Python quality constraints.

## Scope

- **Scope IN:**
  - `tests/test_volume.py`
  - `docs/audit/refactor/command_packet_shard_b_refactor_2026-03-06_step2.md`
  - `tests/test_authority_mode_resolver.py`
  - `docs/audit/refactor/command_packet_shard_b_refactor_2026-03-06_batch2.md`
- **Scope OUT:**
  - all non-test paths except listed governance artifacts under `docs/audit/refactor/`
  - all other test files
- **Expected changed files:**
  - `tests/test_volume.py`
  - `docs/audit/refactor/command_packet_shard_b_refactor_2026-03-06_step2.md`
  - `tests/test_authority_mode_resolver.py`
  - `docs/audit/refactor/command_packet_shard_b_refactor_2026-03-06_batch2.md`
- **Max files touched:** `4`

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

- Scope drift beyond listed files
- Any runtime behavior impact
- Any assertion parity drift in authority-mode tests
- Determinism, feature cache, pipeline invariant, or smoke regression

## Output required

- **Implementation Report**
- **PR evidence template**

## Gate evidence (executed)

Gate evidence below is reported from executed local runs.
Raw terminal transcripts are attached in PR evidence artifacts for independent verification.
Current changed files are verified via `git status` and constrained to the batch2
test/docs scope definitions above.

Increment note: initial substep touched only `tests/test_volume.py`.
Current batch state also includes parametrization cleanup in
`tests/test_authority_mode_resolver.py`.
Revalidation note: gates were re-run after two-input guardrail dedupe; outcomes remained green.
Revalidation note: gates were re-run after invalid-parameter guardrail dedupe; outcomes remained green.
Revalidation note: gates were re-run after empty-input/insufficient-data guardrail dedupe; outcomes remained green.
Revalidation note: gates were re-run after strict canonicalization normalization dedupe; outcomes remained green.
Revalidation note: gates were re-run after OBV scenario sequence-assertion dedupe; outcomes remained green.
Remediation note: out-of-scope artifact `scripts/build/__pycache__/` removed before final post-audit.
Revalidation note: quick parity check re-run on `tests/test_volume.py` after artifact cleanup; outcomes remained green.

- targeted tests (`tests/test_authority_mode_resolver.py`, `tests/test_volume.py`) -> PASS (`52 passed, 0 failed`)
- OBV scenario selector (`tests/test_volume.py::TestOBV::test_obv_scenarios`) -> PASS (`4 passed, 0 failed`)
- strict exception parity selector (`tests/test_authority_mode_resolver.py::test_strict_canonicalization_exact_exception_message_parity`) -> PASS (`5 passed, 0 failed`)
- `python -m pre_commit run --all-files` -> PASS
- `python -m ruff check .` -> PASS
- `pytest` -> PASS (`981 passed, 0 failed`)
- Selector suite -> PASS (`15 passed, 0 failed`)
  - determinism replay: `tests/test_backtest_determinism_smoke.py`,
    `tests/test_config_authority_path_determinism.py`
  - feature cache invariance: `tests/test_feature_cache.py`,
    `tests/utils/diffing/test_feature_cache.py`
  - pipeline invariant: `tests/test_backtest_hook_invariants.py`
  - smoke: `tests/test_import_smoke_backtest_optuna.py`
- quick revalidation (`tests/test_volume.py`) -> PASS (`38 passed, 0 failed`)
