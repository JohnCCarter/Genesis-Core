# RI policy router bars-7 continuation-persistence candidate packet

Date: 2026-04-27
Branch: `feature/ri-role-map-implementation-2026-03-24`
Mode: `RESEARCH`
Status: `docs-only / candidate preservation / föreslagen / no runtime authority`

This packet preserves one bounded future candidate on the separate bars-7 row at `2023-12-20T03:00:00+00:00`.
It does not authorize runtime implementation, widening into the later low-zone rows, or reopening the negative bars-8 closeout.

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `branch:feature/ri-role-map-implementation-2026-03-24`
- **Risk:** `MED` — why: this is still docs-only, but it preserves one future candidate on a high-sensitivity router seam and must remain explicit about evidence, exclusions, and authority locks.
- **Required Path:** `Quick`
- **Lane:** `Research-evidence` — why this is the cheapest admissible lane now: the bars-8 runtime candidate has just closed negative, and the next smallest remaining row-specific question is whether `2023-12-20T03:00:00+00:00` deserves its own state-sensitive continuation-persistence candidate rather than being silently bundled back into low-zone floor semantics.
- **Objective:** preserve one exact-row candidate centered on `2023-12-20T03:00:00+00:00` that could later test an enabled-only, router-local continuation-persistence reconsideration on the first low-zone `insufficient_evidence` row arriving immediately after continuation, without reopening the negative bars-8 family, seam-A single-veto semantics, aged-weak continuation, or global floor retuning.
- **Candidate:** `bars-7 continuation-persistence reconsideration`
- **Base SHA:** `75246d369ef7611870d740ec0d88cd7ff9d63363`

## Evidence anchors

- `docs/analysis/ri_policy_router_weak_pre_aged_single_veto_release_residual_blocked_longs_diagnosis_2026-04-27.md`
- `docs/decisions/ri_policy_router_low_zone_bars8_evidence_floor_runtime_packet_2026-04-27.md`
- `docs/decisions/ri_policy_router_low_zone_bars8_evidence_floor_runtime_closeout_2026-04-27.md`
- `results/backtests/ri_policy_router_low_zone_bars8_runtime_20260427/fail_b_helper_hit_diagnostics.json`
- `src/core/strategy/ri_policy_router.py`

## Authoritative row lock

This candidate is bounded to the following exact router-executed row on the pinned fail-B carrier:

| Timestamp (UTC)             | Zone  | Bars since regime change | Clarity score | Confidence gate |    Action edge | Previous policy          | Raw target           | Selected policy      | Switch reason           | Dwell duration |
| --------------------------- | ----- | -----------------------: | ------------: | --------------: | -------------: | ------------------------ | -------------------- | -------------------- | ----------------------- | -------------: |
| `2023-12-20T03:00:00+00:00` | `low` |                      `7` |          `35` |  `0.5060251200` | `0.0120502401` | `RI_continuation_policy` | `RI_no_trade_policy` | `RI_no_trade_policy` | `insufficient_evidence` |            `1` |

If a later replay changes this exact row signature materially, this candidate must be re-anchored before any runtime attempt.

## Candidate hypothesis

### Candidate intent

Preserve one future hypothesis that `2023-12-20T03:00:00+00:00` may deserve a **one-row continuation-persistence reconsideration** because it is the first low-zone `insufficient_evidence` collapse immediately following continuation.

The intended shape is narrow:

- state-sensitive rather than threshold-retuning
- centered on the first row only, not the later low-zone rows
- enabled-only
- router-local
- no forced continuation or defensive outcome

### State-sensitive signature lock

Any future runtime packet preserved by this candidate must remain attached to the combination below, not a generic low-zone carve-out:

- exact timestamp lock above as the authoritative row
- `previous_policy = RI_continuation_policy`
- `selected_policy = RI_no_trade_policy`
- `raw_target_policy = RI_no_trade_policy`
- `switch_reason = insufficient_evidence`
- `bars_since_regime_change = 7`
- `dwell_duration = 1`
- `zone = low`
- `clarity_score = 35`
- `0 < (0.515 - confidence_gate) <= 0.01`
- `0.010 <= action_edge <= 0.014`

### Outcome-neutrality lock

This packet does **not** assert that continuation should win.
If a later runtime slice is attempted, `RI_no_trade_policy` may still remain the correct outcome.

## Explicit exclusions

This candidate explicitly excludes all of the following:

- `2023-12-21T18:00:00+00:00`
- `2023-12-22T09:00:00+00:00`
- the negative bars-8 runtime family
- seam-A single-veto semantics
- aged-weak continuation rows on `2023-12-28T09:00:00+00:00` and `2023-12-30T21:00:00+00:00`
- global confidence-floor retuning
- global edge-floor retuning
- classifier edits
- forced defensive outcomes
- forced continuation outcomes
- default-path changes

## Intended falsifier

Retire this candidate if any of the following turns out to be true:

- helping `2023-12-20T03:00:00+00:00` requires also including `2023-12-21T18:00:00+00:00` or `2023-12-22T09:00:00+00:00`
- the candidate only works by retuning global floors or classifier logic
- the row is no longer best explained as a first-row continuation-persistence question
- the runtime proof would need to alter seam-A or aged-weak semantics as its primary mechanism

## Scope

- **Scope IN:**
  - `docs/decisions/ri_policy_router_bars7_continuation_persistence_candidate_packet_2026-04-27.md`
  - `GENESIS_WORKING_CONTRACT.md`
- **Scope OUT:**
  - `src/**`
  - `tests/**`
  - `config/**`
  - `results/**`
  - `artifacts/**`
  - bars-8 low-zone runtime family
  - seam-A single-veto semantics
  - aged-weak continuation semantics
  - classifier edits
  - default-path changes
- **Expected changed files:**
  - `docs/decisions/ri_policy_router_bars7_continuation_persistence_candidate_packet_2026-04-27.md`
  - `GENESIS_WORKING_CONTRACT.md`
- **Max files touched:** `2`

## Gates required

- minimal markdown/reference sanity on the changed files
- diff-scope confirmation that only this packet and `GENESIS_WORKING_CONTRACT.md` changed in this slice
- explicit self-review for silent widening back into the closed bars-8 family

## Stop Conditions

- any attempt to bundle `2023-12-20T03:00:00+00:00` back together with the two later low-zone rows
- any wording that revives the negative bars-8 runtime family
- any wording that implies runtime authority from this packet alone
- any drift toward global floor/classifier retuning

## Output required

- one repo-visible candidate anchor for the separate bars-7 row
- one updated working contract that points the next admissible runtime packet at this exact row rather than the closed bars-8 family
