# RI advisory environment-fit trade-level label mapping contract packet

Date: 2026-04-17
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: `active / docs-only / trade-level label and mapping contract`

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `branch:feature/ri-role-map-implementation-2026-03-24`
- **Category:** `docs`
- **Risk:** `LOW` — docs-only definitional slice for a new trade-level-authority lane; no runtime/config/test/results/artifact mutation.
- **Required Path:** `Quick`
- **Constraints:** `NO BEHAVIOR CHANGE`
- **Objective:** define the minimal admissible trade-level authority labels and the minimal admissible entry-row mapping outputs for the RI advisory pivot, while making partial coverage, uncertainty, and contradiction-year handling explicit and fail-closed.
- **Candidate:** `RI advisory environment-fit trade-level label mapping contract`
- **Base SHA:** `e16e3f9fd68500dc741f8edd9757c709e22bf595`
- **Skill Usage:** no suitable existing skill; no skill-based process claim is made in this packet.

### Scope

- **Scope IN:**
  - `docs/decisions/regime_intelligence/advisory_environment_fit/ri_advisory_environment_fit_trade_level_label_mapping_contract_packet_2026-04-17.md`
  - `docs/analysis/regime_intelligence/advisory_environment_fit/ri_advisory_environment_fit_trade_level_label_mapping_contract_2026-04-17.md`
- **Scope OUT:**
  - `src/**`
  - `tests/**`
  - `config/**`
  - `tmp/**`
  - `results/**`
  - `artifacts/**`
  - any trade-level label implementation
  - any mapping algorithm implementation
  - any deterministic baseline implementation
  - any ML/model work
  - any runtime integration
  - any claim of restored exact row-level authority
- **Expected changed files:**
  - `docs/decisions/regime_intelligence/advisory_environment_fit/ri_advisory_environment_fit_trade_level_label_mapping_contract_packet_2026-04-17.md`
  - `docs/analysis/regime_intelligence/advisory_environment_fit/ri_advisory_environment_fit_trade_level_label_mapping_contract_2026-04-17.md`
- **Max files touched:** `2`

### Gates required

- `pre-commit run --files docs/decisions/regime_intelligence/advisory_environment_fit/ri_advisory_environment_fit_trade_level_label_mapping_contract_packet_2026-04-17.md docs/analysis/regime_intelligence/advisory_environment_fit/ri_advisory_environment_fit_trade_level_label_mapping_contract_2026-04-17.md`

### Allowed evidence inputs

- `plan/ri_advisory_environment_fit_roadmap_2026-04-16.md`
- `docs/analysis/regime_intelligence/advisory_environment_fit/ri_advisory_environment_fit_phase2_label_taxonomy_2026-04-16.md`
- `docs/analysis/regime_intelligence/advisory_environment_fit/ri_advisory_environment_fit_phase3_partial_baseline_label_gap_2026-04-17.md`
- `docs/analysis/regime_intelligence/advisory_environment_fit/ri_advisory_environment_fit_phase3_provisional_evaluation_admissibility_2026-04-17.md`
- `docs/analysis/regime_intelligence/advisory_environment_fit/ri_advisory_environment_fit_phase3_reliability_exact_label_authority_preflight_2026-04-17.md`
- `docs/analysis/regime_intelligence/advisory_environment_fit/ri_advisory_environment_fit_phase3_post_exact_label_authority_preflight_admissibility_2026-04-17.md`
- `docs/analysis/regime_intelligence/advisory_environment_fit/ri_advisory_environment_fit_phase3_materially_different_surface_inventory_2026-04-17.md`
- `docs/analysis/regime_intelligence/advisory_environment_fit/ri_advisory_environment_fit_trade_level_authority_admissibility_2026-04-17.md`
- `docs/decisions/regime_intelligence/advisory_environment_fit/ri_advisory_environment_fit_trade_level_authority_admissibility_packet_2026-04-17.md`

### Required decision questions

The memo must answer at minimum:

1. what minimal trade-level authority labels are admissible for the new lane?
2. what kinds of entry-row outputs may a later mapping emit without pretending to restore exact row-level authority?
3. how must partial coverage, uncertainty, and unsupported rows be reported?
4. which shortcut paths remain forbidden, especially around raw realized P&L, leakage, and deterministic row relabeling?
5. what narrow next step becomes admissible after this contract is fixed?

### Required boundary statements

The memo must state explicitly that:

- trade-level labels are authority labels and entry-row mapping outputs are not the same thing
- entry rows remain the scoring-time surface
- no entry row may be described as having restored exact Phase-2-faithful authority unless a later separate governed slice proves that explicitly
- partial coverage must remain explicit and may not be reframed as full row coverage
- unsupported or non-evaluable rows/trades must remain visible rather than forced into supportive/hostile buckets
- `2025` remains a mandatory contradiction-year check for any future deterministic baseline in this lane
- this packet does not authorize implementation, ML, runtime integration, or Phase 4

### Stop Conditions

- any wording that collapses trade-level authority labels and entry-row mapping outputs into the same thing
- any wording that treats raw `total_pnl` sign alone as a sufficient trade-level authority label
- any wording that describes mapped row outputs as restored exact row-level authority
- any wording that removes uncertainty, coverage state, or unsupported-state reporting
- any wording that authorizes implementation, ML, runtime integration, or score promotion from this packet alone

## Bottom line

This packet authorizes one docs-only trade-level label and mapping contract slice.
It does not authorize implementation, runtime changes, ML, or any claim that exact row-level authority has been recovered.
