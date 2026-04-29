# Feature Attribution — post-Phase-14 Phase 0 reactivation packet

Date: 2026-04-02
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: `phase0-active / docs-only / non-authorizing`

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md`
- **Category:** `docs`
- **Risk:** `LOW` — why: this slice is limited to roadmap/provenance locking for the post-Phase-14 restart lane and creates no runtime, config, test, or artifact-generation authority.
- **Required Path:** `Quick`
- **Objective:** Open the post-Phase-14 Feature Attribution restart lane by locking provenance, restart ordering, and the first admissible research slice against the current executable route.
- **Candidate:** `Feature Attribution post-Phase-14 restart boundary`
- **Base SHA:** `b7a6a7de`

### Scope

- **Scope IN:**
  - `plan/feature_attribution_post_phase14_reactivation_roadmap_2026-04-02.md`
  - `docs/decisions/feature_attribution_post_phase14_phase0_reactivation_packet_2026-04-02.md`
- **Scope OUT:**
  - all files under `src/`
  - all files under `tests/`
  - all files under `config/`
  - all files under `results/research/`
  - any reruns, executions, or regenerated artifacts
  - any default-behavior changes
  - any new promotion/readiness claims
  - any reopening of fib economic discovery
- **Expected changed files:**
  - `plan/feature_attribution_post_phase14_reactivation_roadmap_2026-04-02.md`
  - `docs/decisions/feature_attribution_post_phase14_phase0_reactivation_packet_2026-04-02.md`
- **Max files touched:** `2`

### Gates required

For this packet itself:

- markdown/path sanity only
- read-only citation check against existing FA-v1 and Phase 14 surfaces
- manual wording audit that the slice remains docs-only and non-authorizing
- manual wording audit that frozen-route and current-route provenance are kept distinct

### Stop Conditions

- any wording that authorizes execution, reruns, code edits, or artifact generation
- any wording that silently treats the historical frozen 146-trade baseline as identical to the current executable route
- any wording that promotes a candidate verdict to runtime/config authority
- any wording that reopens fib discovery, tuning, or promotion
- any wording that expands this slice beyond roadmap/provenance locking

### Output required

- one reviewable restart roadmap
- one reviewable post-Phase-14 Phase 0 packet
- explicit first-slice priority ordering for restart work
- explicit provenance boundary between historical FA-v1 evidence and current-route evidence

## What this packet does

This packet opens a **post-Phase-14 restart boundary** for Feature Attribution work.

It does exactly four things:

1. acknowledges that FA-v1 already exists as a governed research lane
2. acknowledges that the current executable route has drifted from the historical frozen baseline
3. locks the next priority order for restart work
4. limits the immediate start step to provenance and roadmap discipline only

## Governing basis

This packet is grounded in the following already-existing repository surfaces:

- `docs/decisions/feature_attribution_v1_phase0_scope_freeze_packet_2026-03-31.md`
- `docs/decisions/feature_attribution_v1_phase1_feature_inventory_packet_2026-03-31.md`
- `docs/decisions/feature_attribution_v1_phase2_toggle_boundary_packet_2026-03-31.md`
- `results/research/feature_attribution_v1/reports/fa_v1_operator_summary_20260331_01.md`
- `results/research/feature_attribution_v1/reports/fa_v1_full_admitted_units_synthesis_20260331_01.md`
- `results/research/feature_attribution_v1/manifests/fa_v1_full_admitted_units_synthesis_20260331_01.json`
- `results/research/fa_v2_adaptation_off/EDGE_ORIGIN_REPORT.md`
- `src/core/strategy/decision_sizing.py`
- `tests/utils/test_decision_sizing.py`

These are citation anchors only.
This packet does not reinterpret them as execution authority.

## Locked current understanding

The restart lane begins from the following locked understanding:

- historical FA-v1 evidence and current executable-route evidence are both useful, but they are not interchangeable
- current-route synthesis does not show any admitted unit as a robust standalone edge-driver
- `Volatility sizing cluster` is the strongest current-route mover by absolute total-return delta
- `Signal-adaptation threshold cluster` is the clearest harmful current-route surface
- several previously admitted seams are currently inert on the executable route
- the broader edge-origin synthesis currently remains best explained as `emergent_system_behavior`

## Restart boundary

The restart lane is explicitly bounded as follows:

- no fresh code changes
- no fresh toggles
- no fresh reruns in this slice
- no new result artifacts in this slice
- no backfill pretending to be new evidence
- no claim that historical FA-v1 outputs automatically validate the current executable route

## First admissible next step

The only next admissible step after this packet is:

- one narrow RESEARCH slice that reconciles frozen historical FA-v1 baseline evidence with the current executable-route baseline and locks the first replay candidate ordering

That next slice may prepare for later cluster replay, but it must still remain separate from:

- runtime edits
- toggle implementation
- execution artifacts
- promotion/readiness claims

## Locked initial candidate ordering

The restart priority order is locked as:

1. `Volatility sizing cluster`
2. `Signal-adaptation threshold cluster`
3. admitted sizing interaction ladder

This ordering is grounded in the existing current-route synthesis and may only be changed by a later explicit packet.

## Why volatility sizing is first

Among the already synthesized admitted units, `Volatility sizing cluster` is the strongest current-route mover and is also one of the cleanest currently admitted seams on the canonical route.

It is therefore the best first replay candidate once provenance has been reconciled.

## Why this slice stays docs-only

If the restart lane begins by jumping straight into new execution, it risks mixing:

- frozen historical evidence
- current-route evidence
- Phase 14 structural interpretation

That would create citation drift and muddy the meaning of any follow-up artifact.

So this slice stays deliberately boring — governance boring, not existentially boring.

## Bottom line

Feature Attribution work is now reopened only as a **post-Phase-14 restart lane**.

This packet does not start execution.
It starts discipline.
And that discipline points the next real slice toward current-route rebaseline reconciliation, followed by `Volatility sizing cluster` replay.
