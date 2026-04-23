# RI router replay counterfactual closeout report

Date: 2026-04-23
Branch: `feature/ri-role-map-implementation-2026-03-24`
Mode: `RESEARCH`
Risk: `MED`
Path: `Full`
Constraint: research-only synthesis over frozen evidence surfaces; runtime/default/family authority remains unchanged
Packet: `docs/governance/ri_router_replay_implementation_packet_2026-04-23.md`
Skills used: `python_engineering`, `decision_gate_debug`

This document closes the current bounded RI router replay counterfactual lane. It records research-only findings over the fresh replay root and isolated counterfactual reruns on the same frozen input surface. It does not authorize runtime integration, default changes, family authority, promotion claims, or inherited approval from any research-only counterfactual that looked better on this surface.

Any future semantics, runtime, or integration follow-up would require a new packet, fresh scope approval, and separate verification. None is granted here.

## Scope summary

### Scope IN

- `docs/governance/ri_router_replay_implementation_packet_2026-04-23.md`
- `tmp/ri_router_replay_v1_20260423.py`
- `results/research/ri_router_replay_v1/`
- `results/research/ri_router_replay_v1_counterfactual_switch_threshold_1/`
- `results/research/ri_router_replay_v1_counterfactual_min_dwell_1/`
- `results/research/ri_router_replay_v1_counterfactual_hysteresis_0/`
- `results/research/ri_router_replay_v1_counterfactual_switch_threshold_1_min_dwell_1/`
- `results/research/ri_router_replay_v1_counterfactual_switch_threshold_1_min_dwell_1_hysteresis_0/`
- `results/research/ri_router_replay_v1_counterfactual_defensive_transition_mandate_2/`
- `docs/governance/ri_router_replay_counterfactual_closeout_report_2026-04-23.md`
- `GENESIS_WORKING_CONTRACT.md`

### Scope OUT

- `src/**`
- `tests/**`
- `config/**`
- `artifacts/**`
- `scripts/**`
- runtime integration
- backtest execution integration
- family-rule surfaces
- default-path changes
- readiness / promotion claims
- any inherited approval claim from counterfactual research outputs

## What this counterfactual lane resolved

### Baseline defensive scarcity is real and reproducible

The fresh replay baseline already localized a clear compression pattern:

- raw defensive candidates = `30`
- selected defensive rows = `3`

Interpretation:

- The lane no longer needs another slice merely to prove that raw defensive states exist.
- The remaining question is why those states fail to survive routing and stability controls.

### The generic gate story is now disproven

The counterfactual slices resolved that the three named stability levers do not contribute equally:

1. `switch_threshold` is active and materially changes policy separation.
2. `min_dwell` changes routed activity strongly, but mostly by expanding continuation rather than by improving defensive separation.
3. `hysteresis` by itself is a no-op on the baseline surface.

Interpretation:

- “Defensive starvation is caused by the whole stability stack” is now too vague to be useful.
- The bottleneck can be localized more precisely than that.

### The best explanatory model is now semantic rather than purely threshold-based

The most important result in this lane is that two different-looking slices produced exactly the same routed outcome:

- `switch_threshold: 2 -> 1`
- `defensive_transition_state mandate_level/confidence: 1 -> 2`

Both produced the same result on the frozen evidence surface:

- policy counts: continuation `86`, defensive `13`, no-trade `47`
- defensive trades: `9`
- continuation trades: `83`
- defensive profit factor: `1.806219`
- recommendation: `NEEDS_REVISION`

Interpretation:

- The practical effect of lowering the global threshold is equivalent here to raising the raw mandate of the defensive branch.
- That is strong evidence that the deeper explanatory issue is the raw defensive mandate assignment, not a generic global threshold problem.

## Counterfactual findings by slice

### Baseline

- continuation `93`
- defensive `3`
- no-trade `50`
- blocked switches `49`
- no-trade count `55`
- defensive trades `2`
- continuation trades `89`
- continuation profit factor `1.594971`
- defensive profit factor `0.0`

