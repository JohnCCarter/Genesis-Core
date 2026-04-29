# RI advisory environment-fit Phase 3 reliability exact-label-authority preflight packet

Date: 2026-04-17
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: `active / research-only / exact-label-authority preflight`

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `branch:feature/ri-role-map-implementation-2026-03-24`
- **Category:** `obs`
- **Risk:** `MEDIUM-HIGH` — bounded research-only preflight that approaches the exact Phase 2 label contract for the reliability axis; no runtime/config authority changes, but the slice must fail closed on any synthetic label or cohort invention.
- **Required Path:** `Full gated protocol with Opus pre-review`
- **Constraints:** `NO BEHAVIOR CHANGE`
- **Objective:** determine whether the exact Phase 2 supportive/hostile outcome-label surface can be materially re-materialized for the narrow reliability axis on the Phase C capture-v2 RI rows by replaying the locked baseline-vs-candidate comparison chain and joining back by exact key, without heuristic substitution, synthetic cohort invention, or Phase 4 drift.
- **Candidate:** `RI advisory environment-fit Phase 3 reliability exact-label-authority preflight`
- **Base SHA:** `e16e3f9fd68500dc741f8edd9757c709e22bf595`

### Scope

- **Scope IN:**
  - `docs/governance/ri_advisory_environment_fit_phase3_reliability_exact_label_authority_preflight_packet_2026-04-17.md`
  - `tmp/ri_advisory_environment_fit_reliability_exact_label_authority_preflight_20260417.py`
  - approved result artifacts under `results/research/ri_advisory_environment_fit/phase3_reliability_exact_label_authority_preflight_2026-04-17/`
  - `docs/analysis/ri_advisory_environment_fit_phase3_reliability_exact_label_authority_preflight_2026-04-17.md`
- **Scope OUT:**
  - `src/**`
  - `tests/**`
  - `config/**`
  - existing `results/**` artifacts outside the new approved output dir
  - any runtime-facing score implementation
  - any transition-axis promotion
  - any Phase 4 opening
  - any dirty-research heuristic reuse as pseudo-authority
  - any mutation of the locked evidence bundle, baseline config, candidate config, or prior tracked summaries
- **Expected changed files:**
  - `docs/governance/ri_advisory_environment_fit_phase3_reliability_exact_label_authority_preflight_packet_2026-04-17.md`
  - `tmp/ri_advisory_environment_fit_reliability_exact_label_authority_preflight_20260417.py`
  - `results/research/ri_advisory_environment_fit/phase3_reliability_exact_label_authority_preflight_2026-04-17/join_audit.json`
  - `results/research/ri_advisory_environment_fit/phase3_reliability_exact_label_authority_preflight_2026-04-17/label_authority_audit.json`
  - `results/research/ri_advisory_environment_fit/phase3_reliability_exact_label_authority_preflight_2026-04-17/materialized_exact_label_rows.ndjson`
  - `results/research/ri_advisory_environment_fit/phase3_reliability_exact_label_authority_preflight_2026-04-17/boundary_manifest.json`
  - `results/research/ri_advisory_environment_fit/phase3_reliability_exact_label_authority_preflight_2026-04-17/closeout.md`
  - `results/research/ri_advisory_environment_fit/phase3_reliability_exact_label_authority_preflight_2026-04-17/manifest.json`
  - `docs/analysis/ri_advisory_environment_fit_phase3_reliability_exact_label_authority_preflight_2026-04-17.md`
- **Max files touched:** `9`

### Skill coverage

- Invoked repo-local skill: `.github/skills/python_engineering.json`
- No dedicated repo-local skill currently exists for exact-label-authority observability preflight on research artifacts.
- A dedicated skill for this surface is therefore only `föreslagen` and is explicitly OUT OF SCOPE for implementation in this slice.

### Single-source authority anchors

For this slice, exact-label authority may come only from the following locked chain:

- authoritative baseline config:
  - `results/research/fa_v2_adaptation_off/phase15_bull_high_persistence_override/tBTCUSD_3h_bull_high_persistence_override_min_size_001_vol_mult_090_vol_thr_75_cfg.json`
- authoritative candidate config:
  - `results/research/fa_v2_adaptation_off/phase15_bull_high_persistence_override/current_atr_selective_900_validation_2026-04-15/candidate_900_cfg.json`
