# Execution proxy manifest pilot run — packet

Date: 2026-05-15
Branch: `feature/editor-worker-orchestrator`
Status: `historical bounded run packet / research-evidence provenance / no runtime authority`

> Current status note:
>
> - The bounded pilot run authorized by this packet was executed on `feature/editor-worker-orchestrator` at base `ba6955a2` before the later branch split.
> - This file is now preserved on `feature/evidence-closeout-pilot` as run-governance provenance for the first manifest-backed claim-bearing pilot note.

This document authorizes one bounded research-evidence run that materializes a fresh `execution_proxy_evidence` output root with the new deterministic `manifest.json` and then records a claim-bearing pilot note against that exact artifact set.

It does **not** authorize runtime, strategy, config-authority, paper/live, promotion, or champion changes.

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md` via branch mapping for `feature/editor-worker-orchestrator`
- **Category:** `obs`
- **Risk:** `LOW-MED` — why: this slice executes read-only evidence tooling against a fixed historical trace and writes a new bounded output root plus one analysis note; the main risk is overstating proxy evidence as execution authority or mutating historical output roots
- **Required Path:** `Lite`
- **Lane:** `Research-evidence` — why: the target is a deterministic evidence closeout plus a claim-bearing note, not runtime integration
- **Objective:** materialize one fresh manifest-bearing execution-proxy artifact root and use it as the first pilot note for the new claim-header discipline
- **Candidate:** `execution_proxy manifest-backed claim-bearing pilot note`
- **Base SHA:** `ba6955a2`
- **Skill Usage:** consulted the repository evidence-closeout spec `.github/skills/slice_evidence_handoff.json` as a checklist aid for exact scope, gates, and closeout evidence; this does not create authority or replace required review/gate judgment

### Scope

- **Scope IN:**
  - `docs/decisions/diagnostic_campaigns/execution_proxy_manifest_pilot_run_packet_2026-05-15.md`
  - `results/research/fa_v2_adaptation_off/trace_baseline_current.json`
  - `results/research/fa_v2_adaptation_off/phase10_execution_proxy_evidence_manifest_pilot_20260515/execution_proxy_evidence.json`
  - `results/research/fa_v2_adaptation_off/phase10_execution_proxy_evidence_manifest_pilot_20260515/execution_proxy_summary.md`
  - `results/research/fa_v2_adaptation_off/phase10_execution_proxy_evidence_manifest_pilot_20260515/audit_execution_proxy_determinism.json`
  - `results/research/fa_v2_adaptation_off/phase10_execution_proxy_evidence_manifest_pilot_20260515/manifest.json`
  - `docs/analysis/diagnostics/execution_proxy_manifest_claim_pilot_2026-05-15.md`
- **Scope OUT:**
  - all files under `src/`
  - all files under `tests/`
  - all files under `config/`
  - all edits to locked historical `phase10_execution_proxy_evidence/`
  - any rerun or regeneration of baseline traces
  - any runtime/config-authority/default changes
  - any claim that proxy evidence attests realized execution quality
- **Expected changed files:**
  - `docs/decisions/diagnostic_campaigns/execution_proxy_manifest_pilot_run_packet_2026-05-15.md`
  - `results/research/fa_v2_adaptation_off/phase10_execution_proxy_evidence_manifest_pilot_20260515/execution_proxy_evidence.json`
  - `results/research/fa_v2_adaptation_off/phase10_execution_proxy_evidence_manifest_pilot_20260515/execution_proxy_summary.md`
  - `results/research/fa_v2_adaptation_off/phase10_execution_proxy_evidence_manifest_pilot_20260515/audit_execution_proxy_determinism.json`
  - `results/research/fa_v2_adaptation_off/phase10_execution_proxy_evidence_manifest_pilot_20260515/manifest.json`
  - `docs/analysis/diagnostics/execution_proxy_manifest_claim_pilot_2026-05-15.md`
- **Max files touched:** `6`

### Constraints

- run-only for the evidence artifacts; no code edits are authorized by this packet
- input trace is fixed at `results/research/fa_v2_adaptation_off/trace_baseline_current.json`
- output root is fixed at `results/research/fa_v2_adaptation_off/phase10_execution_proxy_evidence_manifest_pilot_20260515/`
- the historical `phase10_execution_proxy_evidence/` root must remain untouched
- the note must use the claim header and keep `observed`, `inferred`, and `unverified` separate
- the note must keep the proxy-only boundary explicit and must not claim realized execution, slippage, latency, or queue-position authority

### Gates required

- CLI run of `scripts/analyze/execution_proxy_evidence.py` against the fixed input trace and fixed new output root
- `audit_execution_proxy_determinism.json` must report `match = true`
- output file set must equal:
  - `execution_proxy_evidence.json`
  - `execution_proxy_summary.md`
  - `audit_execution_proxy_determinism.json`
  - `manifest.json`
- `manifest.json` must record a stable non-self hash inventory for the other approved outputs
- the claim-bearing note must cite the exact artifact root and keep a short explicit non-authority boundary

### Stop Conditions

- any attempt to write into the historical `phase10_execution_proxy_evidence/` root
- any determinism mismatch in the generated audit output
- any unexpected file in the new output root beyond the four approved outputs
- any need to mutate runtime, strategy, config-authority, or trace-production surfaces
- any wording drift that treats proxy evidence as realized execution authority

## Bottom line

This slice is the first practical pilot of the new claim-bearing evidence discipline: one fresh manifest-backed proxy artifact run plus one bounded note that cites exactly what was observed and what remains out of scope.
