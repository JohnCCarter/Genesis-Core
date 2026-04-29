# RI policy router weak pre-aged single-veto release low-zone insufficient-evidence diagnosis

Date: 2026-04-27
Branch: `feature/ri-role-map-implementation-2026-03-24`
Mode: `RESEARCH`
Status: `docs-only / analysis-lane diagnosis / no runtime authority`

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `branch:feature/ri-role-map-implementation-2026-03-24`
- **Risk:** `MED` — why: this slice refines one residual surface from the completed single-veto fail-set evidence using a read-only router-meta probe, but does not modify runtime, config, tests, or authority surfaces.
- **Required Path:** `Quick`
- **Lane:** `Research-evidence` — why this is the cheapest admissible lane now: the residual blocked-long set is already split, and the cheapest next clarification is to re-anchor what still belongs to the live low-zone `insufficient_evidence` surface after the blocked downstream-handoff verification invalidated the older three-row picture.
- **Objective:** re-anchor the low-zone residual surface by separating the current raw low-zone no-trade rows from the provisional `2023-12-20 03:00` inclusion after same-pocket single-veto de-chaining has already been proven.
- **Base SHA:** `HEAD`

## Scope

### Scope IN

- `docs/governance/ri_policy_router_weak_pre_aged_single_veto_release_failset_evidence_2026-04-27.md`
- `docs/governance/ri_policy_router_weak_pre_aged_single_veto_release_residual_blocked_longs_diagnosis_2026-04-27.md`
- `src/core/strategy/ri_policy_router.py`
- one new docs-only diagnosis note
- one read-only evaluation-hook probe on the exact fail-B subject to inspect low-zone router metrics

### Scope OUT

- runtime edits
- config edits
- test edits
- tracked artifact writes beyond this diagnosis note
- findings-bank writes
- aged-weak continuation candidate framing
- seam-B runtime intervention
- keep-set or stress-set verification

## Evidence inputs

- `docs/governance/ri_policy_router_weak_pre_aged_single_veto_release_failset_evidence_2026-04-27.md`
- `docs/governance/ri_policy_router_weak_pre_aged_single_veto_release_residual_blocked_longs_diagnosis_2026-04-27.md`
- `docs/governance/ri_policy_router_low_zone_near_floor_insufficient_evidence_downstream_handoff_implementation_packet_2026-04-27.md`
- `src/core/strategy/ri_policy_router.py`
- read-only candidate carrier input: `tmp/policy_router_evidence/tBTCUSD_3h_slice8_runtime_bridge_weak_pre_aged_release_guard_20260424.json`

## Analysis method

The existing decision-row artifacts do not carry `state_out`, router debug, or the threshold values that feed `insufficient_evidence`.

The earlier low-zone diagnosis therefore used a read-only probe over the exact fail-B subject, but the later blocked downstream-handoff verification showed that a naive scan of `research_policy_router_debug` can over-read stale state on bars where the router did not actually run.

This re-anchor keeps the same exact fail-B subject and canonical env, but now treats the earlier three-row picture as provisional and defers to the filtered router-executed replay evidence already recorded in the blocked runtime packet.

The relevant router floors from `src/core/strategy/ri_policy_router.py` are:

- `clarity_floor = 24.0`
- `confidence_floor = 0.515`
- `edge_floor = 0.035`

## Diagnosis

### 1. The earlier three-row picture does not survive router-executed filtering

The first low-zone diagnosis treated the following rows as one low-zone residual surface:

- `2023-12-20T03:00:00+00:00`
- `2023-12-21T18:00:00+00:00`
- `2023-12-22T09:00:00+00:00`

The blocked downstream-handoff verification later showed why that was too coarse:

- a naive scan could over-count by reading stale `research_policy_router_debug`
- after filtering to bars where the router actually ran, the live raw low-zone no-trade residual surface isolates only:
  - `2023-12-21T18:00:00+00:00`
  - `2023-12-22T09:00:00+00:00`

Both of those rows now sit on the same updated structural signature:

- `zone = low`
- `bars_since_regime_change = 8`
- `raw_target_policy = RI_no_trade_policy`
- `selected_policy = RI_no_trade_policy`
- `switch_reason = insufficient_evidence`

So the low-zone evidence-floor surface still exists, but it is now a **two-row bars-8 surface**, not the earlier three-row bars-7 picture.

### 2. The two live low-zone rows still fail confidence and edge, not clarity

Observed router metrics on the two live rows are:

- `2023-12-21T18:00:00+00:00`
  - `clarity_score = 35`
  - `confidence_gate = 0.5068924643`
  - `action_edge = 0.0137849287`
- `2023-12-22T09:00:00+00:00`
  - `clarity_score = 35`
  - `confidence_gate = 0.5052986704`
  - `action_edge = 0.0105973409`

Compared with the router no-trade floors:

