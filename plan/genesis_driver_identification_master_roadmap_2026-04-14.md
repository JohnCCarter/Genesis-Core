# Genesis driver identification — master roadmap

Date: 2026-04-14
Mode: `RESEARCH`
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: `closed / bounded closeout complete / docs-only authority`
Supersedes as live continuation anchor: `plan/feature_attribution_post_phase14_reactivation_roadmap_2026-04-02.md`

## Why this roadmap exists

We have accumulated several valid research slices, but the lane has become too fragmented.
This roadmap exists to force convergence on the actual question:

> What most plausibly drives Genesis on the currently locked evidence surface?

This is **not** a blank-slate roadmap.
It starts from already established results and defines the minimum remaining slices needed to either:

1. keep `emergent_system_behavior` as the best-supported driver-level conclusion and stop, or
2. legitimately elevate a narrower mechanism class above the current residual status.

## What is already established

The following is already supported on the currently locked research surface.
These points are not open-ended brainstorming inputs anymore.

### A. Current best-supported origin hypothesis

`results/research/fa_v2_adaptation_off/EDGE_ORIGIN_REPORT.md` currently identifies the best-supported origin hypothesis as:

- `emergent_system_behavior`

That is a **bounded synthesis conclusion**, not an exclusive causal proof.
But it is the current default answer until a later slice legitimately beats it.

### B. Rejected explanations on the locked surface

The current locked surface already rejects these as supported primary explanations:

- signal-layer edge
- state-dependent concentration
- statistical artifact

### C. Observational survival result already exists

The Phase 4 survival-boundary lane established a deterministic observational separation between survivor and collapse rows on the locked sizing-eligible cohort.

The important takeaway is:

- system survival is not random on the locked surface
- but this boundary is **not itself proof of edge**

### D. Execution evidence improved, but did not close the mechanism question

The execution-proxy lane added a real deterministic proxy price-path surface.
That matters because execution is no longer fully opaque.

But the repository still does **not** have authority to claim:

- realized execution quality as the edge source
- slippage as the edge source
- latency/queue effects as the edge source

So `execution_inefficiency` remains unresolved.

### E. Residual classes are explicitly still unresolved

The current locked surface keeps these residual mechanism classes at `UNATTESTED`:

- `execution_inefficiency`
- `regime_independent_drift`
- `structural_market_microstructure`

### F. Current-route feature-attribution restart already narrowed the live movers

The already closed post-Phase-14 feature-attribution reactivation roadmap established the most important executable-route carry-forward ranking:

1. `Volatility sizing cluster` — strongest current-route mover
2. `Signal-adaptation threshold cluster` — clearest harmful current-route surface
3. admitted sizing interaction ladder

This does **not** yet mean any of those are the full edge mechanism.
It means these are the strongest live candidates on the executable route.

## Main program objective

The objective from here is to close the question in one of three admissible ways:

### Outcome 1 — stop with current best answer

If no later slice legitimately upgrades a narrower mechanism class, stop with:

- `emergent_system_behavior` remains the best-supported explanation

### Outcome 2 — narrow the driver class honestly

If a later slice produces enough bounded evidence, upgrade to a narrower statement such as:

- sizing-governed preserved system
- execution-shaped but not execution-proven system
- drift-compatible residual system

Only if the locked or newly authorized surface genuinely supports it.

### Outcome 3 — escalate to a stricter lane

If the remaining question cannot be answered honestly on the current artifact surface, stop and explicitly say that a stricter evidence-capture lane is required.

## Global constraints

- no default behavior change
- no runtime changes in this roadmap by default
- no Optuna
- no new tuning campaign
- no architecture redesign
- one admissible slice at a time
- preserve historical-vs-current-route provenance split
- do not silently convert proxy evidence into causal execution authority
- do not reopen resolved/rejected explanations unless a new governed surface explicitly justifies it

## Convergence rules

