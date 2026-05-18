# SCPE / Phase C mixed replay non-portability boundary packet

Date: 2026-05-18
Branch: `feature/evidence-closeout-pilot`
Status: `decision-recorded / docs-only / non-authorizing`

This document records the current portability boundary for the broader SCPE / Phase C mixed replay family.
It grants no runtime, config-authority, paper/live, promotion, or carrier-materialization authority by itself.
It classifies current branch-state portability boundaries only; it does not rewrite or supersede historical April 2026 reports.

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md` via `feature/* -> RESEARCH`
- **Category:** `docs`
- **Risk:** `LOW` — why: this slice records one current-state dependency classification only; the main risk is accidentally implying either broader portability or a premature future carrier choice
- **Required Path:** `Quick path / docs-only decision packet`
- **Lane:** `Research-evidence` — why: this slice classifies the current carrier posture of one decision-bearing dependency family without reopening execution, results, or runtime surfaces
- **Objective:** record that the broader SCPE / Phase C mixed replay family remains non-portable at current branch state while preserving the already-bounded `defensive_probe` exception and a separate future reopen path
- **Base SHA:** `b788718657cfe7c4a7d9ec70adff98c4ecb0baa1`
- **Related artifacts:** `docs/analysis/diagnostics/deep_premortem_followup_phase_plan_feature_evidence_closeout_pilot_2026-05-15.md`, `docs/analysis/diagnostics/ignored_artifact_dependency_inventory_2026-05-15.md`, `docs/decisions/governance/scpe_defensive_probe_carrier_decision_packet_2026-05-15.md`, `docs/analysis/scpe_ri_v1/scpe_ri_v1_router_replay_script_promotion_report_2026-04-20.md`, `docs/analysis/scpe_ri_v1/scpe_ri_v1_selected_defensive_transition_window_audit_report_2026-04-20.md`, `docs/analysis/regime_intelligence/advisory_environment_fit/ri_advisory_environment_fit_phase3_carrier_materialization_admissibility_2026-04-16.md`

### Scope

- **Scope IN:** this one packet only; current-state portability classification for the broader SCPE / Phase C mixed replay family above the already-bounded `defensive_probe` pocket
- **Scope OUT:** edits to historical April 2026 reports; edits to `docs/analysis/diagnostics/ignored_artifact_dependency_inventory_2026-05-15.md`; edits to `docs/analysis/diagnostics/deep_premortem_followup_phase_plan_feature_evidence_closeout_pilot_2026-05-15.md`; all changes under `src/**`, `tests/**`, `config/**`, `scripts/**`, `results/**`, and `artifacts/**`; any carrier materialization; any new replay run; any runtime/default/paper-live/promotion language
- **Max files touched:** `1`

### Gates required

- targeted docs validation for this packet
- manual wording audit that the packet keeps the broader family non-portable at current branch state rather than implying permanent closure or future approval
- manual wording audit that the `defensive_probe` exception remains exact and local rather than widening broader SCPE replay authority

## Purpose

This packet answers one narrow question only:

- what portability status honestly applies to the broader SCPE / Phase C mixed replay family at current branch state, above the already-bounded `defensive_probe` exception?

## What changed in this slice

- the repo now records an explicit current-state classification for the broader SCPE / Phase C mixed replay family instead of leaving that family at an implied “partly tracked, probably reusable” posture
- the repo now states that the tracked SCPE replay-root surfaces and curated evaluation summary do **not** erase the still-ignored Phase C dependency upstream of later decision-bearing notes
- the repo now keeps the exact `defensive_probe` two-row pocket as a separately bounded exception only

## What did not change

- no source, test, config, script, results, or artifact surfaces changed
- no historical April 2026 report was rewritten as current guidance
- no future donor or carrier was selected here
- no broader portability claim was upgraded
- no runtime, paper/live, readiness, or promotion semantics changed

## Governing basis

### Observed

1. `docs/analysis/diagnostics/ignored_artifact_dependency_inventory_2026-05-15.md` ranks the **SCPE / Phase C mixed replay family** as the highest unresolved dependency root and says the smallest next admissible move is either one bounded carrier decision or one explicit non-portable classification.
2. `docs/analysis/diagnostics/deep_premortem_followup_phase_plan_feature_evidence_closeout_pilot_2026-05-15.md` says Phase 3 should land one bounded decision note rather than widening directly into implementation or runtime-adjacent work.
3. `docs/analysis/scpe_ri_v1/scpe_ri_v1_router_replay_script_promotion_report_2026-04-20.md` shows that the tracked `results/research/scpe_v1_ri/**` replay root is real and that one commit-safe summary artifact under `results/evaluation/**` was curated, but it keeps that slice replay-root-scoped and research-only.
4. `docs/analysis/scpe_ri_v1/scpe_ri_v1_selected_defensive_transition_window_audit_report_2026-04-20.md` still depends on ignored Phase C entry rows under `results/research/ri_advisory_environment_fit/phase3_phasec_evidence_capture_v2_2026-04-17/**` while also depending on the tracked SCPE replay root.
5. `docs/decisions/governance/scpe_defensive_probe_carrier_decision_packet_2026-05-15.md` already narrowed the only currently bounded SCPE-derived exception to the exact two-row `defensive_probe` pocket and explicitly stopped below broader SCPE replay-root authority.
6. `docs/analysis/regime_intelligence/advisory_environment_fit/ri_advisory_environment_fit_phase3_carrier_materialization_admissibility_2026-04-16.md` says `phaseC_oos_trial.json` is still a donor, not a carrier, and that any carrier-materialization path would need its own later bounded slice.

### Inferred

- the broader SCPE / Phase C mixed replay family remains mixed because its current decision-bearing chain still spans both tracked replay-root surfaces and ignored or local-only Phase C donor/capture surfaces
- the tracked `results/research/scpe_v1_ri/**` root and the curated `results/evaluation/scpe_ri_v1_router_replay_2026-04-20.json` summary are useful tracked anchors, but they are **not equivalent** to a portable carrier for the broader family
- the exact `defensive_probe` pocket can remain a separately bounded local exception without upgrading the broader family above it
- the cheapest honest current-state classification is therefore non-portable rather than provisional portability optimism

### Unverified in this packet

- whether a later bounded carrier-materialization slice should ever open for a broader SCPE / Phase C line
- whether `phaseC_oos_trial.json` or any other donor can later become a commit-safe carrier without semantic drift
- whether the broader family could ever justify `historical-trace-level` or `full-chain clean-checkout-level` wording after a later separately governed reopen
- whether any SCPE-derived line beyond the exact `defensive_probe` pocket should ever receive a stronger portability label

## Boundary decision

### Current standing conclusion

At current branch state, the broader **SCPE / Phase C mixed replay family remains `mixed / non-portable`**.

The tracked `results/research/scpe_v1_ri/**` replay root and the curated `results/evaluation/scpe_ri_v1_router_replay_2026-04-20.json` summary remain legitimate tracked comparison surfaces.
They do **not** erase, subsume, or silently upgrade the still-ignored Phase C dependency that remains upstream of later decision-bearing notes.

The broader family should therefore **not** currently be described as:

- `fixture-level`
- `historical-trace-level`
- `full-chain clean-checkout-level`

portable.

### Narrow exception retained

The only currently separated exception remains the exact `defensive_probe` pocket already bounded in:

- `docs/decisions/governance/scpe_defensive_probe_carrier_decision_packet_2026-05-15.md`

That exception remains:

- exact
- local
- concept/evidence-bounded
- non-authorizing

It does **not** promote the broader SCPE / Phase C mixed replay family above it.

### What this packet does not decide

This packet does **not**:

- choose a new donor or carrier for the broader family
- approve any carrier-materialization path
- reopen the historical April 2026 SCPE reports for rewriting
- claim that the broader family is permanently blocked from future reopen
- authorize runtime, config-authority, paper/live, readiness, or promotion language

## Hard stop and reopen rule

If a future slice needs any of the following, it must stop and reopen as a separate bounded packet:

- any donor or carrier choice for the broader SCPE / Phase C family
- any carrier materialization under `config/**`, `results/**`, `scripts/**`, or other non-docs surfaces
- any portability claim stronger than the current non-portable classification
- any widening beyond the exact `defensive_probe` exception
- any runtime, default, paper/live, readiness, or promotion semantics

## Bottom line

The honest Phase 3 move at current branch state is classification, not premature carrier choice.

The broader **SCPE / Phase C mixed replay family remains non-portable**, because its current decision-bearing chain still mixes tracked replay-root surfaces with ignored or local-only Phase C dependency surfaces.
Only the exact `defensive_probe` pocket remains separately bounded as a local exception.
Any broader carrier or stronger portability claim must reopen separately.