- authoritative comparison-chain implementation:
  - `tmp/current_atr_900_env_profile_20260416.py`
  - specifically the bounded baseline-vs-candidate replay and `_build_analysis_rows(...)` path that emits exact `pnl_delta` from the locked comparison surface and defines the active-uplift population by shared-position membership plus positive `size_delta`
- authoritative capture-v2 join contract:
  - `results/research/ri_advisory_environment_fit/phase3_phasec_evidence_capture_v2_2026-04-17/capture_summary.json`
  - locked definition: `normalize(entry_time)|side`
- authoritative capture-v2 row surface carrying the existing `join_key`:
  - `results/research/ri_advisory_environment_fit/phase3_phasec_evidence_capture_v2_2026-04-17/entry_rows.ndjson`

If any required authority field cannot be obtained from that locked chain, the only allowed top-level outcome is `NOT_RECOVERED`.

### Gates required

- `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m pytest tests/backtest/test_runner_direct_includes_merged_config.py`
- `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m pytest tests/backtest/test_backtest_engine.py::test_engine_run_skip_champion_merge_does_not_load_champion`
- `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m pytest tests/backtest/test_backtest_determinism_smoke.py::test_backtest_engine_is_deterministic_across_two_runs`
- `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m pytest tests/utils/test_features_asof_cache_key_deterministic.py::test_compute_candles_hash_is_deterministic_across_pyhashseed`
- `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m pytest tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`
- `pre-commit run --files docs/governance/ri_advisory_environment_fit_phase3_reliability_exact_label_authority_preflight_packet_2026-04-17.md tmp/ri_advisory_environment_fit_reliability_exact_label_authority_preflight_20260417.py docs/analysis/ri_advisory_environment_fit_phase3_reliability_exact_label_authority_preflight_2026-04-17.md`

### Allowed evidence inputs

#### Label-authority inputs the script may consume directly

- `tmp/current_atr_900_env_profile_20260416.py`
- `tmp/ri_advisory_environment_fit_capture_v2_20260417.py`
- `results/research/ri_advisory_environment_fit/phase3_phasec_evidence_capture_v2_2026-04-17/entry_rows.ndjson`
- `results/research/ri_advisory_environment_fit/phase3_phasec_evidence_capture_v2_2026-04-17/capture_summary.json`
- `results/research/fa_v2_adaptation_off/phase15_bull_high_persistence_override/tBTCUSD_3h_bull_high_persistence_override_min_size_001_vol_mult_090_vol_thr_75_cfg.json`
- `results/research/fa_v2_adaptation_off/phase15_bull_high_persistence_override/current_atr_selective_900_validation_2026-04-15/candidate_900_cfg.json`

These are the only inputs the script may use to author labels, cohorts, joins, or recovery decisions.

#### Memo / provenance-only inputs

- `docs/analysis/ri_advisory_environment_fit_phase2_label_taxonomy_2026-04-16.md`
- `docs/analysis/ri_advisory_environment_fit_phase3_partial_baseline_label_gap_2026-04-17.md`
- `docs/analysis/ri_advisory_environment_fit_phase3_dirty_reliability_evidence_2026-04-17.md`
- `docs/analysis/ri_advisory_environment_fit_phase3_post_dirty_research_exact_label_admissibility_2026-04-17.md`
- `tmp/current_atr_900_multi_year_env_robustness_20260416.py`
- `results/research/fa_v2_adaptation_off/phase15_bull_high_persistence_override/current_atr_900_env_profile_2026-04-16/env_summary.json`
- `results/research/fa_v2_adaptation_off/phase15_bull_high_persistence_override/current_atr_900_env_profile_2026-04-16/manifest.json`
- `results/research/fa_v2_adaptation_off/phase15_bull_high_persistence_override/current_atr_900_multi_year_env_robustness_2026-04-16/robustness_summary.json`
- `artifacts/bundles/ri_advisory_environment_fit/phase3_phasec_evidence_freeze_2026-04-17/phaseC_oos_evidence_bundle.json`

These may inform memo wording, provenance cross-checks, and expectation checks only.
They must not be used by the script as a source for labels, cohorts, join keys, or recovery decisions.

### Required questions

The script and memo must answer at minimum:

1. can the exact bounded baseline-comparison `pnl_delta` surface be replayed from locked sources without mutating upstream artifacts?
2. can active-uplift cohort membership be derived from the same locked comparison chain without heuristic or synthetic invention?
3. can that exact label surface be joined back to the Phase C capture-v2 RI rows by exact `join_key` only?
4. if exact label authority is materially recoverable, does it remain narrow enough to continue only on the reliability axis while keeping transition and Phase 4 closed?

