# RI advisory environment-fit — Phase 3 carrier-materialization admissibility

This memo is docs-only and fail-closed.
It decides whether the roadmap may open a separate bounded implementation slice whose only job would be to materialize one clarity-on RI optimizer artifact into a fixed research carrier.

Governance packet: `docs/governance/ri_advisory_environment_fit_phase3_carrier_materialization_admissibility_packet_2026-04-16.md`

## Source surface used

This memo uses only already tracked adequacy notes, the current fixed carrier, and the strongest clarity-on RI donor artifacts:

- `docs/analysis/ri_advisory_environment_fit_phase3_carrier_adequacy_2026-04-16.md`
- `config/strategy/candidates/3h/tBTCUSD_3h_slice8_runtime_bridge_20260326.json`
- `config/optimizer/3h/phased_v3/best_trials/phaseC_oos_trial.json`
- `config/optimizer/3h/phased_v3/best_trials/phaseB_v2_best_trial.json`
- `config/optimizer/3h/phased_v3/PHASED_V3_RESULTS.md`
- `docs/analysis/regime_intelligence_phase_bc_rerun_plan_2026-03-13.md`

## Decision question

May the roadmap open a separate implementation slice that materializes `phaseC_oos_trial.json` into a fixed RI research carrier before attempting capture v2?

## Short answer

**Yes — narrowly, and only as a separate materialization slice with explicit invariants.**

The repository does not yet have the desired carrier.
But it now has enough evidence to justify a bounded slice whose job is to create one, as long as that slice remains strictly about carrier materialization rather than score authoring or capture.

## Why `phaseC_oos_trial.json` is the right donor candidate

### 1. It is RI-aligned on the dimensions this lane needs

`phaseC_oos_trial.json` is the strongest in-repo donor because it is already:

- RI-family aligned
- `authority_mode = regime_module`
- `clarity_score.enabled = true`
- based on corrected post-fix RI evidence
- explicitly treated in repo documentation as the corrected OOS artifact for the corrected RI path

This makes it materially stronger than:

- the current slice8 runtime bridge, which is fixed but clarity-off
- temporary observational clarity files in `tmp/`
- purely in-sample-only RI artifacts

### 2. It is still only a donor, not a carrier

Despite that strength, `phaseC_oos_trial.json` is still not a ready carrier because:

- it lives under `config/optimizer/.../best_trials/`
- it remains framed as an optimizer / OOS artifact
- it points to trial-local materialization metadata such as `config_path = trial_001_config.json`
- it has not yet been repackaged as a fixed candidate surface with explicit research-carrier semantics

So the lane still cannot jump directly to capture.
What it can do is open a narrower slice whose only purpose is to make that carrier/non-carrier distinction explicit and safe.

## Why a materialization slice is now admissible

### 3. The blocker has become concrete rather than speculative

The previous slices already established:

- the current fixed carrier is too thin
- a richer clarity-on donor exists
- the donor is not yet in the right carrier class

That means the next question is no longer vague.
It is now precise and testable:

> can one fixed research carrier be created from one identified RI donor artifact without changing runtime behavior or silently reinterpreting artifact semantics?

That is exactly the kind of bounded implementation question a separate slice can answer.

### 4. The slice can be tightly constrained

A future materialization slice can remain small and governance-clean if it obeys all of the following:

1. **one donor only**
   - donor must be `config/optimizer/3h/phased_v3/best_trials/phaseC_oos_trial.json`
2. **no parameter invention**
   - no hand tuning, no threshold edits, no weight edits, no semantic reinterpretation
3. **metadata preservation**
   - preserve provenance to donor artifact, runtime version, and donor identity
4. **candidate semantics must be explicit**
   - resulting file must be framed as backtest-only research carrier, not champion, not promotion evidence
5. **no runtime/default mutation**
   - materialization must create a new fixed carrier artifact only; it must not change `src/**`, tests, or active runtime config
6. **no capture in the same slice**
   - materialization and capture must remain separate slices

If those invariants cannot be maintained, the slice should not open.

## What the future materialization slice would need to decide

A later implementation slice would need to answer only the following:

- where the new fixed carrier belongs
- how to translate donor structure into fixed carrier structure without semantic drift
- how provenance is recorded
- how to prove the created carrier is still RI-only and backtest-only

It should **not** also try to:

- run capture v2
- score the resulting carrier
- compare baseline outcomes
- argue that the advisory lane is now validated

## Admissibility decision

The next implementation step is admissible as:

- **one bounded carrier-materialization slice centered on `phaseC_oos_trial.json`**

But this is only admissible under a strict fail-closed reading:

- materialize first
- validate that the result is truly a fixed research carrier
- only then consider a separate capture-v2 slice

## What should not happen next

- no direct capture on raw `phaseC_oos_trial.json`
- no direct baseline authoring from donor artifacts
- no bundling of materialization and capture into one slice
- no implicit claim that `runtime_version` alone makes the donor a ready carrier

## Fallback if invariants cannot be met

If the carrier cannot be materialized cleanly under the invariants above, the correct fallback remains:

- **lane close**

That would mean the lane found a promising donor but not an admissible bridge from donor artifact to fixed carrier.

## Bottom line

The roadmap still cannot open deterministic baseline work.
But it now **can** open one more carefully bounded step:

- **a separate carrier-materialization implementation slice**

So the honest forward path is now:

1. materialize `phaseC_oos_trial.json` into a fixed RI research carrier under strict invariants
2. then reassess whether capture v2 is admissible on that carrier
3. only after that revisit baseline opening

That is the smallest next step that actually moves the lane forward without cheating the evidence.
