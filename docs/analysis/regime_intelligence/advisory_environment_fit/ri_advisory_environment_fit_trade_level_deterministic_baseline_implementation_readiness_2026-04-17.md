# RI advisory environment-fit — trade-level deterministic baseline implementation readiness

This memo is docs-only and fail-closed.
It decides whether the first bounded implementation slice for the new RI trade-level deterministic baseline may open, and if so under what exact research-only constraints.

Governance packet: `docs/decisions/regime_intelligence/advisory_environment_fit/ri_advisory_environment_fit_trade_level_deterministic_baseline_implementation_readiness_packet_2026-04-17.md`

## Source surface used

- `plan/ri_advisory_environment_fit_roadmap_2026-04-16.md`
- `docs/analysis/regime_intelligence/advisory_environment_fit/ri_advisory_environment_fit_phase2_label_taxonomy_2026-04-16.md`
- `docs/analysis/regime_intelligence/advisory_environment_fit/ri_advisory_environment_fit_phase3_direct_baseline_admissibility_2026-04-16.md`
- `docs/analysis/regime_intelligence/advisory_environment_fit/ri_advisory_environment_fit_phase3_post_capture_v2_baseline_admissibility_2026-04-17.md`
- `docs/analysis/regime_intelligence/advisory_environment_fit/ri_advisory_environment_fit_trade_level_authority_admissibility_2026-04-17.md`
- `docs/analysis/regime_intelligence/advisory_environment_fit/ri_advisory_environment_fit_trade_level_label_mapping_contract_2026-04-17.md`
- `docs/analysis/regime_intelligence/advisory_environment_fit/ri_advisory_environment_fit_trade_level_evidence_family_leakage_boundary_2026-04-17.md`
- `docs/analysis/regime_intelligence/advisory_environment_fit/ri_advisory_environment_fit_trade_level_deterministic_baseline_admissibility_2026-04-17.md`
- `docs/analysis/regime_intelligence/advisory_environment_fit/ri_advisory_environment_fit_trade_level_deterministic_baseline_definition_2026-04-17.md`
- `docs/decisions/regime_intelligence/advisory_environment_fit/ri_advisory_environment_fit_trade_level_authority_admissibility_packet_2026-04-17.md`
- `docs/decisions/regime_intelligence/advisory_environment_fit/ri_advisory_environment_fit_trade_level_label_mapping_contract_packet_2026-04-17.md`
- `docs/decisions/regime_intelligence/advisory_environment_fit/ri_advisory_environment_fit_trade_level_evidence_family_leakage_boundary_packet_2026-04-17.md`
- `docs/decisions/regime_intelligence/advisory_environment_fit/ri_advisory_environment_fit_trade_level_deterministic_baseline_admissibility_packet_2026-04-17.md`
- `docs/decisions/regime_intelligence/advisory_environment_fit/ri_advisory_environment_fit_trade_level_deterministic_baseline_definition_packet_2026-04-17.md`

## Decision question

After fixing the trade-level authority lane, the label/mapping contract, the evidence-family boundary, the deterministic baseline admissibility, and the deterministic baseline definition, may the lane now open one first implementation slice?

## Short answer

**Yes — but only as a bounded research-only materialization slice below runtime, below ML, and below any promotion or Phase 4 semantics.**

That means:

- the first implementation slice may materialize the predicate layer
- the first implementation slice may materialize the entry-row band layer
- the first implementation slice may emit trade labels, row mappings, and required reports
- the first implementation slice may not touch runtime code, runtime config, family authority, or ML surfaces

So readiness is affirmed only for a very small implementation box.
Not for deployment.
Not for runtime.
And definitely not for “problem solved, ship it” theater.

## Why implementation-readiness is now admissible

### 1. The baseline semantics are already defined enough to prevent implementation drift

The earlier slices already fixed the parts that usually make first implementations dangerous:

- the authority surface is trade-level, not row-level
- the scoring-time surface remains the entry row
- admissible trade labels are already bounded
- admissible row outputs are already bounded
- leakage boundaries are already explicit
- reporting duties are already explicit
- fail-closed conditions are already explicit

