# RI advisory environment-fit Phase 3 dirty reliability evidence packet

Date: 2026-04-17
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: `active / bounded dirty-research evidence shaping / results-only / default unchanged`
Opus pre-code verdict: `APPROVED_WITH_NOTES`

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `branch:feature/ri-role-map-implementation-2026-03-24`
- **Category:** `obs`
- **Risk:** `MED` — bounded exploratory evidence-shaping on an already joined RI selector/proxy surface using approximate labels and simple heuristics; outputs confined to `tmp/`, `results/`, and one memo; no runtime/default/authority changes.
- **Required Path:** `Full`
- **Constraints:** `NO BEHAVIOR CHANGE`
- **Objective:** shape one approximate reliability-side evidence surface using clearly non-authoritative heuristic labels so Phase 3 can inspect the data in a more useful form before any exact-label-authority follow-up is considered.
- **Candidate:** `RI advisory environment-fit Phase 3 dirty reliability evidence`
- **Base SHA:** `e16e3f9fd68500dc741f8edd9757c709e22bf595`
- **Skill Usage:** `python_engineering`, `genesis_backtest_verify`

### Scope

- **Scope IN:**
  - `docs/governance/ri_advisory_environment_fit_phase3_dirty_reliability_evidence_packet_2026-04-17.md`
  - one bounded research script under `tmp/`
  - one results directory under `results/research/ri_advisory_environment_fit/`
  - one analysis memo under `docs/analysis/`
- **Scope OUT:**
  - `src/**`
  - `tests/**`
  - `config/**`
  - `artifacts/**`
  - runtime authority changes
  - default behavior changes
  - any exact Phase 2 supportive/hostile claim
  - any production-clean label claim
  - any Phase 4 opening
  - any runtime-facing recommendation
  - ML/model work
- **Expected changed files:**
  - this packet
  - one `tmp/` script
  - one `docs/analysis/` memo
  - results artifacts confined to one new result subdirectory
- **Max files touched:** `8`

### Dirty-research allowance used in this slice

This slice explicitly uses the controlled dirty-research allowance inside `RESEARCH` only.
It does not create or imply a fourth governance mode.

- approximate labels are allowed
- incomplete classification is allowed
- simple heuristics are allowed

But only if the outputs remain explicitly marked as:

- exploratory
- approximate
- non-authoritative
- not Phase-2-faithful

### Fixed evidence source

- selector source:
  - `results/research/ri_advisory_environment_fit/phase3_phasec_evidence_capture_v2_2026-04-17/entry_rows.ndjson`
  - `results/research/ri_advisory_environment_fit/phase3_phasec_evidence_capture_v2_2026-04-17/capture_summary.json`
- restored proxy source:
  - `results/research/ri_advisory_environment_fit/phase3_proxy_coverage_audit_2026-04-17/materialized_proxy_rows.ndjson`
  - `results/research/ri_advisory_environment_fit/phase3_proxy_coverage_audit_2026-04-17/manifest.json`
  - `results/research/ri_advisory_environment_fit/phase3_proxy_coverage_audit_2026-04-17/proxy_surface.json`
- rerun boundary source:
  - `results/research/ri_advisory_environment_fit/phase3_provisional_evaluation_rerun_2026-04-17/manifest.json`
  - `results/research/ri_advisory_environment_fit/phase3_provisional_evaluation_rerun_2026-04-17/join_audit.json`
  - `docs/analysis/ri_advisory_environment_fit_phase3_post_rerun_label_authority_admissibility_2026-04-17.md`

### Join and shaping contract

The script must rebuild the same exact joined exploratory surface as the approved rerun:

1. join key must remain `join_key`
2. duplicate selector join keys must fail the run
3. duplicate restored-proxy join keys must fail the run
4. restored proxy rows without selector rows must fail the run
5. joined row count must equal restored proxy `materialized_row_count`
6. post-join proxy null counts must match the restored proxy source exactly

Only after that join passes may the dirty-research shaping begin.

### Allowed approximate labels

This slice may emit only explicitly approximate heuristic labels such as:

- `approx_supportive_proxy_label`
- `approx_hostile_proxy_label`
- `approx_ambiguous_proxy_label`
- `approx_non_evaluable_proxy_label`

These labels must be derived only from restored proxy fields and simple documented heuristic rules.
Approximate proxy labels are exploratory buckets only and must never be described as exact, Phase-2-faithful, runtime-valid, or promotion-bearing.

### Allowed heuristic inputs

Only the following restored proxy fields may be used for approximate-label shaping:

- `continuation_score`
- `fwd_16_atr`
- `mfe_16_atr`

Only the following selector-side field may be used for exploratory stratification:

- `decision_reliability_rank` or its direct pre-entry ingredients from the already admitted selector subset

### Explicitly forbidden shortcuts

- raw `total_pnl` sign as any approximate label shortcut
- any reconstruction of `pnl_delta`
- any synthetic `active_uplift_cohort_membership`
- any claim that the heuristic labels recover the exact Phase 2 contract
- any transition-axis promotion based on this slice

### Required outputs

- one join-audit artifact proving the joined exploratory surface still matches the rerun contract
- one heuristic-definition artifact recording the exact approximate label rules
- one approximate-label-surface artifact with counts by year and label class
- one bucket/crosstab artifact showing reliability-side structure against the approximate label classes
- one boundary manifest showing source artifacts/hashes, that only restored proxy fields were used for heuristic labeling, and that outputs remain `approximate`, `exploratory`, and `non-authoritative`
- one manifest stating clearly that the slice is exploratory, approximate, and non-authoritative
- one memo stating whether the dirty-research evidence shape adds enough insight to justify a later exact-label-authority follow-up

### Gates required

- `pre-commit run --files <packet> <tmp script> <analysis memo>`
- `pytest tests/backtest/test_runner_direct_includes_merged_config.py`
- `pytest tests/backtest/test_backtest_engine.py::test_engine_run_skip_champion_merge_does_not_load_champion`
- `pytest tests/backtest/test_backtest_determinism_smoke.py::test_backtest_engine_is_deterministic_across_two_runs`
- `pytest tests/utils/test_features_asof_cache_key_deterministic.py::test_compute_candles_hash_is_deterministic_across_pyhashseed`
- `pytest tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`
- bounded execution of the dirty-research script itself
- deterministic replay of the dirty-research script on identical inputs with stable summary/hash output

### Stop Conditions

- any failure of the exact join contract, in which case the slice must stop as `BLOCKED_DIRTY_RESEARCH_BOUNDARY_BREACH`
- any attempt to describe approximate labels as exact supportive/hostile outcomes
- any output text, column name, or conclusion that uses exact/supportive/hostile language without the explicit `approx_` framing required by this packet
- any need to touch `src/**`, `tests/**`, `config/**`, or runtime defaults/config semantics
- any evidence that the join surface no longer matches the approved rerun contract
- any use of raw `total_pnl`, reconstructed `pnl_delta`, or synthetic active-uplift membership
- any attempt to promote the mixed transition axis from this slice
- any runtime-facing recommendation, readiness claim, or promotion claim
- any boundary-breach artifact or conclusion that implies `phase4_opening=true` or `exact_label_authority=true`, in which case the slice must stop as `BLOCKED_DIRTY_RESEARCH_BOUNDARY_BREACH`

## Bottom line

This packet proposes one narrow next step only:

- shape a dirty-research reliability evidence surface with approximate labels under strict isolation and explicit non-authoritative marking

It does not authorize exact label authority, Phase 4, runtime integration, or production-clean claims.
