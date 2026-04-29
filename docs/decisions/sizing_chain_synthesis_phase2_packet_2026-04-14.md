# Sizing-chain synthesis — Phase 2 packet

Date: 2026-04-14
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: `proposed / docs-only / no-runtime-authority`

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md`
- **Category:** `obs`
- **Risk:** `MED` — why: this slice is docs-only, but it can still overclaim a sizing-based mechanism if survival and cluster-marginal evidence are fused too aggressively.
- **Required Path:** `Quick`
- **Objective:** Synthesize the current sizing-related evidence into one bounded driver ladder and decide whether the sizing chain materially narrows Genesis or whether it still remains subordinate to the broader `emergent_system_behavior` conclusion.
- **Candidate:** Phase 2 sizing-chain synthesis
- **Base SHA:** `ba1db8ac`

### Scope

- **Scope IN:**
  - `docs/decisions/sizing_chain_synthesis_phase2_packet_2026-04-14.md`
  - `docs/analysis/sizing_chain_synthesis_phase2_2026-04-14.md`
  - `plan/genesis_driver_identification_master_roadmap_2026-04-14.md`
  - `plan/feature_attribution_post_phase14_reactivation_roadmap_2026-04-02.md`
  - `docs/analysis/feature_attribution_post_phase14_rebaseline_reconciliation_2026-04-02.md`
  - `results/research/feature_attribution_v1/reports/fa_v1_full_admitted_units_synthesis_20260331_01.md`
  - `results/research/feature_attribution_v1/reports/fa_v1_cluster_implementation_handoff_20260331_01.md`
  - `docs/decisions/survival_boundary_phase4_packet_2026-04-01.md`
  - `results/research/fa_v2_adaptation_off/survival_boundary_summary.md`
  - `results/research/fa_v2_adaptation_off/EDGE_ORIGIN_REPORT.md`
- **Scope OUT:**
  - all files under `src/`
  - all files under `tests/`
  - all files under `config/`
  - all files under `scripts/`
  - all files under `results/`
  - `.github/agents/Codex53.agent.md`
  - any runtime/config authority changes
  - any trace regeneration or backtest reruns
  - any edits to locked Phase 4–14 artifacts
- **Expected changed files:**
  - `docs/decisions/sizing_chain_synthesis_phase2_packet_2026-04-14.md`
  - `docs/analysis/sizing_chain_synthesis_phase2_2026-04-14.md`
  - `plan/genesis_driver_identification_master_roadmap_2026-04-14.md`
- **Max files touched:** `3`

### Constraints

- docs-only; no code changes and no new artifact generation
- the synthesis may use only already generated or already tracked evidence
- survival-boundary evidence may be used only as an observational preservation boundary, not as proof of edge
- current-route cluster deltas may be used only as marginal evidence, not as runtime authority or standalone mechanism proof
- the synthesis must preserve that `emergent_system_behavior` remains the current default broader hypothesis unless the bounded sizing evidence genuinely beats it
- the memo must finish with exactly one conclusion from this closed set:
  - `sizing chain materially narrows Genesis`
  - `sizing chain matters but does not beat emergent_system_behavior`

### Required synthesis outcomes

The memo is complete only if it does all of the following:

1. maps the main sizing-related surfaces into a bounded driver ladder
2. assigns each surface one label from this closed set:
   - `direct driver candidate`
   - `risk-shaping contributor`
   - `harmful surface`
   - `confounded mover`
   - `inert on current route`
3. explains how survival-boundary evidence and current-route cluster evidence do and do not combine
4. states whether the sizing chain beats the current broader hypothesis or remains subordinate to it
5. identifies the next admissible move for the master roadmap

### Stop Conditions

- any wording that upgrades observational sizing evidence into exclusive edge proof
- any attempt to reinterpret current-route cluster deltas as direct runtime authority
- any scope drift into runtime changes, results regeneration, or unrelated agent/tooling files
- any conclusion that silently overwrites `emergent_system_behavior` without explicit bounded evidence

### Output required

- one docs-only packet
- one analysis memo with a bounded sizing-chain verdict
- one roadmap update reflecting whether Phase 2 is closed

## Bottom line

This slice exists to answer a narrower question than “what is the whole edge.”
It asks whether the existing survival, sizing-cluster, and harmful-threshold evidence is enough to elevate the sizing chain above a subsystem role.
If not, the sizing chain should be recorded as important but still subordinate to the broader system-level interpretation.
