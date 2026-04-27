# RI policy router low-zone near-floor insufficient-evidence residual hypothesis packet

Date: 2026-04-27
Branch: `feature/ri-role-map-implementation-2026-03-24`
Mode: `RESEARCH`
Status: `docs-only / candidate preservation / föreslagen / no runtime authority`

This packet preserves a low-zone near-floor insufficient-evidence residual hypothesis for future bounded evidence work.
It does not propose, approve, or specify runtime semantics, threshold changes, or promotion/readiness claims.

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `branch:feature/ri-role-map-implementation-2026-03-24`
- **Risk:** `LOW` — why: this slice preserves one docs-only low-zone follow-up hypothesis after the residual diagnosis, but does not modify runtime, config, tests, results, or authority surfaces.
- **Required Path:** `Quick`
- **Lane:** `Research-evidence` — why this is the cheapest admissible lane now: the residual set is already split and the live cheapest surface is now the two raw low-zone near-floor rows that remain after stale debug carry is excluded, so the next honest move is to preserve one bounded hypothesis for that surface before any new runtime packet is considered.
- **Objective:** preserve one low-zone-only residual hypothesis that stays anchored to the two live near-floor `insufficient_evidence` rows while explicitly excluding `2023-12-20 03:00` as a separate seam.
- **Candidate:** `low-zone near-floor insufficient-evidence residual hypothesis`
- **Base SHA:** `HEAD`

## Review status

- `Opus 4.6 Governance Reviewer`: `APPROVED_WITH_NOTES`
- review scope: docs-only candidate preservation plus optional working-anchor update
- review lock: the packet must remain `föreslagen`, non-authoritative, and explicit that it preserves one low-zone near-floor residual hypothesis rather than specifying concrete runtime semantics or a threshold carve-out

## Skill Usage

- no repo-local skill is clearly required for this trivial docs-only framing slice
- existing evidence anchors plus the blocked runtime packet now bind the live surface tightly enough for re-anchored candidate preservation

### Research-evidence lane

- **Baseline / frozen references:**
  - `docs/governance/ri_policy_router_weak_pre_aged_single_veto_release_failset_evidence_2026-04-27.md`
  - `docs/governance/ri_policy_router_weak_pre_aged_single_veto_release_residual_blocked_longs_diagnosis_2026-04-27.md`
  - `docs/governance/ri_policy_router_weak_pre_aged_single_veto_release_low_zone_insufficient_evidence_diagnosis_2026-04-27.md`
  - `src/core/strategy/ri_policy_router.py`
- **Candidate / comparison surface:**
  - any future bounded evidence or runtime packet must stay explicit about the two named low-zone residual rows only
  - `2023-12-20T03:00:00+00:00` is explicitly out of this packet and belongs to a separate bars-7 continuation-persistence seam if reopened later
  - any future runtime packet, if later approved, must remain inside `src/core/strategy/ri_policy_router.py` plus focused tests and must not widen into other seams or global floor changes without a newly widened contract
- **Vad ska förbättras:**
  - preserve one future path that could explain or rescue the two named low-zone residual rows without re-solving the wrong seam
  - keep future work focused on the actual live constraint: near-floor confidence/edge pressure while clarity remains healthy
- **Vad får inte brytas / drifta:**
  - no claim that seam-A latch behavior is still the blocker
  - no claim that low clarity is the issue
  - no global confidence-floor or edge-floor retune from this packet alone
  - no widening into aged weak continuation, seam-B / strong continuation, cooldown, sizing, defensive routing, family/default/champion/promotion/readiness semantics
- **Reproducerbar evidens som måste finnas:**
  - the two live rows remain low-zone / `insufficient_evidence` / near-floor residuals on router-executed re-check
  - one compact evidence table that shows their shared row signature

## Verified residual signature for the chosen surface

The preserved hypothesis is bounded to the following two live rows only:

