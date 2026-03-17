## Context Map

### Slice intent

This slice defines the exact future execution flow for `RI P1 OFF parity governed rerun`.

It remains **prep-only**. No rerun is executed here, no baseline is approved here, and no sign-off claim is made here.

### Planned frozen execution target

These values are the **planned frozen execution inputs derived from the current repo-visible contract/example surface**. They are not, by themselves, proof that an approved baseline already exists.

| Field                   | Planned target value                                   | Source / note                            |
| ----------------------- | ------------------------------------------------------ | ---------------------------------------- |
| `window_spec_id`        | `ri_p1_off_parity_v1`                                  | locked by DoD                            |
| `mode`                  | `OFF`                                                  | locked by DoD                            |
| `symbol`                | `tTESTBTC:TESTUSD`                                     | repo-visible concrete example/test value |
| `timeframe`             | `1h`                                                   | repo-visible concrete example/test value |
| `start_utc`             | `2025-01-01T00:00:00Z`                                 | repo-visible concrete example/test value |
| `end_utc`               | `2025-01-31T23:59:59Z`                                 | repo-visible concrete example/test value |
| `baseline_artifact_ref` | `results/evaluation/ri_p1_off_parity_v1_baseline.json` | reserved canonical reference path        |
| `GENESIS_FAST_HASH`     | `0`                                                    | frozen determinism requirement           |

### Hard caveat on baseline provenance

Execution must **STOP** unless approved baseline provenance for the exact target window above is verified first.

Accepted baseline classifications for the future execution slice:

- `recovered approved baseline`
- `newly approved baseline under explicit governance approval`

Any other baseline classification is invalid for sign-off.

### Future execution flow map

| Step | Planned action                                                                                | Planned output                                                                             | Must be reviewable? |
| ---- | --------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------ | ------------------- |
| 1    | verify frozen spec + target window                                                            | execution packet header                                                                    | yes                 |
| 2    | verify baseline provenance and classify it                                                    | baseline classification note                                                               | yes                 |
| 3    | materialize/recover baseline rows evidence                                                    | supplemental baseline rows JSON under `docs/audit/refactor/regime_intelligence/evidence/`  | yes                 |
| 4    | generate candidate decision rows with `scripts/run/run_backtest.py` and `--decision-rows-out` | supplemental candidate rows JSON under `docs/audit/refactor/regime_intelligence/evidence/` | yes                 |
| 5    | run `tools/compare_backtest_results.py --ri-off-parity`                                       | canonical parity artifact under `results/evaluation/`                                      | yes                 |
| 6    | compute SHA256 values and write supplemental manifest                                         | supplemental rerun manifest JSON under `docs/audit/refactor/regime_intelligence/evidence/` | yes                 |
| 7    | run full gate bundle                                                                          | gate transcript + PASS/FAIL outcomes                                                       | yes                 |
| 8    | only if parity verdict is `PASS` and all gates are green, propose sign-off                    | governance recommendation                                                                  | yes                 |

### Planned artifact role map for future execution

| Role                              | Planned path                                                                                        | Role type                        | Notes                                                                |
| --------------------------------- | --------------------------------------------------------------------------------------------------- | -------------------------------- | -------------------------------------------------------------------- |
| Canonical parity artifact         | `results/evaluation/ri_p1_off_parity_v1_<run_id>.json`                                              | normative / canonical            | required for sign-off                                                |
| Canonical baseline reference path | `results/evaluation/ri_p1_off_parity_v1_baseline.json`                                              | normative reference path         | reserved path; approval/provenance must be verified before execution |
| Baseline rows retained evidence   | `docs/audit/refactor/regime_intelligence/evidence/ri_p1_off_parity_v1_baseline_rows_<run_id>.json`  | supplemental governance evidence | must hash-link to approved baseline input                            |
| Candidate rows retained evidence  | `docs/audit/refactor/regime_intelligence/evidence/ri_p1_off_parity_v1_candidate_rows_<run_id>.json` | supplemental governance evidence | generated via `--decision-rows-out`                                  |
| Supplemental manifest             | `docs/audit/refactor/regime_intelligence/evidence/ri_p1_off_parity_v1_manifest_<run_id>.json`       | supplemental governance evidence | must reference canonical artifact path and SHA256                    |

### Required metadata bundle for the future execution slice

- `run_id`
- `git_sha`
- `branch`
- `executed_at_utc`
- `window_spec_id`
- `mode`
- `symbol`
- `timeframe`
- `start_utc`
- `end_utc`
- `runtime_config_source`
- `compare_tool_path`
- `baseline_artifact_ref`
- `baseline_rows_path`
- `candidate_rows_path`
- `baseline_sha256`
- `candidate_sha256`
- `canonical_artifact_path`
- `canonical_artifact_sha256`
- `size_tolerance`
- `decision_rows_format`
- `candidate_generation_command`
- `compare_command`

### Exact future verification bundle

- `pre-commit` / lint
- smoke test: `tests/governance/test_import_smoke_backtest_optuna.py`
- determinism replay: `tests/backtest/test_backtest_determinism_smoke.py`
- feature cache invariance:
  - `tests/utils/test_features_asof_cache.py`
  - `tests/utils/test_features_asof_cache_key_deterministic.py`
- pipeline invariant: `tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`
- evaluate/source invariants:
  - `tests/backtest/test_evaluate_pipeline.py::test_evaluate_pipeline_shadow_error_rate_contract`
  - `tests/backtest/test_evaluate_pipeline.py::test_evaluate_pipeline_authority_mode_source_invariant_contract`
- comparator selectors:
  - `tests/backtest/test_compare_backtest_results.py::test_compare_ri_p1_off_parity_rows_pass_order_insensitive`
  - `tests/backtest/test_compare_backtest_results.py::test_build_ri_p1_off_parity_artifact_required_fields`
- decision-row serialization selector:
  - `tests/backtest/test_run_backtest_decision_rows.py::test_write_decision_rows_json_and_ndjson`
- skill checks:
  - `python scripts/run_skill.py --skill ri_off_parity_artifact_check --manifest dev`
  - `python scripts/run_skill.py --skill feature_parity_check --manifest dev --dry-run`
  - `python scripts/run_skill.py --skill config_authority_lifecycle_check --manifest dev --dry-run`

### Non-negotiable boundaries

- No execution in this slice
- No baseline approval in this slice
- No writes to canonical or supplemental evidence paths in this slice
- No runtime/config/champion/default-authority changes
- No reuse of `ri_p1_off_parity_v1_ri-20260303-003.json` as sign-off evidence, baseline, or candidate input
