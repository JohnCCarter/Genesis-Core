# RI advisory environment-fit Phase 3 proxy-coverage admissibility packet

Date: 2026-04-17
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: `active / docs-only / proxy-coverage admissibility decision`

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `branch:feature/ri-role-map-implementation-2026-03-24`
- **Category:** `docs`
- **Risk:** `LOW` — docs-only decision about whether the lane may open a bounded observational follow-up after the provisional slice stopped on `BLOCKED_PROXY_COVERAGE_GAP`; no runtime/config/test/results regeneration.
- **Required Path:** `Quick`
- **Constraints:** `NO BEHAVIOR CHANGE`
- **Objective:** decide whether the next admissible step is a bounded proxy-coverage / realized-metrics audit focused on the missing ATR-normalization anchor on capture-v2 rows, or whether evaluation-side Phase 3 work should stop here.
- **Candidate:** `RI advisory environment-fit Phase 3 proxy-coverage admissibility`
- **Base SHA:** `e16e3f9fd68500dc741f8edd9757c709e22bf595`

### Scope

- **Scope IN:**
  - `docs/decisions/ri_advisory_environment_fit_phase3_proxy_coverage_admissibility_packet_2026-04-17.md`
  - `docs/analysis/ri_advisory_environment_fit_phase3_proxy_coverage_admissibility_2026-04-17.md`
- **Scope OUT:**
  - `src/**`
  - `tests/**`
  - `config/**`
  - `tmp/**`
  - `results/**`
  - `artifacts/**`
  - any new score implementation
  - any proxy-materialization run
  - any capture rerun
  - any label reconstruction or Phase 2 contract rewrite
  - any runtime/default/authority change
- **Expected changed files:**
  - `docs/decisions/ri_advisory_environment_fit_phase3_proxy_coverage_admissibility_packet_2026-04-17.md`
  - `docs/analysis/ri_advisory_environment_fit_phase3_proxy_coverage_admissibility_2026-04-17.md`
- **Max files touched:** `2`

### Gates required

- `pre-commit run --files docs/decisions/ri_advisory_environment_fit_phase3_proxy_coverage_admissibility_packet_2026-04-17.md docs/analysis/ri_advisory_environment_fit_phase3_proxy_coverage_admissibility_2026-04-17.md`

### Allowed evidence inputs

- `docs/analysis/ri_advisory_environment_fit_phase2_label_taxonomy_2026-04-16.md`
- `docs/analysis/ri_advisory_environment_fit_phase3_post_capture_admissibility_2026-04-16.md`
- `docs/analysis/ri_advisory_environment_fit_phase3_post_capture_v2_baseline_admissibility_2026-04-17.md`
- `docs/analysis/ri_advisory_environment_fit_phase3_partial_baseline_label_gap_2026-04-17.md`
- `docs/analysis/ri_advisory_environment_fit_phase3_provisional_evaluation_2026-04-17.md`
- `tmp/ri_advisory_environment_fit_capture_v2_20260417.py`
- `tmp/ri_advisory_environment_fit_provisional_evaluation_20260417.py`
- `tmp/ri_advisory_environment_fit_capture_20260416.py`
- `tmp/current_atr_900_env_profile_20260416.py`
- `results/research/ri_advisory_environment_fit/phase3_phasec_evidence_capture_v2_2026-04-17/entry_rows.ndjson`
- `results/research/ri_advisory_environment_fit/phase3_provisional_evaluation_2026-04-17/proxy_surface.json`
- `results/research/ri_advisory_environment_fit/phase3_provisional_evaluation_2026-04-17/manifest.json`
- `results/research/ri_advisory_environment_fit/phase3_ri_evidence_capture_2026-04-16/entry_rows.ndjson`

`docs/analysis/ri_advisory_environment_fit_phase3_partial_baseline_label_gap_2026-04-17.md`
is the label-gap boundary source for this decision.
It is governance context only and not a required execution artifact for this slice.

### Required decision questions

The memo must answer at minimum:

1. is `BLOCKED_PROXY_COVERAGE_GAP` caused by a generalized evidence failure, or by a narrower missing normalization-anchor surface on the captured realized rows?
2. does the evidence support opening one bounded observational follow-up that audits proxy coverage specifically, rather than resuming any scoring work?
3. what exact claims remain forbidden even if such a follow-up opens?
4. what stop condition should end that follow-up if normalization-equivalence or admissibility cannot be shown cleanly?

### Stop Conditions

- any wording that treats provisional realized-outcome proxies as equivalent to the exact Phase 2 supportive/hostile contract
- any wording that treats `current_atr_used` as already-approved semantic replacement for `entry_atr` without a separate bounded audit
- any wording that authorizes renewed scoring, contradiction-year evaluation, or role-map implementation from this packet alone
- any wording that reopens `pnl_delta` reconstruction, synthetic `active_uplift_cohort_membership`, or raw `total_pnl` sign shortcuts
- any wording that authorizes runtime or capture-v2 code changes from this docs-only decision

## Bottom line

This packet authorizes one docs-only admissibility decision and nothing more.
It does not authorize new proxy materialization, new scoring, label substitution, capture reruns, or runtime integration.
