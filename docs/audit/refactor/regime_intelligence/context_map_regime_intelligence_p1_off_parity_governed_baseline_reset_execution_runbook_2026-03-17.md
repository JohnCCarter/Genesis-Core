## Context Map

### Runbook intent

This slice defines the operational execution runbook for the selected fallback path:

`governed baseline reset via parity rerun under frozen spec ri_p1_off_parity_v1`

It is still **prep-only**.

It does **not** start the rerun, does **not** approve the baseline, and does **not** approve execution.

### Pinned execution provenance

| Field                    | Locked value                                      | Meaning                                                                          |
| ------------------------ | ------------------------------------------------- | -------------------------------------------------------------------------------- |
| reviewed branch          | `feature/regime-intelligence-cutover-analysis-v1` | branch reviewed for future rerun execution                                       |
| reviewed short SHA       | `1c2f38ad`                                        | human-readable pin                                                               |
| reviewed full SHA        | `1c2f38ad88723034b819b7844c69d138a7702086`        | exact reviewed execution commit                                                  |
| working tree requirement | `clean`                                           | no uncommitted or untracked execution inputs may participate in the future rerun |

### Future execution provenance rule

The future rerun may be proposed only from:

- reviewed branch `feature/regime-intelligence-cutover-analysis-v1`
- reviewed commit `1c2f38ad88723034b819b7844c69d138a7702086`
- a clean working tree

If execution is later proposed from any successor SHA, the rerun must STOP and wait for a separate execution-approval packet that explicitly re-pins and re-reviews that successor SHA.

### How the frozen spec materializes

`window_spec_id=ri_p1_off_parity_v1` is a governance-defined frozen execution identity.

It materializes in two layers:

1. **candidate-row generation layer**
   - the backtest command materializes the frozen execution tuple:
     - `symbol=tTESTBTC:TESTUSD`
     - `timeframe=1h`
     - `start=2025-01-01`
     - `end=2025-01-31`
     - optional reviewed `--config-file`
   - this step produces the candidate decision rows
2. **parity-artifact layer**
   - the compare command materializes:
     - `window_spec_id=ri_p1_off_parity_v1`
     - `run_id`
     - `git_sha`
     - `baseline_artifact_ref`
     - `parity_verdict`
     - mismatch counts
     - `size_tolerance`

### Frozen future execution target

| Field                   | Locked value                                           | Source                            |
| ----------------------- | ------------------------------------------------------ | --------------------------------- |
| `window_spec_id`        | `ri_p1_off_parity_v1`                                  | governance frozen spec            |
| `mode`                  | `OFF`                                                  | comparator contract               |
| `symbol`                | `tTESTBTC:TESTUSD`                                     | reviewed execution tuple          |
| `timeframe`             | `1h`                                                   | reviewed execution tuple          |
| `start_utc`             | `2025-01-01T00:00:00Z`                                 | reviewed execution tuple          |
| `end_utc`               | `2025-01-31T23:59:59Z`                                 | reviewed execution tuple          |
| `baseline_artifact_ref` | `results/evaluation/ri_p1_off_parity_v1_baseline.json` | reserved canonical reference path |
| `GENESIS_FAST_HASH`     | `0`                                                    | frozen environment requirement    |
| `size_tolerance`        | `1e-12`                                                | compare-tool contract             |

### Baseline handling in the future rerun

The future execution packet must distinguish three baseline concepts clearly:

| Concept                           | Future meaning                                                                       | Allowed in future rerun?        |
| --------------------------------- | ------------------------------------------------------------------------------------ | ------------------------------- |
| baseline input rows               | the actual rows file passed as baseline input to the comparator                      | yes                             |
| canonical baseline reference path | `results/evaluation/ri_p1_off_parity_v1_baseline.json` recorded in artifact metadata | yes, as reserved reference path |
| baseline approval / promotion     | governance act that approves or promotes a canonical baseline                        | not by this runbook             |

Required future baseline classification:

- `newly approved baseline under explicit governance approval`

That classification must be recorded explicitly in the future execution packet. A future parity `PASS` does **not** implicitly create or approve the canonical baseline path.

### Candidate-row generation surface

The future rerun must generate candidate rows via `scripts/run/run_backtest.py` using the reviewed CLI surface:

- `--symbol tTESTBTC:TESTUSD`
- `--timeframe 1h`
- `--start 2025-01-01`
- `--end 2025-01-31`
- `--decision-rows-out docs/audit/refactor/regime_intelligence/evidence/ri_p1_off_parity_v1_candidate_rows_<run_id>.json`
- `--decision-rows-format json`
- optional reviewed `--config-file <path>`

