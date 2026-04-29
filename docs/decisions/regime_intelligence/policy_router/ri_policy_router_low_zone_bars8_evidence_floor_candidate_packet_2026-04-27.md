# RI policy router low-zone bars-8 evidence-floor candidate packet

Date: 2026-04-27
Branch: `feature/ri-role-map-implementation-2026-03-24`
Mode: `RESEARCH`
Status: `docs-only / candidate preservation / föreslagen / no runtime authority`

This packet preserves one bounded future candidate on the re-anchored low-zone bars-8 evidence-floor surface.
It does not authorize implementation, runtime semantics, threshold changes, or promotion/readiness claims.

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `branch:feature/ri-role-map-implementation-2026-03-24`
- **Risk:** `MED` — why: this slice is still docs-only, but it preserves one future candidate shape on a high-sensitivity router seam and therefore must remain explicit about scope, exclusions, and authority locks.
- **Required Path:** `Quick`
- **Lane:** `Research-evidence` — why this is the cheapest admissible lane now: the low-zone surface has already been re-anchored to the live two-row post-filter envelope, so the next honest move is to preserve one bounded candidate on that exact surface before any new runtime packet is attempted.
- **Objective:** preserve one exact two-row low-zone bars-8 evidence-floor candidate that could later test an enabled-only, router-local reconsideration of the immediate raw no-trade short-circuit on that live surface, without reopening the blocked three-row packet, the `2023-12-20 03:00` continuation-persistence seam, aged weak continuation rows, seam-A single-veto semantics, or global floor retuning.
- **Candidate:** `low-zone bars-8 evidence-floor downstream reconsideration`
- **Base SHA:** `HEAD`

## Review status

- `Opus 4.6 Governance Reviewer`: `APPROVED_WITH_NOTES`
- review scope: docs-only candidate preservation plus working-anchor update
- review lock: the exact two timestamps are authoritative, the shared metrics are corroboration only, the old three-row runtime packet stays blocked, and this packet grants no runtime authority

## Skill Usage

- **Applied repo-local spec:** `decision_gate_debug`
  - reason: the candidate is derived from row-level router evidence and must stay anchored to verified gate/switch behavior rather than loose threshold narratives.
- **Conditional repo-local spec:** `python_engineering`
  - reason: any later runtime slice on this candidate would still need to stay small, typed, and test-backed, but this packet is docs-only.

### Research-evidence lane

- **Baseline / frozen references:**
  - `docs/analysis/regime_intelligence/policy_router/ri_policy_router_weak_pre_aged_single_veto_release_residual_blocked_longs_diagnosis_2026-04-27.md`
  - `docs/analysis/regime_intelligence/policy_router/ri_policy_router_weak_pre_aged_single_veto_release_low_zone_insufficient_evidence_diagnosis_2026-04-27.md`
  - `docs/decisions/regime_intelligence/policy_router/ri_policy_router_low_zone_near_floor_insufficient_evidence_residual_hypothesis_packet_2026-04-27.md`
  - `docs/decisions/regime_intelligence/policy_router/ri_policy_router_low_zone_near_floor_insufficient_evidence_downstream_handoff_implementation_packet_2026-04-27.md`
  - `src/core/strategy/ri_policy_router.py`
- **Candidate / comparison surface:**
  - any future runtime slice must remain inside `src/core/strategy/ri_policy_router.py` plus focused tests
  - the only admissible future behavior hypothesis preserved here is one enabled-only, router-local reconsideration of the immediate raw `RI_no_trade_policy` short-circuit on the exact two-row live surface below
  - reconsideration here means handing those rows to the existing downstream classifier unchanged instead of immediately returning raw no-trade
- **Vad ska förbättras:**
  - preserve one future path that could test whether the exact two live bars-8 low-zone rows deserve router-local reconsideration without reopening broader seams
  - keep any later runtime follow-up focused on the current live constraint: healthy clarity, slightly subfloor confidence, and very low action edge on the same two rows
- **Vad får inte brytas / drifta:**
  - no default-path change
  - no reuse of the invalidated three-row runtime envelope
  - no inclusion of `2023-12-20T03:00:00+00:00`
  - no inclusion of the aged weak continuation rows on `2023-12-28` / `2023-12-30`
  - no seam-A single-veto semantics change
  - no global confidence-floor or edge-floor retune
  - no classifier changes
  - no forced defensive or continuation outcomes
  - no widening into cooldown, sizing, exits, defensive routing, family/default/champion/promotion/readiness semantics
- **Reproducerbar evidens som måste finnas:**
  - the live surface must remain exactly the two timestamps below after router-executed filtering
  - the shared bars-8 low-zone evidence-floor signature must still corroborate those two timestamps
  - if a future replay produces any different row set, this candidate is invalid until re-anchored again

## Authoritative live row-set lock

This candidate applies only to the following **post-router-filter live surface**:

| Timestamp (UTC)             | Zone  | Bars since regime change | Clarity score | Confidence gate |    Action edge | Raw target           | Switch reason           |
| --------------------------- | ----- | -----------------------: | ------------: | --------------: | -------------: | -------------------- | ----------------------- |
| `2023-12-21T18:00:00+00:00` | `low` |                      `8` |          `35` |  `0.5068924643` | `0.0137849287` | `RI_no_trade_policy` | `insufficient_evidence` |
| `2023-12-22T09:00:00+00:00` | `low` |                      `8` |          `35` |  `0.5052986704` | `0.0105973409` | `RI_no_trade_policy` | `insufficient_evidence` |