This roadmap is explicitly designed to prevent endless looping.

### Hard stop rules

Stop the lane immediately if any of the following becomes true:

1. two consecutive slices fail to upgrade or narrow the mechanism picture meaningfully
2. a slice depends on evidence that is not present on the locked or explicitly authorized surface
3. a slice starts drifting into runtime redesign, tuning, or implicit promotion logic
4. the only path forward requires new artifact-production authority

### Lane close rule

Close the lane once one of these is true:

- `emergent_system_behavior` survives all remaining bounded slices
- a narrower driver statement becomes best-supported
- the remaining uncertainty is strictly an evidence-capture problem and not a reasoning problem

## Priority order from here

This is the enforced next-step order.
Do not skip ahead unless a prior phase explicitly says to stop.

1. execution-proxy partition slice
2. sizing-chain synthesis slice
3. residual drift-separation slice
4. microstructure triage decision
5. final synthesis and closeout

## Phase 0 — roadmap freeze and evidence ledger

### Goal

Turn the current fragmented research state into one live working roadmap with explicit stop conditions.

### Status

- `completed by this document`

### Deliverable

- `plan/genesis_driver_identification_master_roadmap_2026-04-14.md`

### Exit criteria

- one active roadmap anchor exists
- older roadmap is treated as historical predecessor, not live execution order
- next slice is unambiguous

## Phase 1 — execution-proxy partition slice

### Status

- `completed on docs-only basis`
- packet anchor: `docs/governance/execution_proxy_partition_phase1_packet_2026-04-14.md`
- analysis anchor: `docs/analysis/execution_proxy_partition_phase1_2026-04-14.md`
- verdict: `stricter execution lane justified`

### Why this is first

This is the highest-information, lowest-risk next slice.
It uses an already generated proxy surface and does not require runtime changes.

### Goal

Determine whether the new proxy execution surface actually narrows the driver question or merely confirms that execution remains bounded-but-incomplete.

### Core question

Does the proxy surface contain a strong asymmetry that materially narrows the Genesis driver story, or does it only reduce uncertainty without upgrading execution as a supported class?

### Required inputs

- `docs/analysis/execution_proxy_first_read_2026-04-02.md`
- local home-machine artifacts under `results/research/fa_v2_adaptation_off/phase10_execution_proxy_evidence/`
- `results/research/fa_v2_adaptation_off/EDGE_ORIGIN_REPORT.md`
- `docs/analysis/execution_inefficiency_artifact_gap_2026-04-02.md`

### Required partition axes

- `full-window` vs `sparse-window`
- resolved vs omitted exit proxy price
- winners vs losers on the realized ledger
- short horizons vs longer horizons

### Required output

- one packet for the partition slice
- one analysis memo with a verdict from this closed set:
  - `execution still unresolved`
  - `execution weakened as candidate`
  - `execution strengthened but still non-authoritative`
  - `stricter execution lane justified`

### Exit criteria

At least one of the following must be true:

- execution becomes clearly less plausible as the main driver
- execution becomes more plausible but still bounded
- execution cannot move further without a stricter surface

If none of those is achieved, stop and mark the slice inconclusive.

### Closeout note

Phase 1 is now closed.
The partitioned proxy read showed that the strongest favorable execution-proxy behavior is concentrated in incomplete proxy subsets, especially the `sparse-window` / omitted-exit region.
That is enough to justify a future stricter execution lane, but not enough to keep spending bounded-slice effort on the same proxy-only surface.

The next bounded move on the current roadmap is therefore:

- **Phase 2 — sizing-chain synthesis**

## Phase 2 — sizing-chain synthesis slice

### Status

- `completed on docs-only basis`
- packet anchor: `docs/governance/sizing_chain_synthesis_phase2_packet_2026-04-14.md`
- analysis anchor: `docs/analysis/sizing_chain_synthesis_phase2_2026-04-14.md`
- conclusion: `sizing chain matters but does not beat emergent_system_behavior`

