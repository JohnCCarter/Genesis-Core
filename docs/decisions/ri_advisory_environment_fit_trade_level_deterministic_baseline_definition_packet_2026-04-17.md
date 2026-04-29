# RI advisory environment-fit trade-level deterministic baseline definition packet

Date: 2026-04-17
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: `active / docs-only / trade-level deterministic baseline definition`

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `branch:feature/ri-role-map-implementation-2026-03-24`
- **Category:** `docs`
- **Risk:** `LOW` — docs-only baseline-definition slice for the new trade-level-authority lane; no runtime/config/test/results/artifact mutation.
- **Required Path:** `Quick`
- **Constraints:** `NO BEHAVIOR CHANGE`
- **Objective:** define the first bounded deterministic baseline for the RI trade-level-authority lane, including the rule-order for trade-level labels, the rule-order for bounded entry-row mapping outputs, the mandatory reporting surface, and the immediate fail-closed checks that must remain in force before any implementation begins.
- **Candidate:** `RI advisory environment-fit trade-level deterministic baseline definition`
- **Base SHA:** `b30e6fbac3839a2ced1c1c18474f5545779962b7`
- **Skill Usage:** no suitable existing skill; no skill-based process claim is made in this packet.

### Scope

- **Scope IN:**
  - `docs/decisions/ri_advisory_environment_fit_trade_level_deterministic_baseline_definition_packet_2026-04-17.md`
  - `docs/analysis/ri_advisory_environment_fit_trade_level_deterministic_baseline_definition_2026-04-17.md`
- **Scope OUT:**
  - `src/**`
  - `tests/**`
  - `config/**`
  - `tmp/**`
  - `results/**`
  - `artifacts/**`
  - any trade-label implementation
  - any row-mapping implementation
  - any deterministic baseline implementation
  - any ML/model work
  - any runtime integration
  - any Phase 4 opening
  - any claim of restored exact row-level authority
- **Expected changed files:**
  - `docs/decisions/ri_advisory_environment_fit_trade_level_deterministic_baseline_definition_packet_2026-04-17.md`
  - `docs/analysis/ri_advisory_environment_fit_trade_level_deterministic_baseline_definition_2026-04-17.md`
- **Max files touched:** `2`

### Gates required

- `pre-commit run --files docs/decisions/ri_advisory_environment_fit_trade_level_deterministic_baseline_definition_packet_2026-04-17.md docs/analysis/ri_advisory_environment_fit_trade_level_deterministic_baseline_definition_2026-04-17.md`

### Allowed evidence inputs

- `plan/ri_advisory_environment_fit_roadmap_2026-04-16.md`
- `docs/analysis/ri_advisory_environment_fit_phase2_label_taxonomy_2026-04-16.md`
- `docs/analysis/ri_advisory_environment_fit_phase3_direct_baseline_admissibility_2026-04-16.md`
- `docs/analysis/ri_advisory_environment_fit_phase3_post_capture_v2_baseline_admissibility_2026-04-17.md`
- `docs/analysis/ri_advisory_environment_fit_trade_level_authority_admissibility_2026-04-17.md`
- `docs/analysis/ri_advisory_environment_fit_trade_level_label_mapping_contract_2026-04-17.md`
- `docs/analysis/ri_advisory_environment_fit_trade_level_evidence_family_leakage_boundary_2026-04-17.md`
- `docs/analysis/ri_advisory_environment_fit_trade_level_deterministic_baseline_admissibility_2026-04-17.md`
- `docs/decisions/ri_advisory_environment_fit_trade_level_authority_admissibility_packet_2026-04-17.md`
- `docs/decisions/ri_advisory_environment_fit_trade_level_label_mapping_contract_packet_2026-04-17.md`
- `docs/decisions/ri_advisory_environment_fit_trade_level_evidence_family_leakage_boundary_packet_2026-04-17.md`
- `docs/decisions/ri_advisory_environment_fit_trade_level_deterministic_baseline_admissibility_packet_2026-04-17.md`

### Required decision questions

The memo must answer at minimum:

1. what exact deterministic rule order defines the first trade-level label surface?
2. what exact deterministic output domains and rule order define the first bounded entry-row mapping surface?
3. what reporting surface is mandatory before any implementation can be reviewed honestly?
4. what fail-closed checks must stop the lane if the baseline can be defined only by weakening coverage, leakage, contradiction-year, or transition discipline?
5. what is the narrowest next step after the definition is fixed?

### Required boundary statements

The memo must state explicitly that:

- trade-level label rules and entry-row mapping rules remain different surfaces
- trade-level labels may use realized-trade evidence families only
- row mapping may use entry-time field families only
- no row-mapping rule may import `total_pnl`, `pnl_delta`, `mfe_16_atr`, `mae_16_atr`, `fwd_*`, `continuation_score`, or future cohort membership
- supportive and hostile trade labels may not be defined from raw realized P&L sign alone
- `transition_trade_outcome` must remain narrow and evidence-based rather than a junk drawer
- `coverage_state` and `authority_strength` must remain explicit outputs rather than hidden internals
- `2025` remains the mandatory contradiction-year check
- this packet does not authorize implementation, ML, runtime integration, or Phase 4

### Stop Conditions

- any wording that treats mapped row outputs as restored exact row-level authority
- any wording that allows post-entry evidence into row-mapping or scoring-time inputs
- any wording that allows raw realized P&L sign alone to define supportive or hostile trade labels
- any wording that hides unsupported coverage, weak authority, or uncertainty for neat reporting
- any wording that opens implementation, runtime integration, ML, Phase 4, or promotion framing from this packet alone

## Bottom line

This packet authorizes one docs-only trade-level deterministic baseline-definition slice.
It does not authorize implementation, runtime changes, ML, or any claim that exact row-level authority has been recovered.
