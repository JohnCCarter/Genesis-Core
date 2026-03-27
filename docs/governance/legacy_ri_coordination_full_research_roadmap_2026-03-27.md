# Genesis-Core legacy + RI + coordination full research roadmap

Date: 2026-03-27
Status: tracked / roadmap reference / no implementation authority
Lane: `run_intent: research_experiment`

## How to use this roadmap

- Treat this document as a phased plan, not as authority to implement everything.
- At each step:
  - identify current state
  - identify the current phase
  - identify the next admissible step only
  - define the minimal artifact for that step
  - list what must not be touched
- Fail closed on ambiguity.

## Global principles

1. Determinism over performance.
2. Fail closed on ambiguity.
3. No mixed family surfaces.
4. Legacy and RI remain separate internal strategy families.
5. Coordination, routing, and ensemble logic must live above the families, not inside them.
6. No comparison, readiness, or promotion unless explicitly opened later.
7. Every phase ends with a decision gate:
   - continue
   - falsify
   - stop
   - open new lane

## Phase 0 - lock current baseline

### Objective

Freeze current understanding before new research begins.

### Deliverables

- one tracked baseline summary that locks:
  - Legacy current reference state
  - RI plateau state
  - explicit statement that current RI local surfaces are exhausted
  - explicit statement that Legacy and RI remain separate families

### Constraints

- no new tuning
- no new coordination logic
- no new launch

### Decision gate

Proceed only when baseline is explicit and closed.

## Phase 1 - define the experiment map

### Objective

Create one governed experiment map covering all admissible next research directions.

### Must define these experiment classes

#### A. RI internal next-hypothesis experiments

Examples:

- new signal hypothesis
- new regime hypothesis
- new decision or gating hypothesis
- new objective or scoring hypothesis

#### B. Legacy internal next-hypothesis experiments

Examples:

- Legacy-specific signal improvements
- Legacy-specific decision or gating improvements
- Legacy robustness studies

#### C. Cross-family coordination experiments

Examples:

- Legacy primary plus RI veto
- RI primary plus Legacy veto
- regime-based router
- confidence-based router
- ensemble arbitration
- abstain or no-trade coordinator

#### D. Meta-governance experiments

Examples:

- admissibility for coordination lanes
- authority boundaries for router outputs
- classification of research-only coordination artifacts

### Constraints

- no implementation yet
- only define the map and allowed classes

### Decision gate

Choose which experiment class is opened first.

## Phase 2 - RI internal research track

### Objective

Continue RI research only through new hypothesis classes, not local re-tuning of exhausted surfaces.

### Allowed subtracks

#### RI-S1 - signal hypothesis

Examples:

- new features
- revised zone definition
- revised regime signal inputs
- new context inputs

#### RI-S2 - regime hypothesis

Examples:

- alternate regime segmentation
- alternate regime normalization
- alternate authoritative regime mapping

#### RI-S3 - decision hypothesis

Examples:

- EV formula changes
- confidence logic changes
- candidate arbitration logic changes
- gate ordering changes

#### RI-S4 - objective hypothesis

Examples:

- robustness-weighted scoring
- PF ex top trades
- drawdown-sensitive objective

### Required process for each RI subtrack

1. Write one narrow research-direction packet.
2. Choose exactly one hypothesis.
3. Define allowed surface.
4. Define fixed surface.
5. Create config(s).
6. Validate or preflight.
7. Smoke if needed.
8. Launch authorization.
9. Run.
10. Outcome classification:
    - improvement
    - plateau
    - degradation
11. Close or continue.

### Hard constraints

- no reopening exhausted local exit or override tuning
- no family rule mutations without separate authority
- no runtime, readiness, or promotion claims

### Decision gate

If RI improves meaningfully, allow another RI research slice.

If RI plateaus again, falsify that hypothesis class and move to a different RI class or stop RI temporarily.

## Phase 3 - Legacy internal research track

### Objective

Assess whether Legacy still has productive internal research room independent of RI.

### Allowed subtracks

