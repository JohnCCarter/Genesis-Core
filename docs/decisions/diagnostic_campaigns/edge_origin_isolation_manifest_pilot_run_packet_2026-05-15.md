# Edge-origin isolation manifest pilot run — packet

Date: 2026-05-15
Branch: `feature/evidence-closeout-pilot`
Status: `active bounded run packet / research-evidence / no runtime authority`

> Current status note:
>
> - The bounded pilot run authorized by this packet was executed on `feature/evidence-closeout-pilot` at base `4dc9fbba`.
> - The resulting manifest-backed artifact root lives under `results/research/fa_v2_adaptation_off/phase10_edge_origin_isolation_manifest_pilot_20260515/` and is cited by `docs/analysis/diagnostics/edge_origin_isolation_manifest_claim_pilot_2026-05-15.md`.

This document authorizes one bounded research-evidence run that materializes a fresh `edge_origin_isolation` output root with the new deterministic `manifest.json` and then records a claim-bearing pilot note against that exact artifact set.

It does **not** authorize runtime, strategy, config-authority, paper/live, promotion, or champion changes.

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md` via branch mapping for `feature/evidence-closeout-pilot`
- **Category:** `obs`
- **Risk:** `LOW-MED` — why: this slice executes read-only evidence tooling against fixed historical trace artifacts and writes a new bounded output root plus one analysis note; the main risk is overstating observational Phase 10 outputs as authority or mutating historical output roots
- **Required Path:** `Lite`
- **Lane:** `Research-evidence` — why: the target is a deterministic evidence closeout plus a claim-bearing note, not runtime integration
- **Objective:** materialize one fresh manifest-bearing edge-origin artifact root and use it as the next pilot note for the claim-header discipline
- **Candidate:** `edge-origin manifest-backed claim-bearing pilot note`
- **Base SHA:** `4dc9fbba`
- **Skill Usage:** consulted the repository evidence-closeout spec `.github/skills/slice_evidence_handoff.json` as a checklist aid for exact scope, gates, and closeout evidence; this does not create authority or replace required review/gate judgment

### Scope

- **Scope IN:**
  - `docs/decisions/diagnostic_campaigns/edge_origin_isolation_manifest_pilot_run_packet_2026-05-15.md`
  - `results/research/fa_v2_adaptation_off/trace_baseline_current.json`
  - `results/research/fa_v2_adaptation_off/trace_adaptation_off.json`
  - `results/research/fa_v2_adaptation_off/phase10_edge_origin_isolation_manifest_pilot_20260515/execution_attribution.json`
  - `results/research/fa_v2_adaptation_off/phase10_edge_origin_isolation_manifest_pilot_20260515/execution_summary.md`
  - `results/research/fa_v2_adaptation_off/phase10_edge_origin_isolation_manifest_pilot_20260515/sizing_attribution.json`
  - `results/research/fa_v2_adaptation_off/phase10_edge_origin_isolation_manifest_pilot_20260515/sizing_summary.md`
  - `results/research/fa_v2_adaptation_off/phase10_edge_origin_isolation_manifest_pilot_20260515/path_dependency.json`
  - `results/research/fa_v2_adaptation_off/phase10_edge_origin_isolation_manifest_pilot_20260515/path_summary.md`
  - `results/research/fa_v2_adaptation_off/phase10_edge_origin_isolation_manifest_pilot_20260515/selection_attribution.json`
  - `results/research/fa_v2_adaptation_off/phase10_edge_origin_isolation_manifest_pilot_20260515/selection_summary.md`
  - `results/research/fa_v2_adaptation_off/phase10_edge_origin_isolation_manifest_pilot_20260515/counterfactual_matrix.json`
  - `results/research/fa_v2_adaptation_off/phase10_edge_origin_isolation_manifest_pilot_20260515/audit_phase10_determinism.json`
  - `results/research/fa_v2_adaptation_off/phase10_edge_origin_isolation_manifest_pilot_20260515/manifest.json`
  - `docs/analysis/diagnostics/edge_origin_isolation_manifest_claim_pilot_2026-05-15.md`
- **Scope OUT:**
  - all files under `src/`
  - all files under `tests/`
  - all files under `config/`
  - all edits to historical `phase10_edge_origin_isolation/`
  - any rerun or regeneration of baseline traces
  - any runtime/config-authority/default changes
  - any claim that the observational Phase 10 surface attests runtime causality or readiness
- **Expected changed files:**
  - `docs/decisions/diagnostic_campaigns/edge_origin_isolation_manifest_pilot_run_packet_2026-05-15.md`
  - `results/research/fa_v2_adaptation_off/phase10_edge_origin_isolation_manifest_pilot_20260515/execution_attribution.json`
  - `results/research/fa_v2_adaptation_off/phase10_edge_origin_isolation_manifest_pilot_20260515/execution_summary.md`
  - `results/research/fa_v2_adaptation_off/phase10_edge_origin_isolation_manifest_pilot_20260515/sizing_attribution.json`
  - `results/research/fa_v2_adaptation_off/phase10_edge_origin_isolation_manifest_pilot_20260515/sizing_summary.md`
  - `results/research/fa_v2_adaptation_off/phase10_edge_origin_isolation_manifest_pilot_20260515/path_dependency.json`
  - `results/research/fa_v2_adaptation_off/phase10_edge_origin_isolation_manifest_pilot_20260515/path_summary.md`
  - `results/research/fa_v2_adaptation_off/phase10_edge_origin_isolation_manifest_pilot_20260515/selection_attribution.json`
  - `results/research/fa_v2_adaptation_off/phase10_edge_origin_isolation_manifest_pilot_20260515/selection_summary.md`
  - `results/research/fa_v2_adaptation_off/phase10_edge_origin_isolation_manifest_pilot_20260515/counterfactual_matrix.json`
  - `results/research/fa_v2_adaptation_off/phase10_edge_origin_isolation_manifest_pilot_20260515/audit_phase10_determinism.json`
  - `results/research/fa_v2_adaptation_off/phase10_edge_origin_isolation_manifest_pilot_20260515/manifest.json`
  - `docs/analysis/diagnostics/edge_origin_isolation_manifest_claim_pilot_2026-05-15.md`
- **Max files touched:** `13`

### Constraints

- run-only for the evidence artifacts; no code edits are authorized by this packet
- input traces are fixed at:
  - `results/research/fa_v2_adaptation_off/trace_baseline_current.json`
  - `results/research/fa_v2_adaptation_off/trace_adaptation_off.json`
- output root is fixed at `results/research/fa_v2_adaptation_off/phase10_edge_origin_isolation_manifest_pilot_20260515/`
- the historical `phase10_edge_origin_isolation/` root must remain untouched
- the note must use the claim header and keep `observed`, `inferred`, and `unverified` separate
- the note must keep the observational-only boundary explicit and must not claim runtime causality, readiness, or promotion authority

### Gates required

- CLI run of `scripts/analyze/edge_origin_isolation.py` against the fixed two input traces and fixed new output root
- `audit_phase10_determinism.json` must report `match = true`
- output file set must equal:
  - `execution_attribution.json`
  - `execution_summary.md`
  - `sizing_attribution.json`
  - `sizing_summary.md`
  - `path_dependency.json`
  - `path_summary.md`
  - `selection_attribution.json`
  - `selection_summary.md`
  - `counterfactual_matrix.json`
  - `audit_phase10_determinism.json`
  - `manifest.json`
- `manifest.json` must record stable input hashes for both locked inputs plus a stable non-self hash inventory for the other approved outputs
- the claim-bearing note must cite the exact artifact root and keep a short explicit non-authority boundary

### Stop Conditions

- any attempt to write into the historical `phase10_edge_origin_isolation/` root
- any determinism mismatch in the generated audit output
- any unexpected file in the new output root beyond the eleven approved outputs
- any need to mutate runtime, strategy, config-authority, or trace-production surfaces
- any wording drift that treats observational Phase 10 outputs as runtime or promotion authority

## Bottom line

This slice is the next practical pilot of the claim-bearing evidence discipline: one fresh manifest-backed edge-origin artifact run plus one bounded note that cites exactly what was observed and what remains out of scope.
