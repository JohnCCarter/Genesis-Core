# Edge-origin isolation manifest-pilot portability boundary packet

Date: 2026-05-18
Branch: `feature/evidence-closeout-pilot`
Status: `decision-recorded / docs-only / non-authorizing`

This document records the current portability boundary for the manifest-backed
`edge_origin_isolation` pilot claim surface. It grants no source, test, runtime,
config-authority, paper/live, promotion, or cross-chain replay authority by itself.
It does not rewrite the separate future carrier decision for `edge_origin_isolation`, and it
does not widen any Phase 10 family claim above the current branch-state evidence.

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md` via `feature/* -> RESEARCH`
- **Category:** `docs`
- **Risk:** `LOW` — why: this slice records one current-state portability boundary and one queue
  sync only; it does not modify `src/**`, `tests/**`, `scripts/**`, `results/**`, or runtime
  authority surfaces
- **Required Path:** `Quick path / docs-only boundary record`
- **Lane:** `Research-evidence` — why: this packet narrows the honest portability wording for one
  claim-bearing Phase 10 surface without reopening artifact generation, retained-trace work, or
  implementation
- **Objective:** pin the current manifest-pilot `edge_origin_isolation` claim surface to
  `same-local-checkout only` and keep stronger portability language below separately reopened
  carrier work
- **Base SHA:** `894dd19d0d3ef65a83ed3c94920f4b5becfc0a5f`
- **Related artifacts:**
  - `docs/analysis/diagnostics/next_phase_verkstad_queue_2026-05-15.md`
  - `docs/analysis/diagnostics/ignored_artifact_dependency_inventory_2026-05-15.md`
  - `docs/analysis/diagnostics/edge_origin_isolation_manifest_claim_pilot_2026-05-15.md`
  - `docs/decisions/diagnostic_campaigns/edge_origin_isolation_manifest_pilot_run_packet_2026-05-15.md`
  - `docs/decisions/governance/edge_origin_isolation_carrier_decision_packet_2026-05-15.md`
  - `docs/decisions/governance/execution_proxy_replay_claim_level_boundary_packet_2026-05-15.md`

### Scope

- **Scope IN:** this boundary packet; queue sync that records one later explicit reopen after the
  closed successor queue
- **Scope OUT:** `docs/analysis/diagnostics/ignored_artifact_dependency_inventory_2026-05-15.md`;
  `docs/analysis/diagnostics/edge_origin_isolation_manifest_claim_pilot_2026-05-15.md`;
  `docs/decisions/diagnostic_campaigns/edge_origin_isolation_manifest_pilot_run_packet_2026-05-15.md`;
  all changes under `results/**`, `scripts/**`, `tests/**`, `src/**`, `config/**`,
  `registry/fixtures/**`, and `artifacts/**`; any retained-trace carrier choice; any stronger
  `historical-trace-level` or `full-chain clean-checkout-level` claim; any runtime/default/
  paper-live/readiness/promotion language
- **Max files touched:** `2`

### Gates required

For this packet itself:

- targeted docs validation for this packet and queue sync
- manual wording audit that the current manifest-pilot surface stays at
  `same-local-checkout only`
- manual wording audit that the separate future tracked-fixture carrier decision remains unchanged
  and non-authorizing

## Purpose

This packet answers one narrow question only:

- what portability label honestly applies to the current manifest-backed `edge_origin_isolation`
  claim surface on this branch today?

## What changed in this slice

- the current manifest-pilot `edge_origin_isolation` claim surface is pinned explicitly to
  `same-local-checkout only`
- the closed successor queue now records one later explicit reopen after the earlier family-level
  closeout sequence

## What did not change

- no source, test, script, fixture, result-root, or runtime surfaces changed
- no new commit-safe carrier was created for `edge_origin_isolation`
- no historical trace was retained or promoted into a stronger carrier class
- the earlier future carrier decision for a tracked minimal fixture pair remains unchanged
- no runtime, policy, readiness, paper/live, or promotion semantics changed

## Governing basis

### Observed

1. `docs/analysis/diagnostics/ignored_artifact_dependency_inventory_2026-05-15.md` records the
   broader Phase 10 historical-trace family as reduced but not closed, because stronger
   portability claims would still depend on older ignored traces under
   `results/research/fa_v2_adaptation_off/**`.
2. `docs/analysis/diagnostics/edge_origin_isolation_manifest_claim_pilot_2026-05-15.md` cites a
   manifest-backed pilot root under
   `results/research/fa_v2_adaptation_off/phase10_edge_origin_isolation_manifest_pilot_20260515/`
   and explicitly records that both the note and that output root were untracked/ignored in that
   slice.
3. The same pilot note cites fixed historical inputs under:
   - `results/research/fa_v2_adaptation_off/trace_baseline_current.json`
   - `results/research/fa_v2_adaptation_off/trace_adaptation_off.json`
4. `docs/decisions/diagnostic_campaigns/edge_origin_isolation_manifest_pilot_run_packet_2026-05-15.md`
   authorizes one bounded run against those fixed historical traces and one ignored output root;
   it does not authorize runtime, config-authority, or replay portability upgrades.
5. `docs/decisions/governance/edge_origin_isolation_carrier_decision_packet_2026-05-15.md`
   already selects one tracked minimal fixture pair under `registry/fixtures/` as the first
   commit-safe carrier strategy **if** the line is reopened later.
6. No current tracked branch-state artifact proves that the manifest-pilot surface can be replayed
   from tracked inputs alone or that the older historical traces have been elevated into a
   retained-trace carrier.

### Inferred

- the current manifest-pilot `edge_origin_isolation` surface is a useful observational citation
  anchor, but it remains tied to ignored historical inputs and an ignored output root on the exact
  observed workstation/checkout surface
- the most honest current portability label is therefore `same-local-checkout only`
- the separate future fixture-pair carrier decision narrows a later reopen path, but it does not
  retroactively upgrade the current manifest-pilot surface into `fixture-level`,
  `historical-trace-level`, or `full-chain clean-checkout-level` portability
- the cheapest honest closeout move is classification, not carrier implementation

### Unverified in this packet

- whether a later retained-trace or tracked-fixture implementation should actually be reopened for
  this chain
- whether any future `historical-trace-level` wording would be worth the extra retained-carrier
  cost
- whether the broader Phase 10 family above the bounded `execution_proxy_evidence` and
  `edge_origin_isolation` exceptions should ever receive a family-wide portability packet

## Boundary decision

### Current standing conclusion

The current justified portability label for the manifest-backed `edge_origin_isolation` claim
surface is:

- **`same-local-checkout only`**

This means the repo may currently say only that:

- one exact local manifest-backed pilot run completed against fixed historical trace inputs on the
  observed checkout/workstation surface
- the resulting outputs remain observational only
- later citations of the manifest-backed pilot note do not upgrade that surface into a tracked,
  retained-trace, or clean-checkout portable carrier

### Wording that remains out of bounds now

Until a later packet proves otherwise, do **not** describe the current manifest-pilot surface as
any of the following:

- `fixture-level`
- `historical-trace-level`
- `full-chain clean-checkout-level`
- tracked-carrier portable
- clean-checkout replay solved
- portability proof for the broader Phase 10 historical-trace family
- runtime-policy, readiness, paper/live, or promotion evidence

### Minimum evidence before `fixture-level` wording is allowed

A future bounded slice would need at minimum:

- one tracked minimal fixture pair under `registry/fixtures/` or another explicitly chosen
  commit-safe carrier
- a focused rerun/test path that proves the named chain can execute from that tracked pair
- an explicit envelope stating that the fixture path is chain-local and does not widen to other
  portability classes or other claim-bearing chains

### Minimum evidence before `historical-trace-level` wording is allowed

A future bounded slice would need at minimum:

- one exact retained historical-trace carrier for the named `edge_origin_isolation` chain
- reproducible reruns against that retained carrier
- an explicit envelope naming the relevant `SHA`, branch, and why the named chain no longer
  depends on unstated local-only inputs or outputs

### Minimum evidence before `full-chain clean-checkout-level` wording is allowed

A future bounded slice would need at minimum:

- a clean checkout that can regenerate the full named `edge_origin_isolation` claim-bearing chain
  from tracked inputs or explicitly retained commit-safe carriers
- no hidden dependence on ignored `results/**`, workstation-local output roots, or unstated local
  state
- an explicit regeneration envelope for the named chain only

## What remains out of scope

This packet does not decide or authorize:

- implementation of the tracked minimal fixture pair
- rerunning the manifest-pilot root
- rewriting the manifest-pilot claim note or run packet
- any broader Phase 10 family portability upgrade
- any source, test, fixture, or results-root changes

## Hard stop and reopen rule

If a future slice needs any of the following, it must stop and reopen separately instead of
leaning on this document:

- any tracked-fixture implementation for `edge_origin_isolation`
- any retained-trace carrier choice
- stronger portability wording for the broader Phase 10 family
- any runtime/default/config-authority/paper-live/promotion semantics

## Bottom line

The current manifest-backed `edge_origin_isolation` pilot win is real but narrow. The honest
label is `same-local-checkout only`: one exact local historical-input plus local-output chain was
observed and summarized, while stronger replay portability still depends on a separately reopened
carrier path and remains out of scope today.
