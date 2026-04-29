# RI policy router aged-weak second-hit release candidate packet

Date: 2026-04-27
Branch: `feature/ri-role-map-implementation-2026-03-24`
Mode: `RESEARCH`
Status: `docs-only / candidate preservation / föreslagen / no runtime authority`

This packet preserves one bounded future candidate on the remaining aged-weak continuation residual surface.
It does not authorize implementation, threshold retuning, strong-continuation changes, or reopening the already-resolved low-zone seams.

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `branch:feature/ri-role-map-implementation-2026-03-24`
- **Risk:** `MED` — why: this is still docs-only, but it preserves one future candidate on a high-sensitivity router seam and must remain explicit about the exact residual row-set, its context anchors, and its exclusions.
- **Required Path:** `Quick`
- **Lane:** `Research-evidence` — why this is the cheapest admissible lane now: the low-zone bars-8 runtime family is closed negative and the bars-7 continuation-persistence slice is now complete, so the next honest move is to re-anchor the remaining aged-weak residual surface before any new runtime packet is attempted.
- **Objective:** preserve one exact-row candidate centered on the residual aged-weak continuation rows at `2023-12-28T09:00:00+00:00` and `2023-12-30T21:00:00+00:00`, framing them as a possible same-guard persistence / second-hit release question rather than another threshold-local retune.
- **Candidate:** `aged-weak second-hit release`
- **Base SHA:** `75246d369ef7611870d740ec0d88cd7ff9d63363`

## Evidence anchors

- `docs/analysis/regime_intelligence/policy_router/ri_policy_router_aged_weak_continuation_guard_failset_evidence_2026-04-24.md`
- `docs/analysis/regime_intelligence/policy_router/ri_policy_router_weak_pre_aged_single_veto_release_failset_evidence_2026-04-27.md`
- `docs/analysis/regime_intelligence/policy_router/ri_policy_router_weak_pre_aged_single_veto_release_residual_blocked_longs_diagnosis_2026-04-27.md`
- `docs/decisions/regime_intelligence/policy_router/ri_policy_router_bars7_continuation_persistence_runtime_closeout_2026-04-27.md`
- `results/backtests/ri_policy_router_aged_weak_residual_probe_20260427/aged_weak_residual_rows.json`
- `src/core/strategy/ri_policy_router.py`

## Authoritative residual row-set lock

This candidate is bounded to the following exact residual blocked baseline longs on the pinned fail-B surface:

| Timestamp (UTC)             | Baseline fail-B | Current fail-B candidate | Zone  | Bars since regime change | Clarity score | Confidence gate |    Action edge | Previous policy      | Raw target           | Selected policy      | Switch reason                  | Dwell duration |
| --------------------------- | --------------- | ------------------------ | ----- | -----------------------: | ------------: | --------------: | -------------: | -------------------- | -------------------- | -------------------- | ------------------------------ | -------------: |
| `2023-12-28T09:00:00+00:00` | `LONG`          | `NONE`                   | `low` |                     `20` |          `38` |  `0.5289101921` | `0.0578203842` | `RI_no_trade_policy` | `RI_no_trade_policy` | `RI_no_trade_policy` | `AGED_WEAK_CONTINUATION_GUARD` |            `2` |
| `2023-12-30T21:00:00+00:00` | `LONG`          | `NONE`                   | `low` |                     `23` |          `37` |  `0.5234482255` | `0.0468964510` | `RI_no_trade_policy` | `RI_no_trade_policy` | `RI_no_trade_policy` | `AGED_WEAK_CONTINUATION_GUARD` |            `2` |

If a later replay changes this exact residual row-set materially, this candidate must be re-anchored before any runtime attempt.

## Context anchors (not target rows)

The rows below are context anchors only and must not be treated as direct helper targets for this candidate:

| Timestamp (UTC)             | Role in current story                                                                            |
| --------------------------- | ------------------------------------------------------------------------------------------------ |
| `2023-12-28T06:00:00+00:00` | first aged-weak guard hit in the first late-December pocket; baseline and candidate both `NONE`  |
| `2023-12-30T18:00:00+00:00` | first aged-weak guard hit in the second late-December pocket; baseline and candidate both `NONE` |
| `2023-12-31T00:00:00+00:00` | later aged-weak guard row on the pinned carrier, but not a residual blocked baseline long        |

