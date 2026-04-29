# RI advisory environment-fit Phase 3 carrier-materialization admissibility packet

Date: 2026-04-16
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: `active / docs-only / carrier-materialization admissibility decision`

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `branch:feature/ri-role-map-implementation-2026-03-24`
- **Category:** `docs`
- **Risk:** `LOW` — docs-only admissibility decision about whether one clarity-on RI optimizer artifact may be materialized into a fixed research carrier in a later slice; no runtime/config/test changes and no artifact regeneration.
- **Required Path:** `Quick`
- **Constraints:** `NO BEHAVIOR CHANGE`
- **Objective:** decide whether a bounded follow-up slice may materialize one specific clarity-on RI optimizer artifact into a fixed research carrier without changing defaults or blurring artifact-vs-carrier semantics.
- **Candidate:** `RI advisory environment-fit Phase 3 carrier materialization admissibility`
- **Base SHA:** `e16e3f9fd68500dc741f8edd9757c709e22bf595`

### Scope

- **Scope IN:**
  - `docs/decisions/ri_advisory_environment_fit_phase3_carrier_materialization_admissibility_packet_2026-04-16.md`
  - `docs/analysis/ri_advisory_environment_fit_phase3_carrier_materialization_admissibility_2026-04-16.md`
- **Scope OUT:**
  - `src/**`
  - `tests/**`
  - `config/**`
  - `tmp/**`
  - `results/**`
  - any actual carrier creation or conversion work
  - any new capture run
  - any score implementation
  - any ML/model work
- **Expected changed files:**
  - `docs/decisions/ri_advisory_environment_fit_phase3_carrier_materialization_admissibility_packet_2026-04-16.md`
  - `docs/analysis/ri_advisory_environment_fit_phase3_carrier_materialization_admissibility_2026-04-16.md`
- **Max files touched:** `2`

### Gates required

- `pre-commit run --files docs/decisions/ri_advisory_environment_fit_phase3_carrier_materialization_admissibility_packet_2026-04-16.md docs/analysis/ri_advisory_environment_fit_phase3_carrier_materialization_admissibility_2026-04-16.md`

### Stop Conditions

- any wording that upgrades `phaseC_oos_trial.json` into a fixed carrier by declaration alone
- any wording that authorizes config creation or carrier capture from this packet alone
- any wording that treats materialization as behavior-neutral without explicit invariants
- any wording that reopens baseline authoring before a materialized carrier exists

### Output required

- one docs-only packet
- one bounded admissibility memo
- one explicit verdict on whether a future carrier-materialization implementation slice is allowed
- one explicit invariant list that such a future slice must obey

## Allowed evidence inputs

- `docs/analysis/ri_advisory_environment_fit_phase3_carrier_adequacy_2026-04-16.md`
- `config/strategy/candidates/3h/tBTCUSD_3h_slice8_runtime_bridge_20260326.json`
- `config/optimizer/3h/phased_v3/best_trials/phaseC_oos_trial.json`
- `config/optimizer/3h/phased_v3/best_trials/phaseB_v2_best_trial.json`
- `config/optimizer/3h/phased_v3/PHASED_V3_RESULTS.md`
- `docs/analysis/regime_intelligence_phase_bc_rerun_plan_2026-03-13.md`

## Required decision questions

The memo must answer at minimum:

1. is `phaseC_oos_trial.json` specific enough, stable enough, and RI-aligned enough to justify a later bounded carrier-materialization slice?
2. what exact semantics must remain unchanged if such materialization happens?
3. does the next implementation slice need to create a new fixed carrier first before any capture v2 can open?
4. if the required invariants are too strong to satisfy cleanly, should the lane stop instead?

## Bottom line

This packet authorizes one docs-only carrier-materialization admissibility decision and nothing more.
Its job is to decide whether the roadmap may open a later, separate implementation slice to create a fixed research carrier from one identified RI donor artifact.