### Required boundary statements

The script and memo must state explicitly that:

- the single-source authority rule is in force: exact-label authority may come only from the locked bounded baseline-vs-candidate comparison chain
- any dirty-research heuristic labels remain out of scope and non-authoritative for this slice
- exact labels, if recovered, come only from the locked baseline-vs-candidate evidence chain
- `pnl_delta` must come from the bounded baseline comparison surface, not from raw `total_pnl` sign shortcuts
- `active_uplift_cohort_membership` must come from the locked comparison chain, not from heuristic reconstruction
- this slice does not open Phase 4 and does not authorize runtime score implementation

### Required output behavior

The script must emit only the approved files under:

- `results/research/ri_advisory_environment_fit/phase3_reliability_exact_label_authority_preflight_2026-04-17/`

The script must produce at minimum:

- one join audit for exact-key overlap with capture-v2 rows
- one label-authority audit explaining whether `pnl_delta` and active-uplift membership were recovered exactly
- one row-level materialized exact-label surface file
- one boundary manifest keeping `exact_label_authority` and `phase4_opening` explicit

The `boundary_manifest.json` must also record at minimum:

- `transition_promotion = false`
- `dirty_research_authority = false`
- `runtime_readiness = false`
- locked provenance / hash anchors for the capture-v2 evidence rows, baseline config, candidate config, and any tracked summary files actually consumed
- content hash for `tmp/current_atr_900_env_profile_20260416.py`
- content hash for `tmp/ri_advisory_environment_fit_capture_v2_20260417.py`

The script and memo may report only one of the following top-level outcomes:

- `RECOVERED_EXACT_LABEL_AUTHORITY`
- `NOT_RECOVERED`

No intermediate authority-like outcome wording is allowed.

`RECOVERED_EXACT_LABEL_AUTHORITY` is allowed only if all of the following are true:

1. exact `pnl_delta` is replayed from the locked bounded baseline-vs-candidate comparison chain only
2. exact `active_uplift_cohort_membership` is replayed from that same locked comparison chain only
3. `join_key` is unique and non-missing on the rematerialized exact-label surface and on the capture-v2 RI rows
4. the shared comparison population joins back to the capture-v2 RI rows as an exact 1:1 join with zero unmatched exact-label rows
5. every capture-v2 RI row receives an exact Phase-2-faithful row state from locked sources only:
  - `supportive_context_outcome`
  - `hostile_context_outcome`
  - `non_evaluable_context`
6. no supportive/hostile row has null `pnl_delta`
7. every `non_evaluable_context` row is produced only because the exact locked comparison chain does not yield supportive/hostile authority for that capture-v2 `join_key`
8. no `non_evaluable_context` row is produced from dirty-research heuristics, proxy ranks, or raw `total_pnl` sign shortcuts

If any one of those conditions fails, the only allowed outcome is `NOT_RECOVERED`.

### Stop conditions

- any need to use dirty-research heuristic buckets as substitutes for exact labels
- any direct script read of dirty-research analysis docs as label/cohort/join-key authority input
- any local reimplementation, copy, wrapper, or edited variant of `tmp/current_atr_900_env_profile_20260416.py::_build_analysis_rows(...)` or its active-uplift cohort derivation logic instead of importing/calling the locked chain directly
- any use of raw `total_pnl` sign as a shortcut for `pnl_delta`
- any need for synthetic or inferred active-uplift cohort membership beyond the locked baseline-vs-candidate comparison chain
- any drift in baseline/candidate config provenance, evidence-bundle provenance, or tracked summary provenance relative to the locked sources named in this packet
- any need to re-author, re-normalize beyond the locked contract, or heuristically derive `join_key` from anything other than the locked `normalize(entry_time)|side` contract and the exact replayed `entry_time` + `side` fields from the authority chain
- any missing or duplicate `join_key` on the rematerialized label surface, the shared comparison surface, or the capture-v2 RI rows
- any many-to-one or fuzzy join instead of exact `join_key`
- any duplicate join keys on either the rematerialized label surface or the capture-v2 RI rows
- any proposal to carry transition-axis claims forward from this slice
- any wording that treats the result as Phase 4 opening or runtime-readiness

## Bottom line

This packet authorizes one narrow research-only exact-label-authority preflight for the reliability axis.
It does not authorize transition promotion, Phase 4, runtime integration, or reuse of dirty-research heuristic labels as authority.
