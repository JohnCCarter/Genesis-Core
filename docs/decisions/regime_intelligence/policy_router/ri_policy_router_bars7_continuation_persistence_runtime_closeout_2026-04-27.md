# RI policy router bars-7 continuation-persistence runtime closeout

Date: 2026-04-27
Branch: `feature/ri-role-map-implementation-2026-03-24`
Mode: `RESEARCH`
Status: `completed / positive runtime closeout / implementation retained`

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `branch:feature/ri-role-map-implementation-2026-03-24`
- **Risk:** `MED` — why: this slice records the bounded positive verdict for the implemented bars-7 continuation-persistence runtime slice on a high-sensitivity router seam without widening the runtime surface further.
- **Required Path:** `Quick`
- **Lane:** `Research-evidence` — why this is the cheapest admissible lane now: the runtime packet is already implemented and green, so the honest next step is to record the verdict, the exact helper-hit artifact, and the next remaining residual seam.
- **Objective:** close the bars-7 continuation-persistence runtime slice with exact helper-hit evidence, retain the implementation, and hand off to the separate aged-weak continuation residual surface.
- **Candidate:** `bars-7 continuation-persistence reconsideration`
- **Base SHA:** `75246d369ef7611870d740ec0d88cd7ff9d63363`

## Evidence inputs

- `docs/decisions/regime_intelligence/policy_router/ri_policy_router_bars7_continuation_persistence_runtime_packet_2026-04-27.md`
- `results/backtests/ri_policy_router_bars7_continuation_20260427/fail_b_helper_hit_timestamps.json`
- `src/core/strategy/ri_policy_router.py`

## Verdict

The bars-7 runtime slice is **positive** on its own exact helper-hit gate and remains acceptably bounded.

Expected helper-hit set on router-executed bars:

- `2023-12-20T03:00:00+00:00`

Actual helper-hit artifact:

- `results/backtests/ri_policy_router_bars7_continuation_20260427/fail_b_helper_hit_timestamps.json`
- contents: `[
  "2023-12-20T03:00:00+00:00"
]`

So the slice satisfies its exact helper-hit set equality requirement on the pinned fail-B carrier.

## Bounded interpretation

The retained implementation remains narrow for the reasons below:

- it only applies on the enabled path
- it stays attached to the existing raw `RI_no_trade_policy` / `insufficient_evidence` seam
- it requires previous continuation state plus the exact bars-7 low-zone signature
- it does not force `RI_continuation_policy` or `RI_defensive_transition_policy`
- it re-enters the existing downstream classifier / stability path unchanged
- later low-zone rows on `2023-12-21T18:00:00+00:00` and `2023-12-22T09:00:00+00:00` remain excluded from the helper-hit set

## Gate summary

- focused router tests: passed
- focused decision scenario tests: passed
- `pre-commit run --all-files`: passed
- `ruff check .`: passed
- import smoke selector: passed
- determinism smoke selector: passed
- feature-cache invariance selectors: passed
- pipeline fast-hash guard selector: passed
- `bandit -r src/core/strategy -c bandit.yaml`: passed

## Consequence

The bars-7 continuation-persistence runtime helper remains in active code.

This closeout does **not** authorize any reopening of:

- the negative low-zone bars-8 runtime family,
- seam-A single-veto semantics,
- global confidence/edge retuning,
- or strong-continuation / seam-B semantics.

## Next admissible move

The next remaining residual surface is the separate aged-weak continuation seam around:

- `2023-12-28T09:00:00+00:00`
- `2023-12-30T21:00:00+00:00`

Any follow-up there must remain explicit that bars-7 is now complete and low-zone bars-8 is negative-only.
