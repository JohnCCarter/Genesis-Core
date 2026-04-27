# RI policy router aged-weak parked handoff on active carrier truth

Date: 2026-04-27
Branch: `feature/ri-role-map-implementation-2026-03-24`
Mode: `RESEARCH`
Status: `docs-only / parked handoff / no active aged-weak runtime candidate`

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `branch:feature/ri-role-map-implementation-2026-03-24`
- **Risk:** `LOW` — why: this slice is docs-only and records the active carrier truth after the recent aged-weak closeouts without reopening runtime, config, tests, or authority surfaces.
- **Required Path:** `Quick`
- **Lane:** `Research-evidence` — why this is the cheapest admissible lane now: the honest next step is to preserve the current parked state and forbid reuse of the falsified aged-weak residual premise before any future seam framing is attempted.
- **Objective:** preserve the active-carrier truth that keeps the aged-weak RI-router chain parked and record the exact reuse assumptions that are now out of bounds.

## Evidence anchors

- `docs/governance/ri_policy_router_reanchor_post_aged_weak_closeouts_2026-04-27.md`
- `docs/governance/ri_policy_router_bars7_continuation_persistence_runtime_closeout_2026-04-27.md`
- `docs/governance/ri_policy_router_weak_pre_aged_single_veto_release_residual_blocked_longs_diagnosis_2026-04-27.md`
- `docs/governance/ri_policy_router_aged_weak_second_hit_release_runtime_closeout_2026-04-27.md`
- `docs/governance/ri_policy_router_aged_weak_plus_stability_interaction_runtime_packet_2026-04-27.md`
- `GENESIS_WORKING_CONTRACT.md`

## Parked handoff verdict

The RI-router runtime chain remains **parked** on the aged-weak surface.

What still holds:

- the retained positive runtime slice in this chain is still the bounded `bars-7 continuation-persistence` helper only
- the aged-weak second-hit slice is closed negative and reverted
- the aged-weak plus stability interaction slice is closed negative and reverted
- there is currently **no active aged-weak runtime candidate** to preserve from the present carrier truth

## Active carrier truth that must not be rewritten

The aged-weak plus stability closeout falsified the older residual-row story on the active carrier.

Expected direct helper-hit set:

- `2023-12-28T09:00:00+00:00`
- `2023-12-30T21:00:00+00:00`

Actual direct helper-hit set:

- `2023-12-28T09:00:00+00:00`
- `2023-12-31T00:00:00+00:00`

The active-carrier interpretation is now locked as:

- `2023-12-30T12:00:00+00:00` is already a continuation entry
- `2023-12-30T15:00:00+00:00` and `2023-12-30T18:00:00+00:00` are cooldown rows
- `2023-12-30T21:00:00+00:00` therefore no longer arrives as the same-origin `RI_no_trade_policy` row required by the falsified aged-weak packet
- `2023-12-31T00:00:00+00:00` was leak/drift on the active carrier, not a legitimate replacement target

## Do-not-repeat assumptions

Future work on this chain must not reuse any of the following as if they were still live premises:

- `2023-12-30T21:00:00+00:00` as a same-origin aged-weak residual row on the active carrier
- `{2023-12-28T09:00:00+00:00, 2023-12-30T21:00:00+00:00}` as if it were still the trustworthy direct helper-hit lock for a new runtime slice
- `2023-12-31T00:00:00+00:00` as a replacement target to "rescue" the falsified aged-weak packet
- the aged-weak second-hit family under the assumption that raw-guard bypass is sufficient while unchanged stability/min-dwell behavior remains intact
- the residual five-row diagnosis as if it were still one unresolved seam-A pocket
- the positive `bars-7 continuation-persistence` closeout as authority to widen into fresh aged-weak runtime work

## Future reopen rule

If this chain is reopened at all, the next move must be one of the following:

1. a **fresh docs-only evidence / seam-framing note** anchored to the active carrier truth, or
2. an explicit decision to leave the RI-router chain parked and move to another research lane

What is not admissible from this handoff note alone:

- a new aged-weak runtime packet
- an Optuna slice on top of the falsified aged-weak story
- reopening seam-A, bars-8, or generic aged-threshold semantics through implication rather than fresh evidence

## Output of this slice

- one docs-only parked handoff note that freezes the active-carrier truth on the aged-weak surface
- one explicit do-not-repeat list for future RI-router framing
- one short handoff rule: future reopening starts with fresh docs-only evidence or the chain stays parked