### Why this is second

If execution remains bounded, the strongest remaining live route-specific story is the sizing chain.
This phase is where we test whether Genesis is best understood as a preserved system whose edge expression is governed primarily by sizing/risk shaping rather than signal alpha.

### Goal

Fuse the following into one bounded driver ladder:

- survival-boundary result
- current-route `Volatility sizing cluster` salience
- admitted sizing interaction ladder
- current-route `Signal-adaptation threshold cluster` harmfulness

### Core questions

- Is Genesis primarily a sizing-governed preserved system?
- Is `Volatility sizing cluster` a direct driver, a risk shaper, or a confounded mover?
- Does `Signal-adaptation threshold cluster` explain degradation more clearly than any positive unit explains edge creation?
- Does the sizing story materially narrow `emergent_system_behavior`, or only describe one important subsystem inside it?

### Required inputs

- `plan/feature_attribution_post_phase14_reactivation_roadmap_2026-04-02.md`
- `docs/analysis/feature_attribution_post_phase14_rebaseline_reconciliation_2026-04-02.md`
- `docs/governance/survival_boundary_phase4_packet_2026-04-01.md`
- `results/research/fa_v2_adaptation_off/EDGE_ORIGIN_REPORT.md`

### Required output

- one synthesis memo with a driver ladder using only this label set:
  - `direct driver candidate`
  - `risk-shaping contributor`
  - `harmful surface`
  - `confounded mover`
  - `inert on current route`

### Exit criteria

The phase must end with one explicit conclusion:

- `sizing chain materially narrows Genesis`
- or `sizing chain matters but does not beat emergent_system_behavior`

If neither can be supported honestly, stop and carry forward uncertainty.

### Closeout note

Phase 2 is now closed.
The synthesis confirmed that the sizing path is the strongest bounded subsystem story remaining after the execution-proxy partition: survival is governed by a deterministic `base_size > 0` preservation boundary, `Volatility sizing cluster` is the strongest current-route mover, and the admitted sizing surfaces form one multiplicative interaction ladder.

But the same synthesis also confirmed that the sizing chain still stops short of exclusive mechanism authority:

- the survival boundary is observational preservation evidence, not proof of edge
- the strongest sizing-cluster effects remain mixed or confounded
- the carried-forward Phase 14 system-level conclusion is not honestly beaten by the current bounded sizing evidence

The next bounded move on the current roadmap is therefore:

- **Phase 3 — residual drift-separation**

## Phase 3 — residual drift-separation slice

### Status

- `completed on docs-only basis`
- packet anchor: `docs/governance/residual_drift_separation_phase3_packet_2026-04-14.md`
- analysis anchor: `docs/analysis/residual_drift_separation_phase3_2026-04-14.md`
- verdict: `drift compatibility strengthened`

### Why this is third

Only do this after execution and sizing have been re-read.
Otherwise drift becomes a vague leftover bucket instead of a disciplined residual test.

### Goal

Test whether the already known combination:

- non-state dependence
- temporal stability
- limited execution/selection causality

can be narrowed into something more informative than a generic residual class.

### Core questions

- Does the residual pattern strengthen a drift-compatible reading?
- Or is drift still merely a compatibility statement, not a mechanism statement?
- After the execution and sizing re-reads, does drift become more plausible or just remain unattested?

### Required inputs

- `docs/analysis/regime_independent_drift_artifact_gap_2026-04-02.md`
- `results/research/fa_v2_adaptation_off/EDGE_ORIGIN_REPORT.md`
- the outputs of Phase 1 and Phase 2

### Required output

- one residual memo with a verdict from this closed set:
  - `drift remains unattested`
  - `drift compatibility strengthened`
  - `drift-specific stricter lane justified`

### Exit criteria

This phase is successful only if it changes the residual interpretation honestly.
If it merely restates the existing gap note, stop and do not open additional drift slices.