### `switch_threshold: 2 -> 1`

- continuation `86`
- defensive `13`
- no-trade `47`
- blocked switches `50`
- no-trade count `54`
- defensive trades `9`
- continuation trades `83`
- defensive profit factor `1.806219`

Interpretation:

- This is still the strongest pure policy-separation slice in the current lane.
- Defensive scarcity becomes materially less severe.

### `min_dwell: 3 -> 1`

- continuation `120`
- defensive `2`
- no-trade `24`
- blocked switches `28`
- no-trade count `32`
- defensive trades `1`
- continuation trades `113`
- continuation profit factor `1.983847`
- defensive profit factor `0.0`

Interpretation:

- Lowering dwell alone mainly expands continuation and reduces no-trade retention.
- It does not improve defensive separation.

### `hysteresis: 1 -> 0`

- exact parity with baseline

Interpretation:

- Hysteresis is not an active first-order blocker on the baseline surface.

### `switch_threshold: 1` + `min_dwell: 1`

- continuation `120`
- defensive `7`
- no-trade `19`
- blocked switches `23`
- no-trade count `30`
- defensive trades `3`
- continuation trades `113`
- defensive profit factor `7.061918`

Interpretation:

- This slice reduces no-trade pressure and blocked-switch counts sharply.
- But it does so mostly by expanding continuation, not by creating the clearest defensive separation.
- The very high defensive profit factor must be treated as small-sample-only because it comes from `3` trades.

### `switch_threshold: 1` + `min_dwell: 1` + `hysteresis: 0`

- exact parity with the previous combined slice

Interpretation:

- The labeled `switch_blocked_by_hysteresis` rows are not actually controlled by the additive hysteresis term on this surface.

### `defensive_transition_state mandate/confidence: 1 -> 2`

- exact parity with `switch_threshold: 2 -> 1`

Interpretation:

- This is the cleanest semantic result in the lane.
- It localizes the bottleneck to the ranking of one specific defensive branch, not to a generic global instability rule.

## What the hysteresis label was actually hiding

The diagnostic check on rows labeled `switch_blocked_by_hysteresis` showed:

- blocked rows = `23`
- all `23` rows were raw defensive rows
- all `23` had raw mandate `1`
- previous selected policy was always continuation
- previous mandate was `3` in `19` rows and `2` in `4` rows

Interpretation:

- Even with `hysteresis = 0`, these rows still fail the comparison because `1 < 2` or `1 < 3`.
- So the apparent hysteresis blocker is, on this evidence surface, really a mandate-gap blocker.

## Final lane status

### Counterfactual-roadmap completion verdict

The bounded counterfactual lane is now complete enough to close in the following sense:

- the main stability levers were isolated one at a time
- the strongest-looking compound slices were tested
- the apparent hysteresis blocker was reduced to a more precise mandate-gap explanation
- the best available explanatory hypothesis is now local and falsifiable

Interpretation:

- The lane no longer needs another generic “one more gate toggle” slice.
- Further useful progress would now require a new, explicitly semantic question.

### Replay-root status remains unchanged

The current replay roots still remain research-only and observational-only.

- `recommendation = NEEDS_REVISION`
- `recommendation_scope = observed_replay_quality_only`

Interpretation:

- The lane closes with explanatory success, not with runtime readiness.
- Counterfactual improvement in a frozen replay root does not grant integration approval.

## What remains unresolved but bounded

1. Whether `defensive_transition_state` should semantically be treated as a mandate-2 candidate rather than a mandate-1 candidate.
2. Whether the defensive subset remains meaningful once evaluated beyond this frozen replay surface.
3. Whether any future semantics change would preserve the desired balance between defensive support and continuation overreach on broader evidence surfaces.

Interpretation:

- Remaining uncertainty is now narrow and explicit.
- It is no longer a missing-observability problem.

## Prerequisites for any future semantics or runtime proposal

1. **New governance lane required**
   - any follow-up must open a new packet with fresh Scope IN/OUT