That means the first implementation slice no longer needs to invent meaning.
It only needs to materialize already-governed meaning.

### 2. The trade-side implementation target is narrow enough

The definition slice already fixed the trade-side target to:

- one predicate layer
- one deterministic trade-label rule order
- four trade-level outputs only

That is materially smaller than “implement the RI advisory program.”
It is one bounded materialization problem:

- coverage / evaluability predicate
- net realized outcome direction predicate
- path-quality predicate
- instability predicate
- deterministic gate order over those predicates

Because the target is that narrow, the first implementation slice can remain a research artifact-materialization step rather than drifting into strategy semantics or runtime authoring.

### 3. The row-side implementation target is also narrow enough

The definition slice also fixed the row-side target to:

- four input bands
- five bounded outputs
- one deterministic rule order
- one explicit coverage gate before interpretation

That means the first implementation slice does not need to discover a new mapping language.
It needs only to materialize:

- `clarity_band`
- `transition_proximity_band`
- `confidence_band`
- `context_support_band`
- `coverage_state`
- bounded likelihood outputs
- `authority_strength`

That is still a bounded research problem.
It is not runtime scoring.

### 4. The slice can stay fully below runtime and ML surfaces

Nothing in the definition requires the first implementation slice to touch:

- `src/**`
- `config/**`
- runtime loaders
- runtime APIs
- champion files
- ML training or comparison logic

The first implementation slice can therefore stay in a research-only envelope such as:

- one bounded script under `tmp/`
- one result directory under `results/research/ri_advisory_environment_fit/`
- one closeout memo under `docs/analysis/`

That is the key readiness fact.
The lane can now be implemented in miniature without crossing into runtime-authority territory.

## What the first implementation slice may do

The first implementation slice may do only the following:

### 1. Materialize the trade-side predicate layer

It may compute bounded trade-level predicates from already admitted realized-trade evidence families only:

- coverage / evaluability
- net realized outcome direction
- path quality
- instability

It may then apply the already-defined gate order to emit only:

- `supportive_trade_outcome`
- `hostile_trade_outcome`
- `transition_trade_outcome`
- `non_evaluable_trade_context`

### 2. Materialize the row-side band layer

It may compute only the already-defined entry-time bands from already admitted entry-time field families only:

- `clarity_band`
- `transition_proximity_band`
- `confidence_band`
- `context_support_band`

Those bands must be derived only from entry-time inputs already admitted by the boundary slice.

### 3. Materialize the bounded row outputs

It may then emit only the already-defined bounded row outputs:

- `supportive_context_likelihood`
- `hostile_context_likelihood`
- `transition_risk_likelihood`
- `authority_strength`
- `coverage_state`

### 4. Emit reporting and fail-closed artifacts

It may emit only the reporting surface already required by the definition slice, including:

- trade-label counts by year
- row coverage-state counts by year
- row likelihood-band counts by year
- authority-strength distribution by year
- unsupported / non-evaluable counts by year
- `transition_trade_outcome` share by year
- explicit `2024` versus `2025` comparison
- contradiction-year warnings
- weak-authority warnings
- label-imbalance warnings

## What the first implementation slice must not do

### 1. No runtime-authority contact

The first implementation slice must not touch:

- `src/**`
- `config/**`
- runtime configuration authority
- champion or candidate writeback surfaces
- API or backtest runtime entrypoints as new production consumers

The point is to materialize the baseline on research surfaces only.

### 2. No ML contact

The first implementation slice must not open:

- ML comparison
- model fitting
- learned thresholds
- classifier replacement
- probability-model reinterpretation

The deterministic baseline must exist as a research artifact before any ML comparator is even discussable.

### 3. No row-level authority inflation

The first implementation slice must not describe its row outputs as:

- restored exact Phase-2-faithful labels
- row-level ground truth
- repaired exact authority

Those claims remain forbidden.

### 4. No leakage relaxation

The first implementation slice must not import any post-entry evidence into row-side bands or row mappings, including:

- `total_pnl`
- `pnl_delta`
- `mfe_16_atr`
- `mae_16_atr`
- `fwd_*`
- `continuation_score`
- future cohort membership