Required future provenance capture from this step:

- `candidate_rows_path`
- `candidate_sha256`
- `candidate_generation_command`
- `runtime_config_source`

If `--config-file` is omitted, `runtime_config_source` must still be recorded explicitly as reviewed default-runtime authority wording; it may not be left blank.

### Compare-command surface

The future rerun must generate the canonical parity artifact via `tools/compare_backtest_results.py` using the reviewed comparator surface:

- positional `baseline` rows input path
- positional `candidate` rows input path
- `--ri-off-parity`
- `--run-id <run_id>`
- `--git-sha 1c2f38ad88723034b819b7844c69d138a7702086`
- `--symbols tTESTBTC:TESTUSD`
- `--timeframes 1h`
- `--start-utc 2025-01-01T00:00:00Z`
- `--end-utc 2025-01-31T23:59:59Z`
- `--baseline-artifact-ref results/evaluation/ri_p1_off_parity_v1_baseline.json`
- optional `--artifact-out results/evaluation/ri_p1_off_parity_v1_<run_id>.json`
- optional `--size-tolerance 1e-12`

If `--artifact-out` is omitted, the compare tool defaults to:

- `results/evaluation/ri_p1_off_parity_v1_<run_id>.json`

### Canonical artifact contract emitted by the compare step

Required artifact metadata fields:

- `window_spec_id`
- `run_id`
- `git_sha`
- `mode`
- `symbols`
- `timeframes`
- `start_utc`
- `end_utc`
- `baseline_artifact_ref`
- `parity_verdict`
- `action_mismatch_count`
- `reason_mismatch_count`
- `size_mismatch_count`
- `added_row_count`
- `missing_row_count`
- `size_tolerance`

### Future evidence outputs required

| Output role               | Required future path                                                                                |
| ------------------------- | --------------------------------------------------------------------------------------------------- |
| baseline rows evidence    | `docs/audit/refactor/regime_intelligence/evidence/ri_p1_off_parity_v1_baseline_rows_<run_id>.json`  |
| candidate rows evidence   | `docs/audit/refactor/regime_intelligence/evidence/ri_p1_off_parity_v1_candidate_rows_<run_id>.json` |
| canonical parity artifact | `results/evaluation/ri_p1_off_parity_v1_<run_id>.json`                                              |
| supplemental manifest     | `docs/audit/refactor/regime_intelligence/evidence/ri_p1_off_parity_v1_manifest_<run_id>.json`       |

### Future gate bundle that must pass before PASS counts

- `pre-commit` / lint
- `python -m pytest -q tests/governance/test_import_smoke_backtest_optuna.py`
- `python -m pytest -q tests/backtest/test_backtest_determinism_smoke.py`
- `python -m pytest -q tests/utils/test_features_asof_cache.py tests/utils/test_features_asof_cache_key_deterministic.py`
- `python -m pytest -q tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`
- `python -m pytest -q tests/backtest/test_evaluate_pipeline.py::test_evaluate_pipeline_shadow_error_rate_contract`
- `python -m pytest -q tests/backtest/test_evaluate_pipeline.py::test_evaluate_pipeline_authority_mode_source_invariant_contract`
- `python -m pytest -q tests/backtest/test_compare_backtest_results.py::test_compare_ri_p1_off_parity_rows_pass_order_insensitive`
- `python -m pytest -q tests/backtest/test_compare_backtest_results.py::test_build_ri_p1_off_parity_artifact_required_fields`
- `python -m pytest -q tests/backtest/test_run_backtest_decision_rows.py::test_write_decision_rows_json_and_ndjson`
- `python scripts/run_skill.py --skill ri_off_parity_artifact_check --manifest dev`
- `python scripts/run_skill.py --skill feature_parity_check --manifest dev --dry-run`
- `python scripts/run_skill.py --skill config_authority_lifecycle_check --manifest dev --dry-run`

### Non-negotiable boundaries

- No execution in this runbook slice
- No baseline approval or promotion in this runbook slice
- No execution from a dirty working tree
- No execution from an unreviewed successor SHA
- No runtime/config/champion/default-authority changes
- No frozen-spec drift
- No compare-surface drift
- No relabeling of March sign-off text or ignored logs as recovered baseline provenance
- No reuse of synthetic `ri_p1_off_parity_v1_ri-20260303-003.json`
- No evidence chain that lives only under ignored or untracked local state