- `L-S1` - Legacy signal hypothesis
- `L-S2` - Legacy regime or context hypothesis
- `L-S3` - Legacy decision or gating hypothesis
- `L-S4` - Legacy objective or robustness hypothesis

### Required process

Same structure as RI:

- one hypothesis only
- one bounded surface
- config(s)
- validation or preflight
- launch authorization
- execution
- strict classification

### Constraints

- do not contaminate Legacy with RI semantics
- do not import RI thresholds or RI gates into Legacy internals
- no mixed family surface

### Decision gate

If Legacy has productive room, continue Legacy-only research.

If not, close that lane and move to coordination-level research.

## Phase 4 - cross-family coordination research

### Objective

Test whether two already-separated families can improve results through an orchestration layer above them.

This phase must not merge families.

### Admissible coordination hypothesis classes

#### C1 - Legacy primary, RI veto

Legacy proposes candidate trade. RI may veto. No RI entry authority.

#### C2 - RI primary, Legacy veto

RI proposes candidate trade. Legacy may veto. No Legacy entry authority.

#### C3 - regime-based router

Router selects exactly one family per context or regime.

#### C4 - confidence-based router

Router selects family based on calibrated confidence or expected-value ranking.

#### C5 - consensus coordinator

Trade only when both families agree.

#### C6 - abstention coordinator

Allow no-trade when neither family clears policy.

### Required ordering

Open these coordination classes in this order unless evidence clearly supports otherwise:

1. Legacy primary plus RI veto
2. RI primary plus Legacy veto
3. Regime-based router
4. Confidence-based router
5. Consensus coordinator
6. More complex ensembles only if simpler classes fail

### Why this order

- simplest interpretation first
- easiest falsification first
- preserves family separation
- minimizes hidden interaction complexity

### Constraints

- do not alter family internals in Phase 4
- coordination logic must be external and explicit
- router must consume family outputs, not mutate family semantics

### Decision gate

If a simple coordination mechanism yields improvement, continue refining coordination research.

If not, do not escalate complexity automatically.

## Phase 5 - router research program

### Objective

If coordination is promising, open router-specific research as its own lane.

### Router hypotheses to test

#### R1 - static regime router

Map regime classes to one family:

- regime A -> Legacy
- regime B -> RI

#### R2 - confidence router

Choose family with the stronger admissible signal.

#### R3 - EV router

Choose family with the stronger expected-value estimate.

#### R4 - drawdown-aware router

Prefer family conditioned on recent drawdown or risk state.

#### R5 - abstain-first router

Default to no-trade unless one family clearly dominates.

### Router artifact requirements

- router spec
- explicit inputs
- explicit output states:
  - choose Legacy
  - choose RI
  - abstain
- explicit tie-handling
- explicit fail-closed behavior

### Router execution requirements

- must be backtestable
- must be deterministic
- must not rewrite family configs
- must log every routing decision

### Router metrics

- validation score
- profit factor
- max drawdown
- trade count
- abstain rate
- family selection frequency
- contribution attribution by family

### Decision gate

If router improves robustness or validation meaningfully, keep the router lane open.

If not, close the router lane and do not escalate to more complex ensemble forms.

## Phase 6 - ensemble or orchestration research

### Objective

Test whether limited higher-order orchestration helps after simple routers are exhausted.

### Allowed forms

- weighted arbitration
- priority stack
- two-stage confirmation
- veto cascades

### Forbidden forms

- hidden blended family semantics
- implicit threshold sharing across families
- automatic parameter mutation from one family into the other

### Requirements

- explicit contract
- explicit attribution
- deterministic logs
- family outputs remain separable

### Decision gate

Continue only if ensemble clearly outperforms simpler router classes.

Otherwise close this phase.

## Phase 7 - comparison lane opening rules

### Objective

Only after a research track shows real promise, open comparison in a controlled way.

### Comparison may open only if

- a research artifact is stable and reproducible
- the artifact is classifiable as comparison-eligible
- authority boundaries are explicit
- family identity remains clear
- no raw research artifact is mislabeled as runtime-valid production artifact