If any future replay, filtering pass, or evidence refresh yields any additional, missing, or different timestamps, this candidate becomes invalid until a new docs-level re-anchor is completed.

## Shared-signature corroboration lock

The shared fields below are **descriptive corroboration only**.
They must not be treated as a free selector that can widen this packet beyond the exact two timestamps above:

- `zone = low`
- `bars_since_regime_change = 8`
- `clarity_score = 35`
- `0 < (0.515 - confidence_gate) <= 0.01`
- `0.010 <= action_edge <= 0.014`
- `raw_target_policy = RI_no_trade_policy`
- `switch_reason = insufficient_evidence`

If a later slice wants to generalize from these values into a reusable predicate, that is a **new candidate**, not this packet.

## Candidate hypothesis

### Candidate intent

On the exact two-row post-filter live surface only, preserve one future hypothesis that a later runtime slice may test an **enabled-only, router-local reconsideration** of the immediate raw no-trade short-circuit.

The preserved shape is narrow:

- the rows would not be forced to `RI_defensive_transition_policy`
- the rows would not be forced to `RI_continuation_policy`
- the rows would simply be handed to the existing downstream classifier unchanged instead of immediately returning raw no-trade

This packet does **not** claim that such a runtime slice would succeed.
It preserves only one bounded future candidate shape on the re-anchored surface.

### Outcome-neutrality lock

This candidate does **not** assert or require a trade-producing result.
If a future runtime slice were attempted, downstream `RI_no_trade_policy` would still remain an admissible outcome.

### Explicit exclusions

This packet explicitly excludes all of the following:

- `2023-12-20T03:00:00+00:00` bars-7 continuation-persistence seam
- `2023-12-28T09:00:00+00:00` and `2023-12-30T21:00:00+00:00` aged weak continuation rows
- seam-A single-veto semantics
- global confidence-floor retuning
- global edge-floor retuning
- forced defensive outcomes
- forced continuation outcomes
- downstream classifier edits
- config-authority or schema edits
- default-path changes

### Prior-packet invalidation lock

The earlier three-row runtime packet at `docs/decisions/regime_intelligence/policy_router/ri_policy_router_low_zone_near_floor_insufficient_evidence_downstream_handoff_implementation_packet_2026-04-27.md` remains blocked/reverted and is **not** revived or made authoritative by this document.

## Admissible runtime shape for a future packet

Any later runtime packet for this candidate may only:

- remain inside `src/core/strategy/ri_policy_router.py` plus focused tests
- preserve the exact two-row post-filter live surface as the authoritative target
- keep the downstream classifier unchanged
- keep router floors unchanged
- keep policy labels unchanged
- keep default-path behavior unchanged when the router leaf is absent or disabled

Any later runtime packet must not:

- reuse the invalidated three-row packet as if it were still authoritative
- generalize the corroborating metrics above into a widening predicate without a new candidate packet
- include the `2023-12-20 03:00` seam or the aged weak continuation rows as part of the same mechanism
- force a continuation or defensive outcome as proof of success
- alter classifier logic, threshold logic, config authority, or default path as its primary mechanism

## Why this remains cheaper than the alternatives

This candidate remains cheaper than:

- reopening the `2023-12-20 03:00` continuation-persistence seam
- reopening the older aged weak continuation seam on `2023-12-28` / `2023-12-30`
- retuning global floors or classifier behavior

It stays on the smallest currently live low-zone surface while preserving exact traceability.

## Intended falsifier

Retire this candidate if any of the following turns out to be true:

- the post-filter live surface is no longer exactly the two timestamps locked above
- helping these rows requires threshold/floor edits, classifier edits, or other broader semantics
- any honest runtime attempt would need to include `2023-12-20 03:00` or the aged weak continuation rows as part of the same mechanism
- the downstream-classifier reconsideration shape can only work by forcing an outcome rather than preserving outcome neutrality

## Scope

- **Scope IN:**
  - `docs/decisions/regime_intelligence/policy_router/ri_policy_router_low_zone_bars8_evidence_floor_candidate_packet_2026-04-27.md`
  - `GENESIS_WORKING_CONTRACT.md`
- **Scope OUT:**
  - `src/**`
  - `tests/**`
  - `config/**`
  - `results/**`
  - `artifacts/**`
  - runtime semantics
  - default-path changes
  - config-authority changes
  - `2023-12-20 03:00` continuation-persistence seam
  - aged weak continuation rows on `2023-12-28` / `2023-12-30`
  - seam-A single-veto semantics
- **Expected changed files:**
  - `docs/decisions/regime_intelligence/policy_router/ri_policy_router_low_zone_bars8_evidence_floor_candidate_packet_2026-04-27.md`
  - `GENESIS_WORKING_CONTRACT.md`
- **Max files touched:** `2`

## Gates required

- minimal markdown/reference sanity on the changed files
- diff-scope confirmation that only the new candidate packet and `GENESIS_WORKING_CONTRACT.md` were touched by this slice
- explicit self-review for silent widening, hidden authority claims, and forced-outcome language

## Stop Conditions

- any attempt to treat the corroborating metric fields as a widening selector instead of corroboration
- any need to include `2023-12-20 03:00` in the same packet
- any need to include aged weak continuation rows in the same packet
- any need to force defensive or continuation outcomes
- any need to edit runtime files in this slice
- any wording that implies this packet revives the blocked three-row runtime packet or grants implementation authority

## Output required

- one repo-visible candidate anchor for the exact two-row low-zone bars-8 evidence-floor surface
- one updated working contract that records the candidate as preserved / `föreslagen` only and keeps runtime authority out of scope until a separate runtime packet is reviewed