- clarity floor `24.0` → both rows are comfortably above floor
- confidence floor `0.515` → both rows are below floor
- edge floor `0.035` → both rows are materially below floor

So the live low-zone residual rows are **not** low-clarity rows.
They are dual-floor failures on:

- `confidence_gate`
- `action_edge`

### 3. `2023-12-20 03:00` is now better understood as a separate continuation-persistence seam

The filtered router-executed replay from the blocked downstream-handoff slice no longer supports carrying `2023-12-20T03:00:00+00:00` inside the same raw low-zone no-trade packet.

On that filtered read, the row instead behaves like a separate bars-7 continuation-persistence seam with:

- `selected_policy = RI_continuation_policy`
- `raw_target_policy = RI_defensive_transition_policy`
- `previous_policy = RI_continuation_policy`
- `switch_reason = confidence_below_threshold`
- `dwell_duration = 8`

That is a different shape from the two live low-zone rows above.
So `2023-12-20 03:00` should no longer be treated as part of the low-zone near-floor insufficient-evidence residual packet.

### 4. This is still not a disguised seam-A release problem

The actual seam-A single-veto row at `2023-12-22T15:00:00+00:00` looks very different:

- `clarity_score = 39`
- `confidence_gate = 0.5411402721`
- `action_edge = 0.0822805443`
- `raw_target_policy = RI_continuation_policy`
- `selected_policy = RI_no_trade_policy`
- `switch_reason = WEAK_PRE_AGED_CONTINUATION_RELEASE_GUARD`

And the immediately following release row at `2023-12-22T18:00:00+00:00` is stronger still:

- `clarity_score = 40`
- `confidence_gate = 0.5446714926`
- `action_edge = 0.0893429852`
- `raw_target_policy = RI_continuation_policy`
- `selected_policy = RI_continuation_policy`
- `switch_reason = continuation_state_supported`

So the live low-zone residual rows are not “almost the same as the seam-A row but still blocked by the latch.”

They remain on the **other side** of the raw no-trade floor, while the real seam-A row has already crossed into continuation-support territory.

### 5. The live low-zone residual surface is an evidence-floor problem, not a clarity problem

Because clarity stays healthy at `35`, the chosen residual surface is not best described as generic weak signal quality.

More precise statement:

- the model-side / regime-side clarity proxy is already high enough
- but `confidence_gate` remains just below `0.515`
- and `action_edge` remains far below `0.035`

That means the live low-zone rows are better understood as an **evidence-floor** issue concentrated in:

- low conviction separation (`action_edge`)
- slightly subfloor decision confidence (`confidence_gate`)

not in overall clarity collapse.

### 6. The cheapest honest next candidate must stay explicit about the split

If work continues on this chosen surface, the next bounded candidate should not be framed as:

- another seam-A release-latch refinement
- a generic “insufficient evidence” mystery
- or an aged-weak continuation retune

It would need to be framed explicitly as a low-zone evidence-floor question around rows with:

- healthy clarity
- subfloor confidence
- very small action edge
- regime age now locked at `8`

And if the user wants to keep following `2023-12-20 03:00`, that should now be reopened as a **separate bars-7 continuation-persistence seam**, not bundled back into the two-row low-zone packet.

Without that framing, a future slice risks solving the wrong problem again.

## Bounded conclusion

The live low-zone residual blocked baseline longs are not residual seam-A latch rows and not low-clarity rows.

They are a cleaner, narrower surface:

- `2023-12-21T18:00:00+00:00`
- `2023-12-22T09:00:00+00:00`
- `zone = low`
- `bars_since_regime_change = 8`
- `clarity_score = 35`
- `confidence_gate < 0.515`
- `0.010 <= action_edge <= 0.014`
- `switch_reason = insufficient_evidence`

And `2023-12-20T03:00:00+00:00` should now be treated separately as a bars-7 continuation-persistence seam.

So the next candidate on the low-zone path, if any, would have to address a **two-row bars-8 low-zone evidence-floor trade-off** rather than the already-bounded seam-A single-veto mechanism.

## Next admissible implication

If the user wants the cheapest next follow-up after this diagnosis, it should be a bounded candidate-framing / packet slice for the two-row low-zone evidence-floor surface only.

That slice should stay explicit about all of the following:

- low-zone only
- exactly the two live rows above
- `bars_since_regime_change = 8`
- confidence/edge floor pressure as the live constraint
- no reopening of the already-bounded seam-A single-veto mechanism
- no bundling with the older `AGED_WEAK_CONTINUATION_GUARD` rows

If instead the user wants to pursue `2023-12-20 03:00`, reopen that as a separate continuation-persistence diagnosis rather than as a low-zone evidence-floor packet.

## Output of this slice

- one repo-visible diagnosis showing that the live low-zone residual rows are driven by confidence/edge floor failure rather than clarity collapse or seam-A latch carry
- one sharper basis for a future two-row low-zone candidate-framing slice that does not silently absorb `2023-12-20 03:00`