### Comparison subjects may include

- RI vs Legacy internal best candidates
- coordination layer vs Legacy standalone
- coordination layer vs RI standalone
- router candidate vs current reference family baseline

### Constraints

- no readiness
- no promotion
- no champion update
- comparison is not deployment evidence

### Decision gate

If comparison result is meaningful and stable, readiness lane may be considered later.

Otherwise close comparison and return to research.

## Phase 8 - readiness lane opening rules

### Objective

Determine whether a comparison winner is eligible for readiness review.

### Readiness may open only if

- comparison lane is complete
- reproducibility is documented
- runtime-valid artifact exists
- family or coordination identity is explicit
- authority semantics are closed
- no unresolved metadata or materialization ambiguity remains

### Constraints

- readiness is not promotion
- readiness does not imply cutover
- writeback remains closed unless separately authorized

### Decision gate

If readiness is green, promotion lane may be opened separately.

If not, stop and return to research or comparison.

## Phase 9 - promotion lane opening rules

### Objective

Promotion remains a distinct governed lane.

### Promotion can open only if

- readiness explicitly passed
- artifact is runtime-valid
- operational authority is resolved
- change surface is fully understood
- audit trail is complete
- no research-only assumptions remain

### Constraints

- no automatic champion cutover
- no implicit writeback
- no branch-local research result may bypass promotion governance

### Decision gate

Either:

- promote
- reject
- return to readiness or research

## Phase 10 - branch strategy

### Objective

Keep experiment work separated cleanly.

### Recommended branches

1. RI internal research branch
   - for RI-only hypothesis work
2. Legacy internal research branch
   - for Legacy-only hypothesis work
3. Coordination or router experiment branch
   - for cross-family orchestration only
4. Governance or docs branch
   - for packet chains and decision artifacts

### Constraints

- do not mix RI internal changes with router logic in one branch unless explicitly authorized
- do not develop promotion logic inside research branches

## Phase 11 - metrics and evaluation standard

Use one shared evaluation template across all research phases.

### Must extract

- validation score
- profit factor
- max drawdown
- trades
- sharpe
- total return
- duplicate ratio
- zero-trade count
- reproducibility status
- plateau, improvement, or degradation classification

### For coordination and router phases also extract

- per-family selection rate
- abstention rate
- contribution attribution
- veto frequency
- regime-conditioned performance

### Decision discipline

- Never call something an improvement without explicit validation uplift.
- Never call something globally dead when only one local surface was tested.

## Phase 12 - stop conditions

Stop a lane immediately if:

- repeated plateau with no new hypothesis
- degradation with no plausible corrective mechanism
- mixed family semantics appear
- runtime validity becomes ambiguous
- governance packets proliferate without new evidence
- branch scope starts to sprawl

### When stopped

- close the lane formally
- document why
- return to experiment-map selection

## Recommended execution order

1. Lock baseline.
2. Open experiment map.
3. Run RI internal next-hypothesis work or Legacy internal next-hypothesis work.
4. If both families look mature or plateaued internally, open coordination.
5. Test simple coordination first:
   - Legacy primary plus RI veto
   - RI primary plus Legacy veto
6. If promising, open router program.
7. Only then consider comparison.
8. Only then consider readiness.
9. Only then consider promotion.

## Primary strategic rule

Do not try to make Legacy and RI one family again.

If they are to play together, they must do so through:

- coordination
- routing
- orchestration
- explicit external decision layers

not through mixed internal surfaces.

## Expected final outcomes

This roadmap should determine one of the following:

1. RI internal research produces a new valid uplift.
2. Legacy internal research produces a new valid uplift.
3. A coordination or router layer outperforms standalone families.
4. No family-combination benefit exists and the families should remain independent.
5. A later comparison, readiness, or promotion path becomes justified for exactly one artifact.

Until then:

- no champion cutover
- no readiness shortcut
- no promotion shortcut
- no live or runtime default mutation