These rows matter only as evidence that the residual rows above may be the later hits of two bounded aged-weak pockets.

## Candidate hypothesis

### Candidate intent

Preserve one future hypothesis that the residual aged-weak surface is not best framed as another threshold-local question.

Instead, the cheapest remaining hypothesis is a **same-guard persistence / second-hit release** question:

- first aged-weak hit in a bounded late-continuation pocket may still block,
- but the later repeated aged-weak hit in that same pocket may deserve one enabled-only router-local reconsideration,
- without changing the aged threshold itself, the confidence/edge thresholds, or strong-continuation semantics.

### State-sensitive lock

Any future runtime packet preserved by this candidate must stay attached to the combination below, not a generic late-age carve-out:

- exact residual timestamps locked above as the authoritative target rows
- `switch_reason = AGED_WEAK_CONTINUATION_GUARD`
- `raw_target_policy = RI_no_trade_policy`
- `selected_policy = RI_no_trade_policy`
- `previous_policy = RI_no_trade_policy`
- `dwell_duration = 2`
- low-zone residual rows only
- first-hit context rows `2023-12-28T06:00:00+00:00` and `2023-12-30T18:00:00+00:00` are context anchors only, not direct helper targets

### Outcome-neutrality lock

This packet does **not** assert that continuation should necessarily win.
If a later runtime slice is attempted, downstream `RI_no_trade_policy` may still remain the correct outcome.

## Explicit exclusions

This candidate explicitly excludes all of the following:

- low-zone bars-8 rows on `2023-12-21T18:00:00+00:00` and `2023-12-22T09:00:00+00:00`
- bars-7 continuation-persistence seam on `2023-12-20T03:00:00+00:00`
- seam-A single-veto semantics around `2023-12-22T15:00:00+00:00`
- already-strong continuation / seam-B around `2023-12-24T21:00:00+00:00`
- global aged-threshold retuning
- global confidence-floor or edge-floor retuning
- classifier edits
- forced defensive outcomes
- forced continuation outcomes
- default-path changes
- config/env/schema/authority surfaces

## Intended falsifier

Retire this candidate if any of the following turns out to be true:

- helping the residual rows requires changing the aged threshold, confidence/edge thresholds, or strong-continuation semantics
- the residual surface is no longer exactly `2023-12-28T09:00:00+00:00` and `2023-12-30T21:00:00+00:00`
- the rows are not genuinely the later repeated hits of bounded aged-weak pockets
- a future runtime slice would need to include `2023-12-31T00:00:00+00:00` as a direct helper target rather than an indirect downstream effect
- the runtime proof would need to reopen low-zone or seam-A families as its primary mechanism

## Scope

- **Scope IN:**
  - `docs/decisions/regime_intelligence/policy_router/ri_policy_router_aged_weak_second_hit_release_candidate_packet_2026-04-27.md`
  - `GENESIS_WORKING_CONTRACT.md`
- **Scope OUT:**
  - `src/**`
  - `tests/**`
  - `config/**`
  - `results/**`
  - `artifacts/**`
  - low-zone bars-8 family
  - bars-7 continuation-persistence family
  - seam-A single-veto semantics
  - already-strong continuation / seam-B semantics
  - classifier edits
  - default-path changes
- **Expected changed files:**
  - `docs/decisions/regime_intelligence/policy_router/ri_policy_router_aged_weak_second_hit_release_candidate_packet_2026-04-27.md`
  - `GENESIS_WORKING_CONTRACT.md`
- **Max files touched:** `2`

## Gates required

- minimal markdown/reference sanity on the changed files
- diff-scope confirmation that only this packet and `GENESIS_WORKING_CONTRACT.md` changed in this slice
- explicit self-review for silent widening back into threshold retuning or previously closed seam families

## Stop Conditions

- any attempt to treat this as another generic aged-threshold tweak
- any attempt to bundle `2023-12-31T00:00:00+00:00` into the direct residual target set
- any wording that revives low-zone or seam-A runtime families
- any wording that implies runtime authority from this packet alone

## Output required

- one repo-visible candidate anchor for the exact residual aged-weak row-set
- one updated working contract that points the next admissible runtime packet at this exact residual surface rather than at older aged-threshold framing