If any of that becomes necessary, the slice is not ready.
It is blocked.

## Exact artifact set the first implementation slice must emit

If a later implementation slice opens, it must emit a bounded artifact set that proves both materialization and restraint.
At minimum:

### 1. Predicate artifact

One artifact must record the materialized trade-side predicates by year and by trade identifier, including:

- coverage / evaluability predicate state
- net realized outcome direction predicate state
- path-quality predicate state
- instability predicate state

### 2. Trade-label surface artifact

One artifact must record the emitted trade labels and their gate path, including:

- final trade label
- gate that fired
- contradiction or fallback cases

### 3. Row-band surface artifact

One artifact must record the materialized entry-time bands for each scored row, including:

- `clarity_band`
- `transition_proximity_band`
- `confidence_band`
- `context_support_band`

### 4. Row-mapping surface artifact

One artifact must record the bounded row outputs, including:

- `coverage_state`
- `supportive_context_likelihood`
- `hostile_context_likelihood`
- `transition_risk_likelihood`
- `authority_strength`

### 5. Summary / warning artifact

One artifact must aggregate the required yearly summaries and warnings, including:

- coverage counts
- weak-authority counts
- label-imbalance counts
- contradiction-year deltas

### 6. Boundary manifest

One manifest must state explicitly that:

- runtime integration = false
- ML opening = false
- Phase 4 opening = false
- exact row-level authority recovery = false
- post-entry row-mapping leakage = false

### 7. Deterministic replay proof

The implementation slice must execute an identical-input replay and emit stable summary/hash proof for at minimum:

- predicate artifact
- trade-label artifact
- row-mapping artifact
- summary artifact

Without replay stability, the first implementation slice is not ready to be interpreted.

## Required stop conditions for the first implementation slice

If a later implementation slice opens, it must stop immediately on any of the following:

### 1. Predicate-authority drift

If the trade-side predicate layer cannot be materialized from the already admitted realized-trade evidence families without inventing a new authority surface, stop.

### 2. Banding leakage drift

If the row-side band layer cannot be materialized from already admitted entry-time families only, stop.

### 3. Coverage-collapse failure

If unsupported plus non-evaluable states dominate so strongly that the resulting baseline surface becomes mostly uninformative, stop or report that failure plainly.

### 4. Weak-authority dominance

If most evaluable rows remain weakly anchored and the slice tries to hide that with averages or flattened summaries, stop.

### 5. Contradiction-year inversion

If `2025` materially inverts or collapses the baseline story, that must remain explicit in the outputs rather than being treated as a minor note.

### 6. Runtime-contact breach

If the slice needs runtime code, runtime config, or family-authority mutation to proceed, stop.
The whole point of readiness here is that the first implementation can remain below those surfaces.

## Readiness verdict

The honest verdict is:

- **implementation-readiness is affirmed for one bounded research-only materialization slice**

But only under this exact reading:

- research-only
- artifact-only
- deterministic replay required
- leakage still fail-closed
- unsupported coverage still visible
- weak authority still visible
- `2025` still mandatory
- runtime still untouched
- ML still unopened

That is enough to open one tiny implementation box.
Not a platform.
Just a box.

## Exact next admissible step

The next admissible move after this readiness decision is:

- **one bounded trade-level deterministic baseline implementation slice on research surfaces only**

That slice should stay scoped to:

1. one bounded script under `tmp/`
2. one results directory under `results/research/ri_advisory_environment_fit/`
3. one closeout memo under `docs/analysis/`
4. deterministic replay proof
5. explicit fail-closed warnings rather than runtime-facing conclusions

## Bottom line

The new lane is now ready for its first tiny implementation step.

But only in the strictest possible sense:

- **predicate layer:** ready to materialize
- **row-band layer:** ready to materialize
- **bounded baseline outputs:** ready to materialize
- **runtime / ML / Phase 4 / restored exact row-level authority:** still closed

So the honest new state is:

- **trade-level deterministic baseline: implementation-ready in one bounded research-only slice**
- **old exact row-level authority problem: still closed**
- **next step: bounded research implementation, not runtime implementation**