2. **No inherited runtime approval**
   - this report does not authorize runtime, backtest, config, or deployment changes
3. **Objective must be explicit**
   - any future lane must say whether it is:
     - research-only semantics evaluation,
     - shadow-only instrumentation,
     - or an actual behavior-changing proposal
4. **Default behavior remains unchanged unless separately authorized**
   - the current lane closes under `RESEARCH` with all runtime/default paths unchanged
5. **Family and readiness boundaries remain out of scope**
   - this lane does not authorize cross-family routing, promotion, readiness, or champion claims

## Boundary proof

- Runtime is unchanged.
- The tracked research implementation script remains unchanged.
- All counterfactuals were executed as isolated reruns against the same frozen evidence surface.
- The current closeout does not change recommendation semantics or authorize integration.

## Exact gates run and outcomes

### Commands executed

1. Repeated read-only / isolated counterfactual reruns of `tmp/ri_router_replay_v1_20260423.py` via the workspace Python interpreter with in-memory logic or parameter overrides only, each writing to its own fresh research root:
   - `results/research/ri_router_replay_v1_counterfactual_switch_threshold_1/`
   - `results/research/ri_router_replay_v1_counterfactual_min_dwell_1/`
   - `results/research/ri_router_replay_v1_counterfactual_hysteresis_0/`
   - `results/research/ri_router_replay_v1_counterfactual_switch_threshold_1_min_dwell_1/`
   - `results/research/ri_router_replay_v1_counterfactual_switch_threshold_1_min_dwell_1_hysteresis_0/`
   - `results/research/ri_router_replay_v1_counterfactual_defensive_transition_mandate_2/`
   - Result: `PASS`
2. Determinism gate for each slice:
   - each output root was rerun a second time with identical input surface and override shape
   - each slice produced identical approved-output hashes across reruns
   - Result: `PASS`
3. Workspace-isolation proof:
   - `git status --short`
   - Result: `PASS` (`no tracked file drift after the research reruns`)
4. Focused diagnostic check on hysteresis-labeled rows:
   - read-only Python analysis over the combined slice state transitions
   - Result: `PASS` (`all 23 hysteresis-labeled rows reduced to raw mandate 1 vs continuation mandate 2/3`)

## Residual risks

- The replay surface still remains `NEEDS_REVISION`.
- Defensive support is still sparse in absolute terms even in the better slices.
- A future semantics proposal could over-read this frozen-surface result if it treats the mandate hypothesis as already approved rather than merely bounded and better localized.

## READY_FOR_REVIEW evidence completeness

- Mode/risk/path: captured above
- Scope IN/OUT: captured above
- Gate outcomes: captured above
- Evidence paths:
  - `docs/governance/ri_router_replay_implementation_packet_2026-04-23.md`
  - `tmp/ri_router_replay_v1_20260423.py`
  - `results/research/ri_router_replay_v1/`
  - `results/research/ri_router_replay_v1_counterfactual_switch_threshold_1/`
  - `results/research/ri_router_replay_v1_counterfactual_min_dwell_1/`
  - `results/research/ri_router_replay_v1_counterfactual_hysteresis_0/`
  - `results/research/ri_router_replay_v1_counterfactual_switch_threshold_1_min_dwell_1/`
  - `results/research/ri_router_replay_v1_counterfactual_switch_threshold_1_min_dwell_1_hysteresis_0/`
  - `results/research/ri_router_replay_v1_counterfactual_defensive_transition_mandate_2/`

## Bottom line

The bounded RI router replay counterfactual lane is now complete enough to close as an explanatory research lane. It successfully isolated the main named stability levers, showed that `switch_threshold` and raw defensive mandate ranking are behaviorally equivalent on this surface, and reduced the apparent hysteresis blocker to a narrower mandate-gap explanation. But it does **not** end in runtime approval: the replay roots remain `NEEDS_REVISION`, and any semantics or integration follow-up would have to begin as a brand-new governance lane with explicit scope and fresh approval.