### Closeout note

Phase 3 is now closed.
The bounded reread did not attest drift as a mechanism, but it did strengthen drift as the cleanest residual interpretation once execution was shown to require a stricter lane and the sizing chain was shown to remain subsystem-level rather than exclusive.

The next bounded move on the current roadmap is therefore:

- **Phase 4 — microstructure triage**

## Phase 4 — microstructure triage decision

### Status

- `completed on docs-only basis`
- packet anchor: `docs/governance/microstructure_triage_phase4_packet_2026-04-14.md`
- analysis anchor: `docs/analysis/microstructure_triage_phase4_2026-04-14.md`
- decision: `future stricter lane only`

### Why this is not earlier

`structural_market_microstructure` is the weakest current near-term candidate because the repository does not yet expose a packet-authorized microstructure surface.
So this is a triage decision, not a default active research lane.

### Goal

Make a deliberate yes/no decision on whether microstructure deserves any further time under current constraints.

### Allowed outcomes

- `stop / keep unresolved`
- `future stricter lane only`

### Default expectation

Default to:

- do **not** spend further bounded-slice time here unless a new evidence source is explicitly authorized

### Exit criteria

A single written decision exists and the lane is either frozen or explicitly deferred to a stricter future program.

### Closeout note

Phase 4 is now closed.
The triage decision is that structural market microstructure remains unresolved, but it is no longer worth bounded-slice time under the current artifact constraints.

The next bounded move on the current roadmap is therefore:

- **Phase 5 — final synthesis and closure**

## Phase 5 — final synthesis and closure

### Status

- `completed on docs-only basis`
- analysis anchor: `docs/analysis/genesis_driver_final_synthesis_2026-04-14.md`
- final label: `emergent_system_behavior remains best-supported`

### Goal

Finish the entire lane with one honest answer to:

> What most plausibly drives Genesis on the current evidence surface?

### Required structure of the final answer

The final synthesis must contain five parts:

1. **Current best-supported driver statement**
2. **What was ruled out**
3. **What still remains unresolved**
4. **Why the chosen conclusion beats the alternatives**
5. **Whether further work is justified or not**

### Allowed final labels

The final synthesis must end in one of these bounded labels:

- `emergent_system_behavior remains best-supported`
- `sizing-governed preserved system is best-supported`
- `execution-shaped but still non-authoritative`
- `drift-compatible residual remains unresolved`
- `stricter evidence lane required`

### Lane closure rule

Once the final synthesis is written, the lane closes unless a stricter successor lane is explicitly opened.

### Closeout note

Phase 5 is now closed.
The bounded Genesis driver-identification program ends here with one top-level closeout:

- `emergent_system_behavior` remains the best-supported broader explanation on the current evidence surface

The strongest bounded subsystem story carried forward from this roadmap is the sizing chain, while any deeper progress on execution, drift, or microstructure now requires separately justified stricter successor lanes.

## Expected file map

This roadmap expects future outputs to follow this placement discipline:

- packets: `docs/governance/`
- analysis memos: `docs/analysis/`
- roadmap anchors: `plan/`
- generated result artifacts: existing governed `results/research/...` roots only when already authorized

## Working-tree hygiene note

There is currently an unrelated local modification in:

- `.github/agents/Codex53.agent.md`

That file is out of scope for this roadmap and must not be mixed into the Genesis-driver slice by accident.

## Bottom line

This roadmap is now closed.

The program from here is no longer “keep exploring until something feels right.”

It is:

1. partition the execution proxy surface
2. synthesize the sizing chain
3. test whether residual drift meaningfully strengthens
4. explicitly triage microstructure out unless new authority appears
5. write one final synthesis and stop

Those steps did not materially beat the current Phase 14 answer, so the correct closeout is:

- `emergent_system_behavior` remains the best-supported explanation on the current evidence surface.