| Timestamp (UTC)             | Zone  | Bars since regime change | Clarity score | Confidence gate |    Action edge | Raw target           | Switch reason           |
| --------------------------- | ----- | -----------------------: | ------------: | --------------: | -------------: | -------------------- | ----------------------- |
| `2023-12-21T18:00:00+00:00` | `low` |                      `8` |          `35` |  `0.5068924643` | `0.0137849287` | `RI_no_trade_policy` | `insufficient_evidence` |
| `2023-12-22T09:00:00+00:00` | `low` |                      `8` |          `35` |  `0.5052986704` | `0.0105973409` | `RI_no_trade_policy` | `insufficient_evidence` |

Observed shared property against the current router no-trade floors:

- `clarity_floor = 24.0` → both rows are above floor
- `confidence_floor = 0.515` → both rows are below floor
- `edge_floor = 0.035` → both rows are below floor

Explicit exclusion from this packet:

- `2023-12-20T03:00:00+00:00` is no longer carried as part of the low-zone near-floor residual surface; current replay evidence treats it as a separate bars-7 continuation-persistence seam.

## Candidate hypothesis

### Candidate intent

Preserve one future hypothesis that treats the chosen low-zone residual rows as a **near-floor insufficient-evidence surface** rather than as:

- a remaining seam-A single-veto problem,
- a low-clarity problem,
- or an aged weak continuation problem.

This packet does **not** specify the runtime answer.
It preserves only the bounded framing that any later answer must stay attached to this exact two-row low-zone near-floor residual signature.

### Explicit non-goals

This is not a runtime packet.
It does not propose:

- a concrete threshold carve-out
- a low-zone continuation exception
- a seam-A latch refinement
- a global confidence-floor retune
- a global edge-floor retune
- any change to aged weak continuation logic
- any seam-B / strong continuation intervention

### Why this is cheaper than jumping back to runtime

The evidence now shows that the live low-zone residual rows are already well-localized and that the previously included `2023-12-20 03:00` row does not belong in the same packet.
The cheapest honest move is therefore to preserve the problem statement precisely before proposing any durable runtime shape.

That is cheaper than:

- reopening a runtime packet without a sharper candidate
- retuning global floors in the dark
- bundling low-zone near-floor rows together with aged weak continuation rows

## Intended falsifier

Retire this hypothesis if any of the following turns out to be true:

- the two live rows no longer share the same low-zone / `insufficient_evidence` / near-floor signature on router-executed re-check
- explaining or rescuing them requires touching seam-A latch behavior, aged weak continuation, seam-B / strong continuation, or any other out-of-scope seam
- a future test would affect rows outside these two residual lows without an explicitly widened contract
- a better explanation lands inside an already-bounded seam family and makes this low-zone framing unnecessary

## Scope

- **Scope IN:**
  - `docs/governance/ri_policy_router_low_zone_near_floor_insufficient_evidence_residual_hypothesis_packet_2026-04-27.md`
  - `GENESIS_WORKING_CONTRACT.md`
- **Scope OUT:**
  - `src/**`
  - `tests/**`
  - `config/**`
  - `results/**`
  - `artifacts/**`
  - seam-A latch semantics
  - aged weak continuation seam
  - seam-B / strong continuation semantics
  - cooldown behavior
  - sizing
  - defensive routing
  - family/default/champion/promotion/readiness surfaces
- **Expected changed files:**
  - `docs/governance/ri_policy_router_low_zone_near_floor_insufficient_evidence_residual_hypothesis_packet_2026-04-27.md`
  - `GENESIS_WORKING_CONTRACT.md`
- **Max files touched:** `2`

## Gates required

- minimal markdown/reference sanity on the changed files
- diff-scope check confirming only the packet and optional working-anchor update changed in this slice

## Stop Conditions

- the packet starts specifying concrete runtime semantics instead of preserving a bounded hypothesis
- the packet starts sounding like a global threshold retune
- the packet bundles the chosen low-zone surface with the aged weak continuation surface
- the next step drifts into runtime authority without a separate runtime packet and review

## Output required

- one repo-visible low-zone residual hypothesis anchor marked `föreslagen` only and re-anchored to the live two-row surface
- one updated working contract that keeps the next admissible move pointed at either a fresh two-row low-zone packet or a separate `2023-12-20` continuation-persistence diagnosis rather than generic seam-A work
