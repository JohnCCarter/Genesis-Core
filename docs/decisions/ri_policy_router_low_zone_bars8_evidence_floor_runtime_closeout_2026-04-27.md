# RI policy router low-zone bars-8 evidence-floor runtime closeout

Date: 2026-04-27
Branch: `feature/ri-role-map-implementation-2026-03-24`
Mode: `RESEARCH`
Status: `completed / negative runtime closeout / implementation reverted`

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `branch:feature/ri-role-map-implementation-2026-03-24`
- **Risk:** `MED` — why: this slice records the bounded negative verdict from the approved bars-8 runtime packet and restores the runtime surface to its pre-slice state.
- **Required Path:** `Quick`
- **Lane:** `Research-evidence` — why this is the cheapest admissible lane now: the runtime packet has already been falsified by its own exact helper-hit gate, so the honest next step is a repo-visible negative closeout rather than more runtime widening.
- **Objective:** record the negative verdict for the bars-8 runtime packet, cite the exact helper-hit artifacts, and lock the next admissible move to the separate bars-7 continuation-persistence seam.
- **Candidate:** `low-zone bars-8 evidence-floor downstream reconsideration`
- **Base SHA:** `75246d369ef7611870d740ec0d88cd7ff9d63363`

## Evidence inputs

- `docs/decisions/ri_policy_router_low_zone_bars8_evidence_floor_runtime_packet_2026-04-27.md`
- `results/backtests/ri_policy_router_low_zone_bars8_runtime_20260427/fail_b_helper_hit_timestamps.json`
- `results/backtests/ri_policy_router_low_zone_bars8_runtime_20260427/fail_b_helper_hit_diagnostics.json`

## Verdict

The bars-8 runtime candidate is **negative** on its own exact helper-hit gate.

Expected helper-hit set on router-executed bars:

- `2023-12-21T18:00:00+00:00`
- `2023-12-22T09:00:00+00:00`

Actual helper-hit artifact:

- `results/backtests/ri_policy_router_low_zone_bars8_runtime_20260427/fail_b_helper_hit_timestamps.json`
- contents: `[]`

So the candidate does not reach even its first admissibility proof on the pinned fail-B subject.

## Diagnostic interpretation

The diagnostic replay on router-executed bars recorded the following rows on the pinned carrier:

- `2023-12-20T03:00:00+00:00`
- `2023-12-21T18:00:00+00:00`
- `2023-12-22T09:00:00+00:00`

Shared observed properties on that verification surface:

- `zone = low`
- `clarity_score = 35`
- `raw_target_policy = RI_no_trade_policy`
- `switch_reason = insufficient_evidence`
- `low_zone_bars8_evidence_floor_reconsideration_applied = false`
- `regime = balanced`

Most importantly, the expected timestamps still appeared with `bars_since_regime_change = 7`, not `8`, and the explicitly excluded `2023-12-20T03:00:00+00:00` row remained present on the same router-executed low-zone surface.

That means the packet's locked two-row bars-8 runtime surface does not hold on the pinned verification carrier.

## Consequence

Because the packet required exact helper-hit set equality and explicit exclusion of `2023-12-20T03:00:00+00:00`, this slice must stop here and close negative.

The implementation tied to this candidate was reverted.

This closeout does **not** authorize widening back toward:

- the blocked three-row low-zone runtime packet,
- a generic near-floor carve-out,
- global floor retuning,
- classifier edits,
- or any forced outcome.

## Next admissible move

Skip further low-zone reruns in this chain.

The next admissible slice is the separate bars-7 continuation-persistence packet centered on `2023-12-20T03:00:00+00:00`, with low-zone bars-8 and aged-weak surfaces kept out of scope.
