## Context Map

### Slice intent

This slice prepares the reviewable execution-approval candidate packet for the selected fallback path:

`governed baseline reset via parity rerun under frozen spec ri_p1_off_parity_v1`

It is an **approval candidate** only.

Readiness state in this slice: `ready_for_governance_review`.

It does **not** start the rerun, does **not** enact baseline approval, and does **not** itself approve execution.

### Lineage inherited from approved docs

| Source doc                                                                                                  | Inherited role                                                                                            |
| ----------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------- |
| `docs/decisions/regime_intelligence/p1_off_parity/regime_intelligence_p1_off_parity_governed_baseline_reset_execution_prep_2026-03-17.md`    | selects fallback path and retires evidence recovery as the preferred next step                            |
| `docs/decisions/regime_intelligence/p1_off_parity/regime_intelligence_p1_off_parity_governed_baseline_reset_execution_runbook_2026-03-17.md` | locks execution provenance, command surfaces, canonical artifact path, metadata contract, and gate bundle |
| `docs/decisions/regime_intelligence/p1_off_parity/regime_intelligence_p1_off_parity_governed_rerun_execution_plan_2026-03-17.md`             | preserves canonical artifact semantics and full future execution flow                                     |
| `docs/decisions/regime_intelligence/p1_off_parity/regime_intelligence_p1_off_parity_governed_rerun_execution_review_2026-03-17.md`           | preserves the rule that execution is not auto-approved by structural completeness                         |

### Pinned execution provenance inherited from the runbook

| Field        | Locked value                                      | Approval significance                               |
| ------------ | ------------------------------------------------- | --------------------------------------------------- |
| branch       | `feature/regime-intelligence-cutover-analysis-v1` | execution candidate must match reviewed branch      |
| short SHA    | `1c2f38ad`                                        | human review anchor                                 |
| full SHA     | `1c2f38ad88723034b819b7844c69d138a7702086`        | exact execution commit requested for approval       |
| working tree | `clean`                                           | future rerun may not execute from dirty local state |

If future execution is proposed from any successor SHA, this approval packet becomes insufficient and a fresh governance packet must re-pin and re-review that SHA.

### Approval decision being prepared

This slice prepares a future governance decision on whether the pinned rerun may be allowed to execute.

The packet therefore asks governance to evaluate, but does not itself grant:

- the pinned rerun provenance
- the requested future baseline classification
- the candidate/baseline provenance contract
- the canonical artifact contract
- the named full gate bundle

### Future-scoped baseline classification

Allowed / requested future baseline classification for this path:

- `newly approved baseline under explicit governance approval`

This wording is future-scoped by design.

It does **not** mean that the baseline is already approved in this slice.
It does **not** promote `results/evaluation/ri_p1_off_parity_v1_baseline.json` in this slice.
It does **not** allow a future `PASS` to auto-promote the canonical baseline path.

### Candidate / baseline provenance contract required for future approval

The future execution packet reviewed under this approval candidate must present a reviewable provenance bundle containing at least:

- `baseline_artifact_ref`
- `baseline_rows_path`
- `baseline_sha256`
- `baseline_approval_anchor`
- `candidate_rows_path`
- `candidate_sha256`
- `candidate_generation_command`
- `runtime_config_source`
- `compare_tool_path`
- `compare_command`
- `canonical_artifact_path`
- `decision_rows_format=json`
- pinned `git_sha`
- pinned `window_spec_id`
- pinned `symbol`, `timeframe`, `start_utc`, `end_utc`

In this slice, those items are defined as approval requirements only. They are not yet fulfilled or written by this slice.

### Canonical artifact contract preserved for the approval candidate

| Contract item                     | Locked value                                           | Status in this slice                    |
| --------------------------------- | ------------------------------------------------------ | --------------------------------------- |
| canonical artifact path           | `results/evaluation/ri_p1_off_parity_v1_<run_id>.json` | defined, not produced                   |
| canonical baseline reference path | `results/evaluation/ri_p1_off_parity_v1_baseline.json` | reserved reference path only            |
| `window_spec_id`                  | `ri_p1_off_parity_v1`                                  | defined, not materialized by this slice |
| `mode`                            | `OFF`                                                  | defined, not materialized by this slice |
| metadata requirements             | locked by compare-tool contract                        | defined, not fulfilled by this slice    |

### Artifact metadata requirements preserved for approval review

The future canonical artifact must include at least:

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

### Full gate bundle that remains locked for approval review

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

- No execution approval by packet existence alone
- No execution in this slice
- No baseline approval or promotion in this slice
- No execution from a dirty working tree
- No execution from an unreviewed successor SHA
- No claim that canonical artifact or evidence outputs already exist because this packet exists
- No claim that future `PASS` auto-promotes `results/evaluation/ri_p1_off_parity_v1_baseline.json`
- No runtime/config/champion/default-authority changes
- No frozen-spec drift
- No gate-bundle or named-skill drift
- No provenance claim that depends only on ignored or untracked local state
- No reuse of synthetic `ri_p1_off_parity_v1_ri-20260303-003.json`
