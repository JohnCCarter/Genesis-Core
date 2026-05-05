# RI advisory environment-fit trade-level deterministic baseline admissibility packet

Date: 2026-04-17
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: `active / docs-only / trade-level deterministic baseline admissibility decision`

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `branch:feature/ri-role-map-implementation-2026-03-24`
- **Category:** `docs`
- **Risk:** `LOW` — docs-only admissibility decision for the new trade-level-authority lane; no runtime/config/test/results/artifact mutation.
- **Required Path:** `Quick`
- **Constraints:** `NO BEHAVIOR CHANGE`
- **Objective:** decide whether the new RI trade-level-authority lane now has enough contract structure to open one bounded deterministic baseline that assigns trade-level authority labels and bounded entry-row mapping outputs under explicit coverage, uncertainty, and contradiction-year discipline.
- **Candidate:** `RI advisory environment-fit trade-level deterministic baseline admissibility`
- **Base SHA:** `b30e6fbac3839a2ced1c1c18474f5545779962b7`
- **Skill Usage:** no suitable existing skill; no skill-based process claim is made in this packet.

### Scope

- **Scope IN:**
  - `docs/decisions/regime_intelligence/advisory_environment_fit/ri_advisory_environment_fit_trade_level_deterministic_baseline_admissibility_packet_2026-04-17.md`
  - `docs/analysis/regime_intelligence/advisory_environment_fit/ri_advisory_environment_fit_trade_level_deterministic_baseline_admissibility_2026-04-17.md`
- **Scope OUT:**
  - `src/**`
  - `tests/**`
  - `config/**`
  - `tmp/**`
  - `results/**`
  - `artifacts/**`
  - any trade-label implementation
  - any mapping algorithm implementation
  - any deterministic baseline implementation
  - any ML/model work
  - any runtime integration
  - any Phase 4 opening
  - any claim of restored exact row-level authority
- **Expected changed files:**
  - `docs/decisions/regime_intelligence/advisory_environment_fit/ri_advisory_environment_fit_trade_level_deterministic_baseline_admissibility_packet_2026-04-17.md`
  - `docs/analysis/regime_intelligence/advisory_environment_fit/ri_advisory_environment_fit_trade_level_deterministic_baseline_admissibility_2026-04-17.md`
- **Max files touched:** `2`

### Gates required

- `pre-commit run --files docs/decisions/regime_intelligence/advisory_environment_fit/ri_advisory_environment_fit_trade_level_deterministic_baseline_admissibility_packet_2026-04-17.md docs/analysis/regime_intelligence/advisory_environment_fit/ri_advisory_environment_fit_trade_level_deterministic_baseline_admissibility_2026-04-17.md`

### Allowed evidence inputs

- `plan/ri_advisory_environment_fit_roadmap_2026-04-16.md`
- `docs/analysis/regime_intelligence/advisory_environment_fit/ri_advisory_environment_fit_phase2_label_taxonomy_2026-04-16.md`
- `docs/analysis/regime_intelligence/advisory_environment_fit/ri_advisory_environment_fit_phase3_direct_baseline_admissibility_2026-04-16.md`
- `docs/analysis/regime_intelligence/advisory_environment_fit/ri_advisory_environment_fit_phase3_post_capture_v2_baseline_admissibility_2026-04-17.md`
- `docs/analysis/regime_intelligence/advisory_environment_fit/ri_advisory_environment_fit_trade_level_authority_admissibility_2026-04-17.md`
- `docs/analysis/regime_intelligence/advisory_environment_fit/ri_advisory_environment_fit_trade_level_label_mapping_contract_2026-04-17.md`
- `docs/analysis/regime_intelligence/advisory_environment_fit/ri_advisory_environment_fit_trade_level_evidence_family_leakage_boundary_2026-04-17.md`
- `docs/decisions/regime_intelligence/advisory_environment_fit/ri_advisory_environment_fit_trade_level_authority_admissibility_packet_2026-04-17.md`
- `docs/decisions/regime_intelligence/advisory_environment_fit/ri_advisory_environment_fit_trade_level_label_mapping_contract_packet_2026-04-17.md`
- `docs/decisions/regime_intelligence/advisory_environment_fit/ri_advisory_environment_fit_trade_level_evidence_family_leakage_boundary_packet_2026-04-17.md`

### Required decision questions

The memo must answer at minimum:

1. does the new trade-level lane now have enough contract structure to open one bounded deterministic baseline at all?
2. if yes, what exact baseline surfaces are admissible:
   - trade-level authority labels,
   - entry-row mapping outputs,
   - coverage / uncertainty reporting?
3. what must remain explicitly out of scope for that baseline, especially around exact row-level authority, ML, runtime integration, and full market-role claims?
4. what failure classes must the first deterministic baseline report immediately if it is opened?
5. if the contract is still insufficient, what is the honest stop condition instead of jumping to formulas?

### Required boundary statements

The memo must state explicitly that:

- admissibility of a deterministic baseline does not mean the old exact row-level authority problem is solved
- trade-level labels and entry-row mapping outputs remain different surfaces
- row mapping must remain entry-time only and may not import post-entry evidence
- unsupported / weakly anchored rows and trades must remain visible rather than forced into complete directional coverage
- `2025` remains a mandatory contradiction-year check
- any first deterministic baseline remains bounded, advisory-only, and non-runtime
- this packet does not authorize implementation, ML, runtime integration, or Phase 4

### Stop Conditions

- any wording that treats a deterministic baseline as restored exact Phase-2-faithful row-level authority
- any wording that allows post-entry path or outcome evidence into row mapping or scoring-time inputs
- any wording that opens ML before a deterministic baseline has been both defined and pressure-tested on `2025`
- any wording that hides unsupported coverage, weak authority strength, or uncertainty for neat reporting
- any wording that opens runtime integration, Phase 4, or promotion framing from this packet alone

## Bottom line

This packet authorizes one docs-only deterministic-baseline admissibility decision for the new trade-level RI lane.
It does not authorize implementation, runtime changes, ML, or any claim that exact row-level authority has been recovered.
